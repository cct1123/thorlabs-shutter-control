"""Session-specific physical confirmation never fabricates SDK feedback."""

import sys
from dataclasses import replace

import pytest
from test_gui import invoke

from thorlabs_shutter_control import KCubeShutter, ShutterError
from thorlabs_shutter_control import __main__ as cli
from thorlabs_shutter_control.gui import create_app


def test_confirmation_is_passive_and_preserves_unknown_readback(rig):
    c = rig.controller
    c.serial_number = "68000001"
    rig.device.interlock = False
    c.confirm_interlock("68000001")
    assert not rig.device.calls and not rig.manager_calls
    s = c.connect()
    assert s.interlock_enabled is None and s.operator_interlock_confirmed
    assert s.interlock_ready
    assert not replace(s, interlock_enabled=False).interlock_ready
    assert not replace(s, connection="fault").interlock_ready
    c.open_shutter()
    assert rig.device.state == "Open"
    c.safe_shutdown()
    assert rig.device.state == "Closed" and not rig.device.IsConnected


def test_confirmation_does_not_cross_serial_or_instance(rig):
    c = rig.controller
    c.serial_number = "68000001"
    c.confirm_interlock("68000001")
    rig.device.interlock = False
    other = KCubeShutter("68000001")
    assert not other.connect().operator_interlock_confirmed
    other.disconnect(close_shutter=False)
    c.serial_number = "68000002"
    c.serial_number = "68000001"
    assert not c.connect().interlock_ready
    c.disconnect(close_shutter=False)


def test_confirmation_requires_explicit_selected_disconnected_controller(rig):
    with pytest.raises(ValueError):
        rig.controller.confirm_interlock("68000001")
    rig.controller.serial_number = "68000001"
    with pytest.raises(ValueError):
        rig.controller.confirm_interlock("68000002")
    rig.controller.connect()
    with pytest.raises(ShutterError):
        rig.controller.confirm_interlock("68000001")
    rig.controller.disconnect(close_shutter=False)


@pytest.mark.parametrize("fault", ["key", "communication"])
def test_confirmation_cannot_override_key_or_communication_failure(rig, fault):
    c = rig.controller
    c.serial_number = "68000001"
    c.confirm_interlock("68000001")
    rig.device.interlock = False
    c.connect()
    if fault == "key":
        rig.device.Status.KeyEnabled = False
    else:
        rig.device.CommsStatus = "Timeout"
    with pytest.raises(ShutterError):
        c.open_shutter()
    assert not any(call == ("set_state", "Active") for call in rig.device.calls)
    rig.device.CommsStatus = "OK"
    c.disconnect(close_shutter=False)


def test_gui_labels_confirmation_and_enables_actual_open(rig):
    c = rig.controller
    c.serial_number = "68000001"
    c.confirm_interlock("68000001")
    rig.device.interlock = False
    app = create_app(c)
    result = invoke(app, "connect", serial="68000001")
    assert result["open"]["disabled"] is False
    assert "Interlock: unknown (operator verified)" in result["safeguards"]["children"]
    assert invoke(app, "open", serial="68000001")["shutter-state"]["children"] == "Open"
    c.safe_shutdown()


def test_cli_confirmation_keeps_startup_passive(rig, monkeypatch):
    from thorlabs_shutter_control import gui

    monkeypatch.setattr(
        sys, "argv", ["shutter-control", "--serial", "68000001", "--verified-interlock", "68000001"]
    )

    def run(app, **kwargs):
        assert not rig.device.calls and not rig.manager_calls
        response = invoke(app, "connect-1", serials=["68000001", None, None])
        assert "operator verified" in response["safeguards-1"]["children"]

    monkeypatch.setattr(gui.Dash, "run", run)
    rig.device.interlock = False
    assert cli.main() == 0
    assert not rig.device.IsConnected


def test_cli_rejects_confirmation_for_unselected_serial(rig, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["shutter-control", "--verified-interlock", "68000001"])
    with pytest.raises(SystemExit) as caught:
        cli.main()
    assert caught.value.code == 2 and not rig.manager_calls and not rig.device.calls
