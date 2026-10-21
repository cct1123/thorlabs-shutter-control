import sys
from pathlib import Path

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


@pytest.mark.parametrize("serials", [["68000003", "68000001", "68000002"]])
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
    monkeypatch.setattr(cli.config, "SERIAL_NUMBERS", serials)
    assert cli.main() == 0
    assert inspected == [True]
    assert rig.manager_calls == []
    assert all(device.calls == [] for device in rig.devices.values())


@pytest.mark.parametrize(
    "settings",
    [
        {"SERIAL_NUMBERS": ("68000001", "68000001")},
        {"SERIAL_NUMBERS": ("68000001", 68000001)},
        {"SLOTS": 1, "SERIAL_NUMBERS": ("68000001", "68000002")},
        {"SERIAL_NUMBERS": ("invalid",)},
        {"PORT": 0},
        {"PORT": 65536},
        {"PORT": True},
        {"PORT": "8050"},
        {"SLOTS": 0},
        {"SLOTS": -1},
        {"SLOTS": 1.5},
    ],
)
def test_invalid_project_config_is_rejected_before_sdk_or_server_access(
    rig, monkeypatch, capsys, settings
):
    def forbidden(*args, **kwargs):
        pytest.fail("Invalid project config must not access SDK or start the server.")

    for key, value in settings.items():
        monkeypatch.setattr(cli.config, key, value)
    monkeypatch.setattr(module, "_load_sdk", forbidden)
    monkeypatch.setattr(gui.Dash, "run", forbidden)
    assert cli.main() == 1
    assert "Invalid project config" in capsys.readouterr().err
    assert rig.manager_calls == []
    assert all(device.calls == [] for device in rig.devices.values())


def test_sdk_path_comes_from_project_config_not_environment(monkeypatch):
    tmp_path = Path("tmp/nonexistent-sdk-path-test")
    monkeypatch.setattr(module, "_loaded_sdk", None)
    monkeypatch.setattr(module.sys, "platform", "win32")
    monkeypatch.setattr(cli.config, "KINESIS_DIR", str(tmp_path / "project-sdk"))
    monkeypatch.setenv("KINESIS_DIR", str(tmp_path / "environment-sdk"))
    with pytest.raises(module.ShutterError, match="project-sdk"):
        module._load_sdk(None)
    with pytest.raises(module.ShutterError, match="explicit-sdk"):
        module._load_sdk(tmp_path / "explicit-sdk")


@pytest.mark.parametrize(
    "interruption,shutdown_failure", [(RuntimeError, True), (KeyboardInterrupt, False)]
)
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
