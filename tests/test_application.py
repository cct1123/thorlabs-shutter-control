"""TEST-201 and TEST-211: passive applications and normalized owner interface."""

import json
import subprocess
import sys
from dataclasses import asdict
from types import SimpleNamespace

import pytest

from thorlabs_shutter_control import load_config
from thorlabs_shutter_control.__main__ import main
from thorlabs_shutter_control.protocol import Deadline
from thorlabs_shutter_control.transport import D2XXTransport, VCPTransport


def test_import_and_help_do_not_load_hardware_modules():
    code = """
import sys
import thorlabs_shutter_control
from thorlabs_shutter_control.__main__ import main
assert not {'clr', 'pythonnet', 'ftd2xx', 'serial', 'dash'} & set(sys.modules)
try:
    main(['--help'])
except SystemExit as e:
    assert e.code == 0
try:
    main(['discover', '--help'])
except SystemExit as e:
    assert e.code == 0
assert not {'clr', 'pythonnet', 'ftd2xx', 'serial', 'dash'} & set(sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, result.stderr
    assert "check-config" in result.stdout


def test_config_validation_is_passive_and_strict(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        "thorlabs_shutter_control.transport.open_transport",
        lambda *a: pytest.fail("Unexpected hardware access"),
    )
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "config/shutters.example.toml"
    assert main(["--config", str(path), "check-config"]) == 0
    assert json.loads(capsys.readouterr().out)[0]["policy"] is None
    bad = tmp_path / "bad.toml"
    bad.write_text(path.read_text() + "\nunknown_option = true\n")
    with pytest.raises(TypeError):
        load_config(bad)


def test_invalid_cli_pulse_does_not_connect(monkeypatch, capsys):
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "config/shutters.example.toml"
    monkeypatch.setattr(
        "thorlabs_shutter_control.ShutterHub.connect",
        lambda *a: pytest.fail("Unexpected connection"),
    )
    assert main(["--config", str(path), "--target", "shutter", "pulse", "--seconds", "nan"]) == 1
    assert "finite" in capsys.readouterr().err


@pytest.mark.parametrize("command", ["identify", "status"])
def test_cli_reads_share_owner_schema_and_release(bench, monkeypatch, capsys, command):
    from thorlabs_shutter_control import __main__ as cli

    hub, devices, _, _ = bench
    monkeypatch.setattr(cli, "load_config", lambda path: hub.configs)
    monkeypatch.setattr(cli, "ShutterHub", lambda configs: hub)
    assert cli.main(["--target", "beam", command]) == 0
    value = json.loads(capsys.readouterr().out)
    if command == "identify":
        assert value["serial_number"] == "68000001"
        assert len(devices[0].history) == 1  # Reuse the identity already verified by connect.
    else:
        assert value["identity"]["serial_number"] == "68000001"
        assert value["feedback"]["status_bits"] == 0x2000
        assert value["feedback"]["operating_state"] == "unknown"
    assert devices[0].closed and not devices[0].output_frames


def test_d2xx_contract_uses_exact_serial_no_enumeration(monkeypatch):
    calls = []

    class Device:
        def __getattr__(self, name):
            def call(*args):
                calls.append((name, args))
                if name == "write":
                    return len(args[0])
                if name == "getQueueStatus":
                    return 0
                if name == "read":
                    return b""

            return call

    def open_ex(serial, flags, *, update):
        calls.append(("openEx", (serial, flags, update)))
        return Device()

    monkeypatch.setitem(sys.modules, "ftd2xx", SimpleNamespace(openEx=open_ex))
    monkeypatch.setattr(
        "thorlabs_shutter_control.transport.dwell", lambda d, s: calls.append(("dwell", (s,)))
    )
    transport = D2XXTransport("68000001", Deadline(1))
    assert calls == [
        ("openEx", (b"68000001", 1, False)),
        ("setTimeouts", (20, 50)),
        ("setBaudRate", (115200,)),
        ("setDataCharacteristics", (8, 0, 0)),
        ("dwell", (0.05,)),
        ("purge", (3,)),
        ("dwell", (0.05,)),
        ("resetDevice", ()),
        ("setFlowControl", (256, 0, 0)),
        ("setRts", ()),
    ]
    assert transport.write(b"123456", Deadline(1)) == 6
    transport.close()


@pytest.mark.parametrize("backend", [D2XXTransport, VCPTransport])
def test_expired_connection_budget_does_not_open_native_device(backend, monkeypatch):
    from thorlabs_shutter_control.errors import DeadlineExceeded

    def forbidden(*args, **kwargs):
        pytest.fail("Expired connection opened a device")

    monkeypatch.setitem(sys.modules, "ftd2xx", SimpleNamespace(openEx=forbidden))
    monkeypatch.setitem(sys.modules, "serial", SimpleNamespace(Serial=forbidden))
    deadline = Deadline(1)
    deadline.end = 0
    with pytest.raises(DeadlineExceeded):
        backend("unused", deadline)


def test_gui_construction_is_passive(bench):
    from thorlabs_shutter_control.gui import create_app

    hub, devices, _, _ = bench
    app = create_app(hub)
    client = app.server.test_client()
    assert client.get("/_dash-layout").status_code == 200
    assert client.get("/_dash-dependencies").status_code == 200
    assert not devices
    assert "Solenoid ON" in client.get("/_dash-layout").get_data(as_text=True)


@pytest.mark.parametrize("target", [None, "unknown"])
@pytest.mark.parametrize("action", ["connect", "read", "manual", "on", "pulse", "off", "release"])
def test_gui_requires_an_exact_target_for_every_action(bench, target, action):
    from thorlabs_shutter_control.gui import create_app

    hub, devices, _, _ = bench
    hub.connect("beam")
    before = len(devices[0].history)
    client = create_app(hub).server.test_client()
    response = client.post(
        "/_dash-update-component",
        json={
            "output": "result.children",
            "outputs": {"id": "result", "property": "children"},
            "changedPropIds": [f"{action}.n_clicks"],
            "inputs": [
                {"id": key, "property": "n_clicks", "value": int(key == action)}
                for key in ("connect", "read", "manual", "on", "pulse", "off", "release")
            ],
            "state": [{"id": "target", "property": "value", "value": target}],
        },
    )
    assert response.status_code == 200
    message = response.get_json()["response"]["result"]["children"]
    assert "Select an exact configured target" in message
    assert not devices[0].closed and len(devices[0].history) == before


def test_existing_diamond_owner_surface_and_feedback_schema(bench):
    hub, _, _, _ = bench
    methods = (
        "connect",
        "identify_device",
        "get_status",
        "connection_snapshot",
        "open_shutter",
        "close_shutter",
        "set_manual_mode",
        "enable_device",
        "recover",
        "disconnect",
        "close",
        "shutdown_outputs",
        "cancel",
    )
    assert all(callable(getattr(hub, method)) for method in methods)
    hub.connect(0)
    status = asdict(hub.get_status("beam"))
    assert {
        "name",
        "channel",
        "serial_number",
        "endpoint",
        "feedback",
        "error",
        "identity_verified",
        "generation",
        "has_device",
    } <= status.keys()
    assert status["feedback_freshness"] == "response_after_request_no_transaction_id"


def test_gui_exit_preserves_original_error_and_each_cleanup(monkeypatch):
    from thorlabs_shutter_control import gui

    calls = []

    def fail_run(**kwargs):
        raise OSError("original server failure")

    def shutdown_outputs():
        calls.append("off")
        raise OSError("OFF unavailable")

    def close():
        calls.append("release")
        raise OSError("release unavailable")

    monkeypatch.setattr(gui, "create_app", lambda hub: SimpleNamespace(run=fail_run))
    hub = SimpleNamespace(shutdown_outputs=shutdown_outputs, close=close)
    with pytest.raises(OSError, match="original server") as caught:
        gui.run(hub)
    assert calls == ["off", "release"]
    assert len(caught.value.__notes__) == 2


def test_cli_gui_transfers_cleanup_ownership_once(bench, monkeypatch):
    from thorlabs_shutter_control import __main__ as cli
    from thorlabs_shutter_control import gui

    hub, devices, _, _ = bench
    releases = []
    monkeypatch.setattr(cli, "load_config", lambda path: hub.configs)
    monkeypatch.setattr(cli, "ShutterHub", lambda configs: hub)
    monkeypatch.setattr(gui, "create_app", lambda owner: SimpleNamespace(run=lambda **kw: None))
    monkeypatch.setattr(hub, "close", lambda: releases.append("release"))
    assert cli.main(["gui"]) == 0
    assert releases == ["release"] and not devices
