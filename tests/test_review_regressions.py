"""TEST-228 software-only regressions; no hardware or bench qualification."""

from dataclasses import replace
from types import SimpleNamespace

import pytest
from conftest import FakeTransport
from ui_helpers import post_callback

from thorlabs_shutter_control import CycleParameters, ShutterError, ShutterHub
from thorlabs_shutter_control.gui import create_app


def test_successful_on_invalidates_off_rest_before_external_off(config, tmp_path, monkeypatch):
    from thorlabs_shutter_control import controller

    config = replace(config, policy=replace(config.policy, min_off_s=2))
    tick = [100.0]
    monkeypatch.setattr(controller, "clock", lambda: tick[0])
    device = FakeTransport(config)
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        hub.get_status("beam")
        tick[0] = 103
        hub.open_shutter("beam")
        device.state = 2  # External OFF; no intervening status poll while ON.
        tick[0] = 103.1
        hub.get_status("beam")
        with pytest.raises(ShutterError, match="OFF/duty recovery"):
            hub.open_shutter("beam")
        assert [frame.param2 for frame in device.output_frames] == [1]


@pytest.mark.parametrize("faulted", [False, True])
def test_completed_output_does_not_actuate_a_later_readonly_connection(bench, faulted):
    hub, devices, _, _ = bench
    hub.connect("beam")
    hub.open_shutter("beam")
    hub.safe_state("beam")
    hub.disconnect("beam")
    hub.connect("beam")
    hub.get_status("beam")
    if faulted:
        devices[-1].serial = "68000002"
        with pytest.raises(ShutterError):
            hub.get_status("beam")
        with pytest.raises(ShutterError, match="Read-only fault"):
            hub.shutdown_outputs()
    else:
        hub.shutdown_outputs()
    assert not devices[-1].output_frames


def test_protected_recovery_clears_active_request_without_incidental_off(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    hub.open_shutter("beam")
    recovered = hub.recover(
        "beam", source_inhibited=True, optical_closed=True, evidence="software fixture observation"
    )
    assert recovered.requested_state is None
    assert recovered.feedback.electrical_state == "off"
    hub.shutdown_outputs()
    assert not devices[-1].output_frames


def test_cycle_settings_enforce_recorded_duty_limit_before_io(config, tmp_path):
    policy = replace(
        config.policy,
        continuous_on_allowed=False,
        max_on_s=4,
        max_duty_fraction=0.25,
        min_off_s=2,
        allow_device_settings=True,
    )
    config = replace(config, policy=policy)
    device = FakeTransport(config)
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        before = len(device.history)
        with pytest.raises(ValueError, match="duty"):
            hub.set_cycle_parameters("beam", CycleParameters(1000, 2000, 1), source_inhibited=True)
        assert len(device.history) == before


def test_cycle_settings_accept_exact_duty_boundary_without_output(config, tmp_path):
    policy = replace(
        config.policy,
        continuous_on_allowed=False,
        max_on_s=4,
        max_duty_fraction=0.25,
        min_off_s=2,
        allow_device_settings=True,
    )
    config = replace(config, policy=policy)
    device = FakeTransport(config)
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        result = hub.set_cycle_parameters(
            "beam", CycleParameters(1000, 3000, 1), source_inhibited=True
        )
        assert result.cycle_parameters == CycleParameters(1000, 3000, 1)
        assert not device.output_frames


@pytest.mark.parametrize("operation", ["mode", "settings"])
def test_configuration_write_cannot_silently_disable_interlock(config, tmp_path, operation):
    config = replace(
        config,
        policy=replace(
            config.policy,
            qualified_modes=("manual", "single"),
            allow_persistent_mode_changes=True,
            allow_device_settings=True,
        ),
    )
    device = FakeTransport(config)
    write = device.write

    def changing_write(raw, deadline):
        result = write(raw, deadline)
        if raw[:2] == (b"\xc0\x04" if operation == "mode" else b"\xc3\x04"):
            device.interlock = 2
        return result

    device.write = changing_write
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        with pytest.raises(ShutterError, match="interlock"):
            if operation == "mode":
                hub.set_operating_mode("beam", "single", source_inhibited=True)
            else:
                hub.set_cycle_parameters(
                    "beam", CycleParameters(1000, 2000, 1), source_inhibited=True
                )
        assert hub.connection_snapshot("beam").error
        assert hub._channel("beam").claim.journal.exists()


def test_mode_stop_clears_native_start_request(config, tmp_path):
    config = replace(
        config,
        policy=replace(
            config.policy,
            qualified_modes=("manual", "auto"),
            allow_persistent_mode_changes=True,
        ),
    )
    device = FakeTransport(config)
    device.mode = 3
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        hub.start("beam", source_inhibited=True)
        device.state = 2  # Native cycle's OFF interval, not proof of Inactive.
        result = hub.set_manual_mode("beam", source_inhibited=True)
        assert result.requested_state == "off"  # Mode transition explicitly sent Stop/OFF.
        assert result.feedback.operating_mode == "manual"


@pytest.mark.parametrize("connected,generation", [(False, 1), (True, 2)])
def test_settings_drafts_do_not_survive_release_or_reconnection(config, connected, generation):
    app = create_app(SimpleNamespace(configs=[config]))
    key = next(key for key in app.callback_map if "cycle-on.value" in key)
    rendered = post_callback(
        app,
        key,
        {
            "target": "beam",
            "sample": {"name": "beam", "has_device": connected, "generation": generation},
            "settings-context": {"target": "beam", "generation": 1, "stamp": "old"},
        },
        "sample.data",
    )
    assert rendered["cycle-on"]["value"] is None
    assert rendered["cycle-off"]["value"] is None
    assert rendered["cycles"]["value"] is None
    assert rendered["continuous"]["value"] == []


def test_polling_does_not_erase_same_connection_drafts(config):
    app = create_app(SimpleNamespace(configs=[config]))
    key = next(key for key in app.callback_map if "cycle-on.value" in key)
    rendered = post_callback(
        app,
        key,
        {
            "target": "beam",
            "sample": {"name": "beam", "has_device": True, "generation": 1},
            "settings-context": {"target": "beam", "generation": 1, "stamp": None},
        },
        "sample.data",
    )
    assert "cycle-on" not in rendered


def test_settings_read_updates_fields_once_per_read_not_every_poll(config):
    app = create_app(SimpleNamespace(configs=[config]))
    key = next(key for key in app.callback_map if "cycle-on.value" in key)
    sample = {
        "name": "beam",
        "has_device": True,
        "generation": 1,
        "cycle_parameters": {"on_ms": 1000, "off_ms": 2000, "cycles": 3},
        "settings_observed_at": "2026-11-07T00:00:00+00:00",
    }
    rendered = post_callback(app, key, {"target": "beam", "sample": sample}, "sample.data")
    assert rendered["cycle-on"]["value"] == 1000
    assert rendered["cycles"]["value"] == 3
    context = rendered["settings-context"]["data"]
    polled = post_callback(
        app, key, {"target": "beam", "sample": sample, "settings-context": context}, "sample.data"
    )
    assert "cycle-on" not in polled


@pytest.mark.parametrize("connected,context_generation", [(False, 1), (True, 1), (True, 0)])
def test_protection_assertions_end_at_actual_disconnect(config, connected, context_generation):
    app = create_app(SimpleNamespace(configs=[config]))
    key = next(key for key in app.callback_map if "source-inhibited.value" in key)
    assert "sample" in {item["id"] for item in app.callback_map[key]["inputs"]}
    rendered = post_callback(
        app,
        key,
        {
            "target": "beam",
            "sample": {"name": "beam", "has_device": connected, "generation": 1},
            "confirmation-context": {"target": "beam", "generation": context_generation},
        },
        "sample.data",
    )
    if connected and context_generation == 1:
        assert "source-inhibited" not in rendered
        assert "live-readback" not in rendered
    else:
        assert rendered["source-inhibited"]["value"] == []
        assert rendered["persist"]["value"] == []
        assert rendered["live-readback"]["value"] == []
