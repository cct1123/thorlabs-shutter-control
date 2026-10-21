import sys

import pytest

from thorlabs_shutter_control import KCubeShutter, gui
from thorlabs_shutter_control import __main__ as cli
from thorlabs_shutter_control import controller as module


def layout_components(app):
    """Inspect the served Dash layout without starting a network listener."""
    components = {}

    def visit(item):
        if isinstance(item, list):
            for child in item:
                visit(child)
        elif isinstance(item, dict):
            props = item.get("props", {})
            if "id" in props:
                components[props["id"]] = props
            visit(props.get("children"))

    response = app.server.test_client().get("/_dash-layout")
    assert response.status_code == 200
    visit(response.get_json())
    return components


@pytest.mark.parametrize("serials", [[], ["68000001"], ["68000003", "68000001", "68000002"]])
def test_gui_launch_has_three_passive_panels_with_requested_preselection(rig, monkeypatch, serials):
    inspected = []

    def forbidden_sdk_load(directory):
        pytest.fail("GUI launch and unconnected shutdown must not load the SDK.")

    def inspect_server(self, **kwargs):
        assert kwargs == {
            "host": "127.0.0.1",
            "port": 8050,
            "debug": False,
            "use_reloader": False,
            "threaded": False,
        }
        components = layout_components(self)
        for slot in range(3):
            assert components[f"serial-{slot + 1}"]["value"] == (
                serials[slot] if slot < len(serials) else None
            )
            assert components[f"connection-{slot + 1}"]["children"] == "Disconnected"
            assert components[f"open-{slot + 1}"]["disabled"] is True
        inspected.append(True)

    monkeypatch.setattr(module, "_load_sdk", forbidden_sdk_load)
    monkeypatch.setattr(gui.Dash, "run", inspect_server)
    argv = ["shutter-control"]
    for serial in serials:
        argv.extend(["--serial", serial])
    monkeypatch.setattr(sys, "argv", argv)
    assert cli.main() == 0
    assert inspected == [True]
    assert rig.manager_calls == []
    assert all(device.calls == [] for device in rig.devices.values())


@pytest.mark.parametrize(
    "arguments",
    [
        ["--serial", "68000001", "--serial", "68000001"],
        [
            "--slots",
            "3",
            "--serial",
            "68000001",
            "--serial",
            "68000002",
            "--serial",
            "68000003",
            "--serial",
            "68000004",
        ],
        ["--serial", "invalid"],
        ["--port", "0"],
        ["--port", "65536"],
    ],
    ids=["duplicate", "too-few-slots", "invalid-serial", "low-port", "high-port"],
)
def test_invalid_arguments_are_rejected_before_sdk_or_server_access(rig, monkeypatch, arguments):
    def forbidden(*args, **kwargs):
        pytest.fail("Invalid CLI arguments must not access SDK or start the server.")

    monkeypatch.setattr(module, "_load_sdk", forbidden)
    monkeypatch.setattr(gui.Dash, "run", forbidden)
    monkeypatch.setattr(sys, "argv", ["shutter-control", *arguments])
    with pytest.raises(SystemExit) as caught:
        cli.main()
    assert caught.value.code == 2
    assert rig.manager_calls == []
    assert all(device.calls == [] for device in rig.devices.values())


@pytest.mark.parametrize("serials", [[], ["68000001", "68000002", "68000003"]])
def test_list_uses_one_fake_discovery_without_connecting_or_actuating(
    rig, monkeypatch, capsys, serials
):
    rig.serials[:] = serials
    monkeypatch.setattr(sys, "argv", ["shutter-control", "--list"])
    assert cli.main() == 0
    expected = "\n".join(serials) if serials else "No KSC101 devices discovered."
    assert capsys.readouterr().out.strip() == expected
    assert rig.manager_calls == ["discover"]
    assert all(device.calls == [] for device in rig.devices.values())


def test_missing_sdk_is_an_actionable_nonzero_exit(monkeypatch, capsys):
    monkeypatch.setattr(module, "_loaded_sdk", None)
    monkeypatch.setattr(
        sys, "argv", ["shutter-control", "--list", "--kinesis-dir", "tmp/nonexistent-sdk-for-test"]
    )
    assert cli.main() == 1
    assert "Kinesis SDK not found" in capsys.readouterr().err


@pytest.mark.parametrize("interruption", [RuntimeError, KeyboardInterrupt])
@pytest.mark.parametrize("shutdown_failure", [False, True])
def test_server_exit_attempts_every_shutter_and_reports_shutdown_failures(
    rig, monkeypatch, capsys, interruption, shutdown_failure
):
    rig.serials[:] = list(rig.devices)
    controllers = [KCubeShutter(timeout=0.5) for _ in range(3)]
    supplied = iter(controllers)
    monkeypatch.setattr(module, "KCubeShutter", lambda *args, **kwargs: next(supplied))

    def interrupt_server(self, **kwargs):
        assert kwargs["debug"] is False
        assert kwargs["use_reloader"] is False
        assert kwargs["host"] == "127.0.0.1"
        assert kwargs["threaded"] is False
        for controller, serial in zip(controllers, rig.serials, strict=True):
            controller.connect(serial)
            controller.open_shutter()
        if shutdown_failure:
            rig.devices["68000001"].fail.add("set_state")
            rig.devices["68000002"].fail.add("disconnect")
        raise interruption("server failure")

    monkeypatch.setattr(gui.Dash, "run", interrupt_server)
    monkeypatch.setattr(sys, "argv", ["shutter-control"])
    if interruption is RuntimeError:
        # Preserving the server exception also preserves its nonzero process exit.
        with pytest.raises(RuntimeError, match="server failure"):
            cli.main()
    else:
        assert cli.main() == (1 if shutdown_failure else 0)

    error_output = capsys.readouterr().err
    if shutdown_failure:
        assert "Shutter 1 (68000001)" in error_output and "set_state" in error_output
        assert "Shutter 2 (68000002)" in error_output and "disconnect" in error_output
    else:
        assert error_output == ""
    for device in rig.devices.values():
        assert device.calls[-2:] == [("stop_poll",), ("disconnect",)]
    assert rig.devices["68000003"].state == "Closed"
    assert not rig.devices["68000003"].IsConnected
    if not shutdown_failure:
        assert all(device.state == "Closed" for device in rig.devices.values())
        assert all(not device.IsConnected for device in rig.devices.values())


@pytest.mark.parametrize("slots,serial_count", [(1, 0), (6, 0), (9, 2), (None, 6)])
def test_configurable_cli_layout_stays_passive(rig, monkeypatch, slots, serial_count):
    serials = [f"6800{n:04d}" for n in range(1, serial_count + 1)]
    count = max(3, serial_count) if slots is None else slots

    def inspect_server(self, **kwargs):
        components = layout_components(self)
        suffixes = [""] if count == 1 else [f"-{n}" for n in range(1, count + 1)]
        assert [components[f"serial{s}"]["value"] for s in suffixes] == (
            serials + [None] * (count - len(serials))
        )
        assert all(components[f"open{s}"]["disabled"] for s in suffixes)

    def forbidden_sdk(directory):
        pytest.fail("Configuring more panels must remain passive")

    args = ["shutter-control"]
    if slots is not None:
        args += ["--slots", str(slots)]
    for serial in serials:
        args += ["--serial", serial]
    monkeypatch.setattr(module, "_load_sdk", forbidden_sdk)
    monkeypatch.setattr(gui.Dash, "run", inspect_server)
    monkeypatch.setattr(sys, "argv", args)
    assert cli.main() == 0


@pytest.mark.parametrize("slots", ["0", "-1", "1.5"])
def test_invalid_cli_slot_counts_never_start_server(rig, monkeypatch, slots):
    def forbidden(*args, **kwargs):
        pytest.fail("Invalid panel count must not start a server/load SDK")

    monkeypatch.setattr(module, "_load_sdk", forbidden)
    monkeypatch.setattr(gui.Dash, "run", forbidden)
    monkeypatch.setattr(sys, "argv", ["shutter-control", "--slots", slots])
    with pytest.raises(SystemExit) as caught:
        cli.main()
    assert caught.value.code == 2
