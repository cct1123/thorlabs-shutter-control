"""Exercise hardware tutorial control flow only through the software device rig."""

import json
import runpy
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from thorlabs_shutter_control import ShutterError
from thorlabs_shutter_control import controller as driver

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "examples"


SCRIPTS = sorted(path.name for path in EXAMPLES.glob("*.py"))


@pytest.mark.parametrize(
    "scenario",
    [
        "success",
        "failed_open",
        "hold_interrupt",
        "wrong_identity",
        "invalid_hold",
        "repeat_success",
        "repeat_interrupt",
        "invalid_repeat",
    ],
)
def test_notebook_uses_explicit_reads_and_preserves_cleanup(rig, monkeypatch, capsys, scenario):
    def forbidden_interlock_gate(_):
        pytest.fail("Interlock metadata must not gate project operations")

    monkeypatch.setattr(driver.ShutterStatus, "interlock_ready", property(forbidden_interlock_gate))
    notebook = json.loads(
        (EXAMPLES / "shutter_open_close_tutorial.ipynb").read_text(encoding="utf-8")
    )
    cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
    # Exercise source with the fake SDK; saved lab outputs are not a runtime contract.
    monkeypatch.setattr(time, "perf_counter", driver.time.monotonic)

    repeat_waits = []

    def sleep(seconds):
        if scenario == "hold_interrupt" and seconds == 1.0:
            raise KeyboardInterrupt("hold interrupted")
        if seconds == 0.04:
            repeat_waits.append(seconds)
            if scenario == "repeat_interrupt" and len(repeat_waits) == 3:
                raise KeyboardInterrupt("repeat interrupted")
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
            if cell["id"] == "repeat-settings":
                namespace["RUN_REPEAT"] = scenario in {
                    "repeat_success",
                    "repeat_interrupt",
                    "invalid_repeat",
                }
                namespace["REPEAT_COUNT"] = 3 if scenario != "invalid_repeat" else 0
                namespace["REPEAT_HOLD_SECONDS"] = 0.04

    if scenario in {"success", "repeat_success"}:
        run_steps()
        output = capsys.readouterr().out
        assert "Open: open (0.000 s API call)" in output
        assert "Close: closed (0.000 s API call)" in output
        if scenario == "repeat_success":
            assert "Cycle 3/3" in output
            assert repeat_waits == [0.04] * 6
    else:
        expected = {
            "failed_open": ShutterError,
            "hold_interrupt": KeyboardInterrupt,
            "wrong_identity": ShutterError,
            "invalid_hold": ValueError,
            "repeat_interrupt": KeyboardInterrupt,
            "invalid_repeat": ValueError,
        }[scenario]
        with pytest.raises(expected):
            run_steps()
    assert not rig.device.IsConnected
    if scenario in (
        "success",
        "failed_open",
        "hold_interrupt",
        "repeat_success",
        "repeat_interrupt",
        "invalid_repeat",
    ):
        assert rig.device.state == "Closed"
        assert rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]
    else:
        assert not any(call[0] in {"enable", "set_state", "set_mode"} for call in rig.device.calls)


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


@pytest.mark.parametrize("duration", ["nan"])
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


@pytest.mark.parametrize(
    "script,flag",
    [
        ("03_open_close.py", "--open-seconds"),
        ("04_three_shutters.py", "--open-seconds"),
        ("05_ttl_control.py", "--armed-seconds"),
    ],
)
def test_tutorial_invalid_hold_rejected_before_sdk(rig, monkeypatch, script, flag):
    serials = list(rig.devices) if script.startswith("04") else ["68000001"]
    main, _ = tutorial(script, monkeypatch, *serials, flag, "0")
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
