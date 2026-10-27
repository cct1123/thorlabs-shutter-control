"""The maintained launcher and GUI workflows through real Dash callback HTTP."""

from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from thorlabs_shutter_control import ShutterHub, controller, gui
from thorlabs_shutter_control import __main__ as launcher


def click(app, action, selections=None):
    """Post the app's one callback without a browser, socket or real SDK.

    selections maps serial component IDs to chosen values. The remaining State
    fields use the panel's default TTL draft. Dash expects flattened output IDs
    and State values even though our callback uses named groups internally.
    """
    callback_key = next(iter(app.callback_map))
    callback = app.callback_map[callback_key]
    selections = selections or {}
    states = []
    for item in callback["state"]:
        name = item["id"]
        if name.startswith("serial"):
            value = selections.get(name)
        elif "polarity" in name:
            value = "high"
        elif name.startswith("trig1-mode"):
            value = "input"
        else:
            value = "output"
        states.append(dict(item, value=value))
    response = app.server.test_client().post(
        "/_dash-update-component",
        json={
            "output": callback_key,
            "outputs": [
                {"id": o.component_id, "property": o.component_property} for o in callback["output"]
            ],
            "inputs": [dict(item, value=1) for item in callback["inputs"]],
            "state": states,
            "changedPropIds": [f"{action}.n_clicks"],
        },
    )
    assert response.status_code == 200, response.data
    return response.get_json()["response"]


@pytest.mark.parametrize("panels", [1, 3])
def test_gui_discovers_and_connects_the_selected_lan_route(bench, panels):
    suffix = "" if panels == 1 else "-1"
    selections = {f"serial{suffix}": bench.lan.serial}
    hub = ShutterHub(slots=panels)
    app = gui.create_app(hub)
    assert not bench.loads
    refresh = next(c for c in app.layout.children if getattr(c, "id", None) == "refresh")
    assert refresh.interval == 100
    found = click(app, "discover")
    assert len(found[f"serial{suffix}"]["options"]) == 2
    assert not bench.lan.IsConnected
    connected = click(app, f"connect{suffix}", selections)
    assert connected[f"connection{suffix}"]["children"] == "Connected"
    assert connected[f"serial{suffix}"]["disabled"]
    assert hub.ethernet_endpoints == (bench.endpoint,) + (None,) * (panels - 1)
    if panels == 3:
        assert connected["connection-2"]["children"] == "Disconnected"
        assert connected["close-2"]["disabled"]
    click(app, f"disconnect{suffix}", selections)
    assert not bench.lan.IsConnected


@pytest.mark.parametrize("panels", [1, 3])
def test_gui_operates_four_modes_and_stops_the_owned_server(bench, panels):
    suffix = "" if panels == 1 else "-1"
    selections = {f"serial{suffix}": bench.usb.serial}
    stopped = []
    app = gui.create_app(ShutterHub(slots=panels), on_shutdown=lambda: stopped.append(True))
    click(app, f"connect{suffix}", selections)
    for mode in ("manual", "single", "auto", "triggered"):
        selected = click(app, f"mode-{mode}{suffix}", selections)
        assert selected[f"mode-{mode}{suffix}"]["aria-pressed"] == "true"
        started = click(app, f"open{suffix}", selections)
        assert started[f"open{suffix}"]["children"] == ("Open" if mode == "manual" else "Start")
        assert bench.usb.operation == "Active"
        click(app, f"close{suffix}", selections)
        assert bench.usb.operation == "Inactive"
    click(app, f"mode-manual{suffix}", selections)
    click(app, f"apply-ttl{suffix}", selections)
    read = click(app, f"read-ttl{suffix}", selections)
    assert read[f"trig1-mode{suffix}"]["value"] == "input"
    click(app, f"arm-ttl{suffix}", selections)
    assert bench.usb.mode == "Triggered" and bench.usb.operation == "Active"
    click(app, f"disarm-ttl{suffix}", selections)
    assert bench.usb.mode == "Manual" and bench.usb.operation == "Inactive"
    click(app, "stop-server", selections)
    assert stopped == [True] and not bench.usb.IsConnected


@pytest.mark.parametrize("panels", [1, 3])
def test_gui_keeps_activation_disabled_for_unknown_feedback(bench, panels):
    suffix = "" if panels == 1 else "-1"
    selections = {f"serial{suffix}": bench.usb.serial}
    bench.usb.operation = "0"  # Observed KSC101 startup value; not Inactive.
    app = gui.create_app(ShutterHub(slots=panels))
    result = click(app, f"connect{suffix}", selections)
    assert result[f"connection{suffix}"]["children"] == "Connected"
    assert result[f"open{suffix}"]["disabled"] and result[f"arm-ttl{suffix}"]["disabled"]
    click(app, f"disconnect{suffix}", selections)


@pytest.mark.parametrize("transport", ["usb", "lan"])
def test_gui_connect_reads_one_combined_feedback_batch(bench, transport):
    device = bench.usb if transport == "usb" else bench.lan
    endpoints = [None] if transport == "usb" else [bench.endpoint]
    app = gui.create_app(ShutterHub(slots=1, ethernet_endpoints=endpoints))
    selections = {"serial": device.serial}

    start = controller.time.monotonic()
    result = click(app, "connect", selections)
    assert controller.time.monotonic() - start == 0
    assert [call[0] for call in device.calls] == [
        "connect",
        "poll",
        "identity",
        "status",
        "mode_read",
        "operation",
        "ttl_read",
    ]
    assert result["connection"]["children"] == "Connected"
    assert "TRIG1 input/high" in result["ttl-status"]["children"]
    assert not result["open"]["disabled"]
    # There was no Enable, mode, output or TTL write in the call history.
    click(app, "disconnect", selections)


def test_gui_connect_keeps_fault_and_cleanup_after_combined_read_failure(bench):
    app = gui.create_app(ShutterHub(slots=1))
    selections = {"serial": bench.usb.serial}
    bench.usb.fail = "ttl_read"
    result = click(app, "connect", selections)
    assert result["connection"]["children"] == "Fault"
    assert "ttl_read failed" in result["message"]["children"]
    assert result["open"]["disabled"] and result["arm-ttl"]["disabled"]
    assert result["serial"]["disabled"] and not result["close"]["disabled"]
    click(app, "disconnect", selections)
    assert not bench.usb.IsConnected


@pytest.mark.parametrize("transport", ["usb", "lan"])
def test_gui_apply_ttl_batches_readback_with_operating_feedback(bench, transport):
    device = bench.usb if transport == "usb" else bench.lan
    endpoints = [None] if transport == "usb" else [bench.endpoint]
    # The draft must change an actual setting, rather than confirm its old value.
    device.settings.Trigger1Mode = "Disabled"
    app = gui.create_app(ShutterHub(slots=1, ethernet_endpoints=endpoints))
    selections = {"serial": device.serial}
    click(app, "connect", selections)
    device.calls.clear()

    start = controller.time.monotonic()
    result = click(app, "apply-ttl", selections)
    assert controller.time.monotonic() - start == 0
    assert [call[0] for call in device.calls] == [
        "status",
        "mode_read",
        "operation",  # Prerequisites before writing.
        "ttl_write",
        "status",
        "mode_read",
        "operation",
        "ttl_read",  # One result batch.
    ]
    assert result["message"]["children"] == "TTL settings applied and read back; disarmed."
    assert "TRIG1 input/high" in result["ttl-status"]["children"]
    assert device.mode == "Manual" and device.operation == "Inactive"
    click(app, "disconnect", selections)


def test_gui_apply_ttl_refuses_to_write_while_active(bench):
    app = gui.create_app(ShutterHub(slots=1))
    selections = {"serial": bench.usb.serial}
    click(app, "connect", selections)
    bench.usb.operation, bench.usb.position = "Active", "Open"
    bench.usb.calls.clear()
    result = click(app, "apply-ttl", selections)
    assert "Disarm/Close before configuring TTL" in result["message"]["children"]
    assert [call[0] for call in bench.usb.calls] == ["status", "mode_read", "operation"]
    click(app, "disconnect", selections)


def test_gui_apply_ttl_reports_actual_readback_mismatch(bench, monkeypatch):
    bench.usb.settings.Trigger1Mode = "Disabled"
    app = gui.create_app(ShutterHub(slots=1))
    selections = {"serial": bench.usb.serial}
    click(app, "connect", selections)

    def ignore_write(settings):
        bench.usb.record("ttl_write")  # Device accepts the call but keeps its settings.

    monkeypatch.setattr(bench.usb, "SetTriggerConfigParams", ignore_write)
    result = click(app, "apply-ttl", selections)
    assert "TTL readback mismatch" in result["message"]["children"]
    assert "TRIG1 disabled/high" in result["ttl-status"]["children"]
    assert result["arm-ttl"]["disabled"]  # Neither actual port is an input.
    click(app, "disconnect", selections)


def test_gui_apply_ttl_keeps_fault_and_cleanup_after_readback_failure(bench):
    app = gui.create_app(ShutterHub(slots=1))
    selections = {"serial": bench.usb.serial}
    click(app, "connect", selections)
    bench.usb.fail = "ttl_read"
    result = click(app, "apply-ttl", selections)
    assert result["connection"]["children"] == "Fault"
    assert "ttl_read failed" in result["message"]["children"]
    assert result["open"]["disabled"] and result["arm-ttl"]["disabled"]
    assert result["serial"]["disabled"] and not result["close"]["disabled"]
    click(app, "disconnect", selections)
    assert not bench.usb.IsConnected


@pytest.mark.parametrize("retained_fault", [False, True])
def test_gui_discover_checks_ownership_without_device_reads(bench, retained_fault):
    app = gui.create_app(ShutterHub(slots=1))
    selections = {"serial": bench.usb.serial}
    click(app, "connect", selections)
    if retained_fault:
        bench.usb.fail = "disconnect"
        click(app, "disconnect", selections)
    bench.usb.calls.clear()

    result = click(app, "discover", selections)
    assert not bench.usb.calls
    assert result["serial"]["value"] == bench.usb.serial
    assert result["serial"]["disabled"]
    assert result["connection"]["children"] == ("Fault" if retained_fault else "Connected")
    bench.usb.fail = None
    click(app, "disconnect", selections)


@pytest.mark.parametrize("transport", ["usb", "lan"])
def test_gui_read_ttl_uses_one_full_snapshot(bench, transport):
    device = bench.usb if transport == "usb" else bench.lan
    endpoints = [None] if transport == "usb" else [bench.endpoint]
    app = gui.create_app(ShutterHub(slots=1, ethernet_endpoints=endpoints))
    selections = {"serial": device.serial}
    click(app, "connect", selections)
    device.settings.Trigger1Polarity = "TriggerLow"
    device.calls.clear()

    result = click(app, "read-ttl", selections)
    assert [c[0] for c in device.calls] == ["status", "mode_read", "operation", "ttl_read"]
    assert result["trig1-polarity"]["value"] == "low"
    assert "TRIG1 input/low" in result["ttl-status"]["children"]
    click(app, "disconnect", selections)


def test_gui_read_ttl_failure_keeps_fault_and_cleanup(bench):
    app = gui.create_app(ShutterHub(slots=1))
    selections = {"serial": bench.usb.serial}
    click(app, "connect", selections)
    bench.usb.fail = "ttl_read"
    result = click(app, "read-ttl", selections)
    assert result["connection"]["children"] == "Fault"
    assert "ttl_read failed" in result["message"]["children"]
    assert result["open"]["disabled"] and not result["close"]["disabled"]
    assert "value" not in result.get("trig1-mode", {})
    click(app, "disconnect", selections)
    assert not bench.usb.IsConnected


@pytest.mark.parametrize("transport", ["usb", "lan"])
def test_gui_trigger_start_combines_prerequisites_and_reads_result(bench, monkeypatch, transport):
    device = bench.usb if transport == "usb" else bench.lan
    endpoints = [None] if transport == "usb" else [bench.endpoint]
    hub = ShutterHub(slots=1, ethernet_endpoints=endpoints)
    app = gui.create_app(hub)
    selections = {"serial": device.serial}
    click(app, "connect", selections)
    click(app, "mode-triggered", selections)

    def separate_ttl_read(slot):
        pytest.fail("Known Trigger mode should include TTL in its prerequisite snapshot")

    monkeypatch.setattr(hub, "get_trigger_config", separate_ttl_read)
    device.calls.clear()
    result = click(app, "open", selections)
    assert [c[0] for c in device.calls] == [
        "status",
        "mode_read",
        "operation",
        "ttl_read",
        "state",
        "status",
        "mode_read",
        "operation",
    ]
    assert result["lamp-active"]["children"]["props"]["title"] == "On"
    click(app, "disconnect", selections)


@pytest.mark.parametrize("issue", ["key", "no_input", "active", "unknown", "read_failure"])
def test_gui_combined_trigger_read_still_refuses_unsafe_start(bench, issue):
    app = gui.create_app(ShutterHub(slots=1))
    selections = {"serial": bench.usb.serial}
    click(app, "connect", selections)
    click(app, "mode-triggered", selections)
    if issue == "key":
        bench.usb.Status.KeyEnabled = False
    elif issue == "no_input":
        bench.usb.settings.Trigger1Mode = "TrigOUT_GPO"
    elif issue == "active":
        bench.usb.operation, bench.usb.position = "Active", "Open"
    elif issue == "unknown":
        bench.usb.operation = "0"
    else:
        bench.usb.fail = "ttl_read"
    bench.usb.calls.clear()

    result = click(app, "open", selections)
    assert not any(c[0] in ("state", "mode", "enable", "ttl_write") for c in bench.usb.calls)
    assert result["open"]["disabled"]
    click(app, "disconnect", selections)
    assert not bench.usb.IsConnected


def test_gui_changed_mode_reads_actual_trigger_inputs_before_start(bench):
    app = gui.create_app(ShutterHub(slots=1))
    selections = {"serial": bench.usb.serial}
    click(app, "connect", selections)  # Display cache still says Manual.
    bench.usb.mode = "Triggered"
    bench.usb.settings.Trigger1Mode = "TrigOUT_GPO"
    bench.usb.calls.clear()

    result = click(app, "open", selections)
    assert ("ttl_read",) in bench.usb.calls
    assert not any(c[0] == "state" for c in bench.usb.calls)
    assert "Open refused" in result["message"]["children"]
    assert result["open"]["disabled"]
    click(app, "disconnect", selections)


def test_launcher_builds_passive_panels_and_exits_normally(bench, monkeypatch):
    stop = []
    create = gui.create_app

    def create_app(hub, *, on_shutdown):
        assert len(hub.controllers) == 3
        stop.append(on_shutdown)
        return create(hub, on_shutdown=on_shutdown)

    @contextmanager
    def server(host, port, application, *, threaded):
        assert host == "127.0.0.1" and not threaded
        yield SimpleNamespace(server_port=port, handle_request=lambda: stop[0]())

    monkeypatch.setattr(gui, "create_app", create_app)
    monkeypatch.setattr(launcher, "make_server", server)
    assert launcher.main() == 0
    assert not bench.loads and all(not d.calls for d in bench.devices.values())
