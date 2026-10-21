"""Exercise hardware tutorial control flow only through the software device rig."""

import json
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from thorlabs_shutter_control import ShutterError
from thorlabs_shutter_control import controller as driver

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "examples"


@pytest.mark.parametrize(
    "scenario",
    ["cycle", "passive", "wrong_route", "wrong_identity", "open_error", "interrupt", "no_hold"],
)
def test_lan_notebook_routes_and_cleans_up(rig, monkeypatch, scenario):
    """Execute the saved lesson against TCPIP metadata with no real SDK/network."""
    rig.controller.discover()
    manager = rig.controller._sdk.manager
    entries = []
    monkeypatch.setattr(manager, "CreateManualDeviceEntry", entries.append, raising=False)
    monkeypatch.setattr(
        manager,
        "GetTransportInfo",
        lambda serial: SimpleNamespace(
            GetProvider=lambda: "TCPIP",
            GetComSpec=lambda: (
                "192.0.2.10:40305" if scenario == "wrong_route" else "192.0.2.10:40304"
            ),
        ),
        raising=False,
    )
    connect = rig.device.Connect

    def lan_connect(serial):
        connect(serial)
        rig.device.USBConnected = "Disconnected"

    monkeypatch.setattr(rig.device, "Connect", lan_connect)
    if scenario == "wrong_identity":
        monkeypatch.setattr(
            rig.device, "GetDeviceInfo", lambda: SimpleNamespace(SerialNumberText="68000002")
        )
    if scenario == "open_error":
        setter = rig.device.SetOperatingState

        def fail_open(state):
            setter(state)
            if state == "Active":
                raise RuntimeError("LAN Open failed after write")

        monkeypatch.setattr(rig.device, "SetOperatingState", fail_open)

    def hold(seconds):
        assert seconds == 0.1
        if scenario == "interrupt":
            raise KeyboardInterrupt("LAN hold interrupted")

    notebook = json.loads((EXAMPLES / "shutter_lan_tutorial.ipynb").read_text(encoding="utf-8"))
    assert all(not c.get("outputs") and c.get("execution_count") is None for c in notebook["cells"])
    cells = {c["id"]: "".join(c["source"]) for c in notebook["cells"] if c["cell_type"] == "code"}
    namespace = {}
    exec(compile(cells["settings"], "settings", "exec"), namespace)
    namespace.update(HUB_IP="192.0.2.10", CUBE_SERIAL=68000001, sleep=hold)
    namespace["HOLD_SECONDS"] = None if scenario == "no_hold" else 0.1

    def run():
        for name, source in cells.items():
            if name == "settings" or (scenario == "passive" and name in {"prepare", "cycle"}):
                continue
            exec(compile(source, name, "exec"), namespace)
            if name == "connect":
                # Setup cannot replace an owned connection with a fresh object.
                original = namespace["hub"]
                with pytest.raises(RuntimeError, match="Disconnect the existing"):
                    exec(compile(cells["construct"], "construct", "exec"), namespace)
                assert namespace["hub"] is original

    if scenario in {"cycle", "passive"}:
        run()
    else:
        error = {
            "wrong_route": RuntimeError,
            "wrong_identity": ShutterError,
            "open_error": ShutterError,
            "interrupt": KeyboardInterrupt,
            "no_hold": ValueError,
        }[scenario]
        with pytest.raises(error):
            run()
    assert entries and set(entries) == {"192.0.2.10:40304"}
    assert not rig.device.IsConnected
    if scenario in {"cycle", "open_error", "interrupt"}:
        assert rig.device.state == "Closed"
        assert ("set_state", "Active") in rig.device.calls
    else:
        assert not any(c[0] in {"enable", "set_state", "set_mode"} for c in rig.device.calls)


@pytest.mark.parametrize(
    "scenario",
    [
        "success",
        "failed_open",
        "hold_interrupt",
        "wrong_identity",
        "invalid_hold",
    ],
)
def test_notebook_uses_explicit_reads_and_preserves_cleanup(rig, monkeypatch, capsys, scenario):
    notebook = json.loads(
        (EXAMPLES / "shutter_open_close_tutorial.ipynb").read_text(encoding="utf-8")
    )
    assert all(not c.get("outputs") and c.get("execution_count") is None for c in notebook["cells"])
    cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
    monkeypatch.setattr(time, "perf_counter", driver.time.monotonic)

    if scenario == "success":
        rig.device.mode = "Triggered"
        rig.device.operation = "Active"
        enable = rig.device.EnableDevice

        def enable_after_inactive():
            assert rig.device.operation == "Inactive" and rig.device.mode == "Manual"
            enable()

        monkeypatch.setattr(rig.device, "EnableDevice", enable_after_inactive)

    def sleep(seconds):
        if scenario == "hold_interrupt" and seconds == 1.0:
            raise KeyboardInterrupt("hold interrupted")
        driver.time.sleep(seconds)

    monkeypatch.setattr(time, "sleep", sleep)
    namespace = {}
    exec(compile("".join(cells[0]["source"]), "settings", "exec"), namespace)
    namespace["SERIAL"] = 68000001
    namespace["HOLD_SECONDS"] = 0 if scenario == "invalid_hold" else 1.0
    if scenario == "wrong_identity":
        monkeypatch.setattr(
            rig.device, "GetDeviceInfo", lambda: SimpleNamespace(SerialNumberText="68000002")
        )
    if scenario == "failed_open":
        original = rig.device.SetOperatingState

        def set_state(state):
            original(state)
            if state == "Active":
                raise RuntimeError("Open failed after write")

        monkeypatch.setattr(rig.device, "SetOperatingState", set_state)

    def run_steps():
        for cell in cells[1:]:
            exec(compile("".join(cell["source"]), cell["id"], "exec"), namespace)

    if scenario == "success":
        run_steps()
        output = capsys.readouterr().out
        assert "Open: open (0.000 s API call)" in output
        assert "Close: closed (0.000 s API call)" in output
    else:
        expected = {
            "failed_open": ShutterError,
            "hold_interrupt": KeyboardInterrupt,
            "wrong_identity": ShutterError,
            "invalid_hold": ValueError,
        }[scenario]
        with pytest.raises(expected):
            run_steps()
    assert not rig.device.IsConnected
    if scenario in (
        "success",
        "failed_open",
        "hold_interrupt",
    ):
        assert rig.device.state == "Closed"
        assert rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]
    else:
        assert not any(call[0] in {"enable", "set_state", "set_mode"} for call in rig.device.calls)
