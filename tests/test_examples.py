"""Exercise hardware tutorial control flow only through the software device rig."""

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from thorlabs_shutter_control import ShutterError

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "examples"
SCRIPTS = sorted(path.name for path in EXAMPLES.glob("*.py"))


def tutorial(name, monkeypatch, *arguments):
    namespace = runpy.run_path(str(EXAMPLES / name))
    main = namespace["main"]
    monkeypatch.setattr(sys, "argv", [name, *arguments])
    waits = []
    if "sleep" in main.__globals__:
        monkeypatch.setitem(main.__globals__, "sleep", waits.append)
    return main, waits


@pytest.mark.parametrize("script", SCRIPTS)
def test_tutorial_import_is_passive(rig, script):
    runpy.run_path(str(EXAMPLES / script))
    assert not rig.manager_calls and all(not d.calls for d in rig.devices.values())


@pytest.mark.parametrize("script", SCRIPTS)
def test_tutorial_help_does_not_access_hardware(rig, monkeypatch, script, capsys):
    main, _ = tutorial(script, monkeypatch, "--help")
    with pytest.raises(SystemExit) as caught:
        main()
    assert caught.value.code == 0
    assert "usage:" in capsys.readouterr().out
    assert not rig.manager_calls and all(not d.calls for d in rig.devices.values())


@pytest.mark.parametrize("empty", [False, True])
def test_discovery_lesson_never_connects_or_writes_output(rig, monkeypatch, empty, capsys):
    if empty:
        rig.serials.clear()
    main, _ = tutorial("01_discover.py", monkeypatch)
    main()
    output = capsys.readouterr().out
    assert ("No KSC101 found" if empty else "68000001") in output
    assert rig.manager_calls == ["discover"]
    assert all(not d.calls for d in rig.devices.values())


def test_status_lesson_releases_without_changing_output_or_mode(rig, monkeypatch):
    rig.device.mode = "Triggered"
    rig.device.operation = "Active"
    rig.device.inputs[0] = True
    main, _ = tutorial("02_connect_and_read_status.py", monkeypatch, "68000001")
    main()
    assert rig.device.mode == "Triggered" and rig.device.operation == "Active"
    assert rig.device.state == "Open" and not rig.device.IsConnected
    assert not any(
        c[0] in {"set_mode", "set_state", "enable", "set_triggers"} for c in rig.device.calls
    )
    assert rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]


def test_manual_lesson_closes_and_releases_after_wait(rig, monkeypatch):
    main, waits = tutorial("03_open_close.py", monkeypatch, "68000001", "--open-seconds", "0.1")
    main()
    assert waits == [0.1]
    assert ("set_state", "Active") in rig.device.calls
    assert rig.device.state == "Closed" and rig.device.mode == "Manual"
    assert rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]


def test_three_shutter_lesson_never_opens_two_at_once_and_releases_all(rig, monkeypatch):
    rig.serials[:] = list(rig.devices)
    for device in rig.devices.values():
        setter = device.SetOperatingState

        def set_state(state, original=setter):
            if state == "Active":
                assert all(d.state == "Closed" for d in rig.devices.values())
            original(state)

        monkeypatch.setattr(device, "SetOperatingState", set_state)
    main, waits = tutorial(
        "04_three_shutters.py", monkeypatch, *rig.serials, "--open-seconds", "0.1"
    )
    main()
    assert waits == [0.1] * 3
    for device in rig.devices.values():
        assert ("set_state", "Active") in device.calls
        assert device.mode == "Manual" and device.state == "Closed"
        assert not device.IsConnected


def test_ttl_lesson_configures_readbacks_arms_and_disarms(rig, monkeypatch):
    main, _ = tutorial("05_ttl_control.py", monkeypatch, "68000001", "--armed-seconds", "0.1")
    snapshots = []

    def observe_wait(seconds):
        snapshots.append((seconds, rig.device.mode, rig.device.operation, rig.device.state))

    monkeypatch.setitem(main.__globals__, "sleep", observe_wait)
    main()
    assert snapshots == [(0.1, "Triggered", "Active", "Closed")]
    config = rig.device.trigger_config
    assert (config.Trigger1Mode, config.Trigger1Polarity) == ("TrigIN_GPI", "TriggerHigh")
    assert (config.Trigger2Mode, config.Trigger2Polarity) == ("Disabled", "TriggerHigh")
    assert rig.device.mode == "Manual" and rig.device.operation == "Inactive"
    assert not rig.device.IsConnected


@pytest.mark.parametrize("duration", ["0", "-1", "nan", "inf"])
@pytest.mark.parametrize(
    "script,flag",
    [
        ("03_open_close.py", "--open-seconds"),
        ("04_three_shutters.py", "--open-seconds"),
        ("05_ttl_control.py", "--armed-seconds"),
    ],
)
def test_bad_dwell_is_rejected_before_sdk_access(rig, monkeypatch, script, flag, duration):
    serials = list(rig.devices) if script.startswith("04") else ["68000001"]
    main, _ = tutorial(script, monkeypatch, *serials, flag, duration)
    with pytest.raises(SystemExit) as caught:
        main()
    assert caught.value.code == 2
    assert not rig.manager_calls and all(not d.calls for d in rig.devices.values())


@pytest.mark.parametrize("three", [False, True])
def test_actuation_error_still_releases_every_connected_handle(rig, monkeypatch, three):
    if three:
        rig.serials[:] = list(rig.devices)
    device = rig.devices["68000002"] if three else rig.device
    setter = device.SetOperatingState

    def fail_after_open(state):
        setter(state)
        if state == "Active":
            raise RuntimeError("Injected tutorial Open failure")

    monkeypatch.setattr(device, "SetOperatingState", fail_after_open)
    name = "04_three_shutters.py" if three else "03_open_close.py"
    main, _ = tutorial(name, monkeypatch, *rig.serials, "--open-seconds", "0.1")
    with pytest.raises(ShutterError, match="tutorial Open failure"):
        main()
    for serial in rig.serials:
        device = rig.devices[serial]
        assert device.state == "Closed" and not device.IsConnected
        assert device.calls[-2:] == [("stop_poll",), ("disconnect",)]


def test_ttl_wait_interrupt_still_disarms_and_releases(rig, monkeypatch):
    main, _ = tutorial("05_ttl_control.py", monkeypatch, "68000001", "--armed-seconds", "0.1")

    def interrupt(seconds):
        raise KeyboardInterrupt("Tutorial interrupted")

    monkeypatch.setitem(main.__globals__, "sleep", interrupt)
    with pytest.raises(KeyboardInterrupt, match="Tutorial interrupted"):
        main()
    assert rig.device.mode == "Manual" and rig.device.operation == "Inactive"
    assert rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]


def test_duplicate_serials_are_rejected_before_sdk_access(rig, monkeypatch):
    main, _ = tutorial(
        "04_three_shutters.py",
        monkeypatch,
        "68000001",
        "68000001",
        "68000003",
        "--open-seconds",
        "0.1",
    )
    with pytest.raises(ValueError, match="distinct"):
        main()
    assert not rig.manager_calls and all(not d.calls for d in rig.devices.values())


@pytest.mark.parametrize(
    "script,flag",
    [
        ("03_open_close.py", "--open-seconds"),
        ("04_three_shutters.py", "--open-seconds"),
        ("05_ttl_control.py", "--armed-seconds"),
    ],
)
def test_tutorial_explicit_confirmation_supports_unknown_sdk_interlock(
    rig, monkeypatch, script, flag
):
    serials = list(rig.devices) if script.startswith("04") else ["68000001"]
    rig.serials[:] = serials
    for serial in serials:
        rig.devices[serial].interlock = False
    confirmations = [value for serial in serials for value in ("--verified-interlock", serial)]
    main, _ = tutorial(script, monkeypatch, *serials, flag, "0.1", *confirmations)
    main()
    assert all(not rig.devices[s].IsConnected and rig.devices[s].state == "Closed" for s in serials)
    assert all(("set_state", "Active") in rig.devices[s].calls for s in serials)


@pytest.mark.parametrize(
    "script,flag",
    [
        ("03_open_close.py", "--open-seconds"),
        ("04_three_shutters.py", "--open-seconds"),
        ("05_ttl_control.py", "--armed-seconds"),
    ],
)
def test_tutorial_confirmation_rejects_wrong_serial_before_sdk(rig, monkeypatch, script, flag):
    serials = list(rig.devices) if script.startswith("04") else ["68000001"]
    main, _ = tutorial(
        script, monkeypatch, *serials, flag, "0.1", "--verified-interlock", "68000009"
    )
    with pytest.raises(SystemExit) as caught:
        main()
    assert caught.value.code == 2
    assert not rig.manager_calls and all(not d.calls for d in rig.devices.values())


@pytest.mark.parametrize(
    "script,flag",
    [
        ("03_open_close.py", "--open-seconds"),
        ("04_three_shutters.py", "--open-seconds"),
        ("05_ttl_control.py", "--armed-seconds"),
    ],
)
def test_failed_identity_and_release_never_close_unverified_tutorial_target(
    rig, monkeypatch, script, flag
):
    from thorlabs_shutter_control import controller as module

    serials = list(rig.devices) if script.startswith("04") else ["68000001"]
    rig.serials[:] = serials
    target = serials[1] if len(serials) == 3 else serials[0]
    device = rig.devices[target]
    monkeypatch.setattr(
        device,
        "GetDeviceInfo",
        lambda: SimpleNamespace(SerialNumberText="68000099", Description="IDENTITY MISMATCH TEST"),
    )
    device.fail.add("disconnect")
    main, _ = tutorial(script, monkeypatch, *serials, flag, "0.1")
    with pytest.raises(Exception) as caught:
        main()
    chain = []
    error = caught.value
    while error is not None:
        chain.append(str(error))
        error = error.__context__
    assert any("identity mismatch" in message for message in chain)
    assert not any(
        c[0] in {"enable", "set_state", "set_mode", "set_triggers"} for c in device.calls
    )
    device.fail.clear()
    module._device_owners[target].disconnect(close_shutter=False)
