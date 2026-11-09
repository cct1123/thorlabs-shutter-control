"""Documented KSC101 flag decoding only; no physical state or SDK execution."""

import struct
from dataclasses import asdict, replace

import pytest
from ui_helpers import post_callback

from thorlabs_shutter_control.gui import create_app
from thorlabs_shutter_control.protocol import Decoder


def set_status_flags(device, mask):
    """Inject documented flags into the fake status reply, preserving output bit0."""

    def rewrite(raw):
        frame = Decoder().feed(raw)[0]
        if frame.message_id == 0x042A:
            channel, bits = struct.unpack("<HI", frame.payload)
            return replace(frame, payload=struct.pack("<HI", channel, bits | mask)).encode()
        return raw

    device.rewrite = rewrite


@pytest.mark.parametrize("bits", [0, 1, 0x1000, 0x80000000, 0x80001001, 0x2000, 0xA0001000])
def test_live_status_decodes_exact_manufacturer_masks_without_extra_requests(bench, bits):
    hub, devices, _, _ = bench
    hub.connect("beam")

    def rewrite(raw):
        frame = Decoder().feed(raw)[0]
        if frame.message_id == 0x042A:
            return replace(frame, payload=struct.pack("<HI", 1, bits)).encode()
        return raw

    devices[0].rewrite = rewrite
    before = len(devices[0].history)
    sample = hub.get_status("beam")
    assert sample.status_bits == bits
    assert sample.interlock_status_bit is bool(bits & 0x1000)
    assert sample.channel_enabled_bit is bool(bits & 0x80000000)
    assert sample.electrical_state == ("on" if bits & 1 else "off")
    assert sample.electrical_observed_at
    assert [f.message_id for _, f in devices[0].history[before:]] == [
        0x0005,
        0x04C1,
        0x04C7,
        0x0429,
    ]
    assert not devices[0].output_frames
    # No cached flags escape through passive host-only/disconnected snapshots.
    passive = hub.connection_snapshot("beam")
    assert (
        passive.status_bits is passive.interlock_status_bit is passive.channel_enabled_bit is None
    )
    hub.disconnect("beam")
    offline = hub.get_status("beam")
    assert offline.interlock_status_bit is offline.channel_enabled_bit is None


def test_on_and_off_results_carry_flags_from_their_own_status_readback(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    set_status_flags(devices[0], 0x80001000)
    opened = hub.set_solenoid("beam", True)
    assert opened.electrical_state == "on"
    assert opened.interlock_status_bit is opened.channel_enabled_bit is True
    closed = hub.safe_state("beam")
    assert closed.electrical_state == "off"
    assert closed.interlock_status_bit is closed.channel_enabled_bit is True


@pytest.mark.parametrize(
    "value,connected,dated,expected",
    [
        (True, True, True, "Set"),
        (False, True, True, "Clear"),
        (None, True, True, "Unknown"),
        (True, False, True, "Unknown"),
        (True, True, False, "Unknown"),
        (1, True, True, "Unknown"),
    ],
)
def test_gui_displays_only_dated_boolean_flags(bench, value, connected, dated, expected):
    hub, _, _, _ = bench
    hub.connect("beam")
    sample = asdict(hub.get_status("beam"))
    sample.update(interlock_status_bit=value, channel_enabled_bit=value, has_device=connected)
    if not dated:
        sample["electrical_observed_at"] = None
    app = create_app(hub)
    key = next(k for k in app.callback_map if "serial-label.children" in k)
    shown = post_callback(app, key, {"target": "beam", "sample": sample}, "sample.data")
    assert shown["interlock-lamp-value"]["children"] == expected
    assert shown["channel-lamp-value"]["children"] == expected


def test_refusal_retains_flags_with_original_timestamp_and_authoritative_fault_state(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    set_status_flags(devices[0], 0x80001000)
    previous = asdict(hub.get_status("beam"))
    app = create_app(hub)
    key = next(k for k in app.callback_map if "notice.children" in k)
    before = len(devices[0].history)
    response = post_callback(
        app,
        key,
        {"target": "beam", "sample": previous, "apply-led": 1, "led-modes": [1]},
        "apply-led.n_clicks",
    )
    sample = response["sample"]["data"]
    assert sample["interlock_status_bit"] is sample["channel_enabled_bit"] is True
    assert sample["electrical_observed_at"] == previous["electrical_observed_at"]
    assert len(devices[0].history) == before
    hub._channel("beam").error = "Fault after previous reading"
    response = post_callback(
        app,
        key,
        {"target": "beam", "sample": previous, "apply-led": 1, "led-modes": [1]},
        "apply-led.n_clicks",
    )
    assert response["sample"]["data"]["interlock_status_bit"] is None
    assert response["sample"]["data"]["channel_enabled_bit"] is None


def test_ui_uses_literal_flag_and_request_labels_instead_of_claiming_key_ready_or_activity(bench):
    import json

    hub, devices, _, _ = bench
    app = create_app(hub)
    layout = json.dumps(app.server.test_client().get("/_dash-layout").get_json())
    assert "Interlock flag" in layout and "Channel flag" in layout
    assert "Software fault" in layout and "Native request" in layout
    assert "Key/Ready and actual native activity are not decoded." in layout
    assert "Key Enabled" not in layout and "Is Ready" not in layout
    assert not devices
