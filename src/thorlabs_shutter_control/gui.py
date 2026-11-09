"""Localhost control panel; all device actions use the canonical APT owner."""

import json
from dataclasses import asdict
from pathlib import Path

from .controller import MODES, CycleParameters

DETAIL_ACTIONS = (
    "read-channel",
    "read-bay",
    "read-led",
    "apply-led",
    "require-interlock",
    "start-updates",
    "stop-updates",
    "read-events",
    "hardware-disconnect",
)
LED_MODES = ((1, "Identify"), (2, "Limit indication"), (8, "Activity indication"))

ACTIONS = (
    "connect",
    "read",
    "release",
    "manual",
    "single",
    "auto",
    "triggered",
    "on",
    "off",
    "settings-stop",
    "pulse",
    "identify",
    "read-settings",
    "apply-settings",
    *DETAIL_ACTIONS,
)


def execute_action(
    hub, action, target, *, source_inhibited=False, cycle_values=None, persist=False, led_modes=()
):
    """Return (status, notice, optional details) through the shared controller only."""
    if target not in {c.name for c in hub.configs}:
        raise ValueError("Select an exact configured target before using a control")
    if action == "connect":
        if not hub.connection_snapshot(target).has_device:
            hub.connect(target)
        return (
            hub.get_status(target),
            "Connected to the exact controller; fresh feedback received.",
            None,
        )
    if action in ("read", "poll"):
        sample = hub.get_status(target)
        return (
            sample,
            (
                "Readback updated."
                if sample.has_device
                else "Disconnected; no device feedback was requested."
            ),
            None,
        )
    if action == "release":
        hub.disconnect(target, require_stopped=True)
        return (
            hub.connection_snapshot(target),
            "Communication released. Optical state is not measured.",
            None,
        )
    if action in MODES.values():
        return (
            hub.set_operating_mode(target, action, source_inhibited=source_inhibited),
            ("Mode selected and read back. Changed modes are remembered at power-up."),
            None,
        )
    if action == "on":
        return (
            hub.start(target, source_inhibited=source_inhibited),
            ("Open / Start sent once. Electrical feedback does not confirm activity."),
            None,
        )
    if action in ("off", "settings-stop"):
        return (
            hub.safe_state(target),
            "Stop / OFF sent; fresh electrical OFF readback received.",
            None,
        )
    if action == "pulse":
        return (
            hub.pulse(target, 1.0),
            "One 1-second host hold completed; electrical OFF read back.",
            None,
        )
    if action == "identify":
        return (
            hub.blink_identify(target),
            "Identify LED flash requested. APT provides no flash acknowledgement.",
            None,
        )
    if action == "read-settings":
        return (
            hub.get_cycle_parameters(target),
            "Device cycle settings read. No defaults were written.",
            None,
        )
    if action == "apply-settings":
        on_ms, off_ms, count, continuous = cycle_values
        if continuous:
            count = 0
        elif count == 0:
            raise ValueError("Select Continuous explicitly to use cycle count 0")
        sample = hub.set_cycle_parameters(
            target,
            CycleParameters(on_ms, off_ms, count),
            source_inhibited=source_inhibited,
            persist=persist,
        )
        return sample, "Cycle settings match fresh readback. " + sample.settings_persistence, None
    if action == "require-interlock":
        return (
            hub.require_interlock(target, source_inhibited=source_inhibited),
            ("Interlock requirement confirmed. Contact continuity is not measured."),
            None,
        )
    if action == "hardware-disconnect":
        return (
            hub.disconnect_hardware(target, source_inhibited=source_inhibited),
            ("Hardware disconnect sent and communication released; no device acknowledgement."),
            None,
        )
    if action == "read-channel":
        details = {"channel_enabled": hub.get_channel_enabled(target)}
        notice = "Channel enable read; this does not measure blade position."
    elif action == "read-bay":
        details = {"bay": hub.get_hub_bay_reply(target)}
        notice = "Raw bay byte read. Configured routing is unchanged."
    elif action == "read-led":
        details = {"led_modes": hub.get_led_modes(target)}
        notice = "LED indication modes read. No settings were written."
    elif action == "apply-led":
        flags = set(led_modes or [])
        if not flags <= {1, 2, 8} or any(type(bit) is not int for bit in flags):
            raise ValueError("Select only the documented LED indications")
        details = {
            "led_modes": hub.set_led_modes(target, sum(flags), source_inhibited=source_inhibited)
        }
        notice = "LED modes match device RAM readback. No EEPROM request sent."
    elif action in ("start-updates", "stop-updates"):
        if action == "start-updates":
            hub.start_updates(target)
            request = "Start requested"
        else:
            hub.stop_updates(target)
            request = "Stop requested"
        details = {"update_request": request}
        notice = request + "; no device acknowledgement. Stop messages before Release."
    elif action == "read-events":
        events = hub.get_events(target)
        details = {
            "events": [{"id": f"0x{f.message_id:04X}", "frame": f.encode().hex()} for f in events]
        }
        notice = f"Collected {len(events)} raw events; payloads are not interpreted."
    else:
        raise ValueError("Unknown WebUI action")
    return hub.get_status(target), notice, details


def create_app(hub):
    from dash import Dash, Input, Output, State, ctx, dcc, html, no_update

    app = Dash(
        __name__,
        assets_folder=str(Path(__file__).with_name("assets")),
        title="KSC101 | Shutter Control",
    )

    def led(label, key, title):
        return html.Div(
            [
                html.Span(label),
                html.Span("Unknown", id=key + "-value", className="lamp-value"),
                html.Span(
                    id=key,
                    className="lamp unknown",
                    role="img",
                    **{"aria-label": label + ": Unknown"},
                ),
            ],
            className="indicator",
            title=title,
        )

    app.layout = html.Main(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.P("DIRECT APT CONTROL", className="eyebrow"),
                            html.H1("Shutter controller"),
                        ]
                    ),
                    html.Span("LOCALHOST", className="local-badge"),
                ],
                className="page-heading",
            ),
            html.Div(
                [
                    html.Label("Configured controller", htmlFor="target"),
                    dcc.Dropdown(
                        id="target",
                        options=[c.name for c in hub.configs],
                        clearable=False,
                        placeholder="Select an exact controller",
                    ),
                    html.Button("Connect", id="connect", className="utility"),
                    html.Button("Read state", id="read", className="utility"),
                    html.Button("Release", id="release", className="utility"),
                ],
                className="connection-bar",
            ),
            html.Section(
                [
                    html.Header(
                        [
                            html.Span("K-Cube Solenoid Controller"),
                            html.Span("S/N —", id="serial-label"),
                        ],
                        className="instrument-title",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2("Operating mode", className="panel-heading"),
                                    html.Div(
                                        [
                                            html.Button(
                                                [
                                                    html.Span(icon, className="mode-icon"),
                                                    html.Span(label),
                                                    html.Span(className="mode-dot"),
                                                ],
                                                id=mode,
                                                className="mode-button",
                                                title=description,
                                            )
                                            for mode, label, icon, description in (
                                                (
                                                    "manual",
                                                    "Manual",
                                                    "M",
                                                    "Direct Open / Close; no implicit mode change",
                                                ),
                                                (
                                                    "single",
                                                    "Single",
                                                    "1",
                                                    "One controller-timed ON interval",
                                                ),
                                                (
                                                    "auto",
                                                    "Auto",
                                                    "↻",
                                                    "Native cycles with device timing and count",
                                                ),
                                                (
                                                    "triggered",
                                                    "Triggered",
                                                    "↗",
                                                    "External-trigger mode; priming is separate",
                                                ),
                                            )
                                        ],
                                        className="mode-grid",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("On duration"),
                                            html.Strong("Not read", id="on-duration"),
                                            html.Span("Off duration"),
                                            html.Strong("Not read", id="off-duration"),
                                            html.Span("Cycles"),
                                            html.Strong("Not read", id="cycle-count"),
                                        ],
                                        className="timing-readout",
                                    ),
                                ],
                                className="mode-column",
                            ),
                            html.Div(
                                [
                                    html.H2("Output control", className="panel-heading"),
                                    html.Div(
                                        [
                                            html.Button(
                                                [
                                                    html.Span("○", className="action-symbol"),
                                                    html.Span("Open / ON", id="on-label"),
                                                ],
                                                id="on",
                                                className="output-action open-action",
                                                title="Open / Start in the current mode",
                                            ),
                                            html.Button(
                                                [
                                                    html.Span("■", className="action-symbol"),
                                                    html.Span("Close / OFF", id="off-label"),
                                                ],
                                                id="off",
                                                className="output-action close-action",
                                                title="Priority OFF; mode unchanged",
                                            ),
                                        ],
                                        className="primary-actions",
                                    ),
                                    html.Div(
                                        [
                                            html.Button(
                                                "⚙  Settings",
                                                id="settings",
                                                className="settings-button",
                                            ),
                                            html.Button(
                                                "1-second ON, then OFF",
                                                id="pulse",
                                                className="pulse-button",
                                                title="One Manual host hold, then OFF",
                                            ),
                                        ],
                                        className="secondary-actions",
                                    ),
                                    html.P(
                                        "Electrical output is not an optical position sensor.",
                                        className="output-note",
                                    ),
                                ],
                                className="action-column",
                            ),
                            html.Div(
                                [
                                    html.H2("Controller status", className="panel-heading"),
                                    led(
                                        "Key Enabled",
                                        "key-lamp",
                                        "Key position unavailable from verified APT feedback.",
                                    ),
                                    led(
                                        "Is Ready",
                                        "ready-lamp",
                                        "Readiness is not inferred from output or policy.",
                                    ),
                                    led(
                                        "Error",
                                        "error-lamp",
                                        "Reported fault; not all hardware faults are observable.",
                                    ),
                                    html.Hr(),
                                    led(
                                        "Output ON",
                                        "output-lamp",
                                        "Electrical output; not independent blade position.",
                                    ),
                                    led(
                                        "Activity",
                                        "active-lamp",
                                        "Start requested is not confirmed Active.",
                                    ),
                                    html.Button(
                                        [html.Span(className="identify-dot"), "Identify"],
                                        id="identify",
                                        className="identify-button",
                                        title="Flash this controller's LEDs only",
                                    ),
                                ],
                                className="status-column",
                            ),
                        ],
                        className="instrument-body",
                    ),
                    html.Footer(
                        [
                            html.Span("Disconnected", id="connection-label"),
                            html.Span("No controller selected", id="route-label"),
                        ],
                        className="instrument-footer",
                    ),
                ],
                className="instrument",
            ),
            html.Div(
                [
                    html.Span("No live feedback", id="readback-time"),
                    dcc.Checklist(
                        id="live-readback",
                        options=[{"label": "Live readback", "value": "live"}],
                        value=[],
                    ),
                ],
                className="readback-bar",
            ),
            html.Div(
                "Select a controller, then Connect. Startup never opens a device.",
                id="notice",
                role="status",
                className="notice",
            ),
            dcc.Checklist(
                id="source-inhibited",
                options=[
                    {
                        "label": "Source independently blocked; external triggers isolated",
                        "value": "protected",
                    }
                ],
                value=[],
                className="source-confirmation",
            ),
            html.P(
                "Mode changes persist. Source protection is an operator condition.",
                id="profile-note",
                className="profile-note",
            ),
            html.Dialog(
                [
                    html.Header(
                        [
                            html.H2("Controller settings"),
                            html.Button("Stop / OFF", id="settings-stop", className="emergency"),
                            html.Button("Close settings", id="settings-close", className="utility"),
                        ],
                        className="dialog-heading",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Fieldset(
                                        [
                                            html.Legend("Cycle settings"),
                                            html.Label("On duration (ms)", htmlFor="cycle-on"),
                                            dcc.Input(
                                                id="cycle-on",
                                                type="number",
                                                min=100,
                                                max=10000,
                                                step=1,
                                                placeholder="100–10000",
                                            ),
                                            html.Label("Off duration (ms)", htmlFor="cycle-off"),
                                            dcc.Input(
                                                id="cycle-off",
                                                type="number",
                                                min=100,
                                                max=10000,
                                                step=1,
                                                placeholder="100–10000",
                                            ),
                                            html.Label("Cycle count", htmlFor="cycles"),
                                            dcc.Input(
                                                id="cycles",
                                                type="number",
                                                min=1,
                                                max=1000000,
                                                step=1,
                                                placeholder="1–1000000",
                                            ),
                                            dcc.Checklist(
                                                id="continuous",
                                                options=[
                                                    {
                                                        "label": "Continuous (count 0)",
                                                        "value": "continuous",
                                                    }
                                                ],
                                                value=[],
                                            ),
                                            html.P(
                                                "Milliseconds. Opening this panel writes nothing.",
                                                className="field-note",
                                            ),
                                            html.Button(
                                                "Read device settings",
                                                id="read-settings",
                                                className="utility",
                                            ),
                                        ],
                                        className="settings-group",
                                    ),
                                    dcc.Checklist(
                                        id="persist",
                                        options=[
                                            {
                                                "label": "Persist cycle settings to device EEPROM",
                                                "value": "persist",
                                            }
                                        ],
                                        value=[],
                                    ),
                                    html.P(
                                        "EEPROM needs separate permission "
                                        "and restart verification.",
                                        className="field-note",
                                    ),
                                    html.Button(
                                        "Apply cycle settings",
                                        id="apply-settings",
                                        className="apply-button",
                                    ),
                                ]
                            ),
                            html.Fieldset(
                                [
                                    html.Legend("Controller options"),
                                    html.Label("LED indications"),
                                    dcc.Checklist(
                                        id="led-modes",
                                        options=[
                                            {"label": label, "value": bit}
                                            for bit, label in LED_MODES
                                        ],
                                        value=[],
                                    ),
                                    html.P("Not read", id="led-reading", className="field-note"),
                                    html.Div(
                                        [
                                            html.Button(
                                                "Read LED modes", id="read-led", className="utility"
                                            ),
                                            html.Button(
                                                "Apply LED modes",
                                                id="apply-led",
                                                className="utility",
                                            ),
                                        ],
                                        className="diagnostic-tools",
                                    ),
                                    html.P(
                                        "Interlock requirement: Unknown", id="interlock-reading"
                                    ),
                                    html.Button(
                                        "Require interlock",
                                        id="require-interlock",
                                        className="utility",
                                    ),
                                    html.P(
                                        "Confirm source protection on the main panel "
                                        "before settings writes. The interlock setting "
                                        "does not measure contact continuity.",
                                        className="field-note",
                                    ),
                                ],
                                className="settings-group controller-options",
                            ),
                        ],
                        className="settings-layout",
                    ),
                    html.Div(
                        "Settings results appear here.",
                        id="settings-notice",
                        role="status",
                        className="notice",
                    ),
                ],
                id="settings-dialog",
                open=False,
            ),
            html.Details(
                [
                    html.Summary("Readback and diagnostics"),
                    html.Div(
                        [
                            html.Button(label, id=key, className="utility")
                            for key, label in (
                                ("read-channel", "Read channel enable"),
                                ("read-bay", "Read raw bay"),
                                ("start-updates", "Start device messages"),
                                ("stop-updates", "Stop device messages"),
                                ("read-events", "Collect raw events"),
                            )
                        ],
                        className="diagnostic-tools",
                    ),
                    html.Div(
                        [
                            html.Span("Channel enable: Not read", id="channel-reading"),
                            html.Span("Raw bay: Not read", id="bay-reading"),
                            html.Span("Device messages: No request", id="update-request"),
                        ],
                        className="diagnostic-readings",
                    ),
                    html.P(
                        "These are last explicit reads, not optical feedback. Device messages are "
                        "separate from Live readback; stop them before Release.",
                        className="field-note",
                    ),
                    html.Pre("No events collected", id="event-data"),
                    html.Div(
                        [
                            html.Button(
                                "Disconnect hardware", id="hardware-disconnect", className="utility"
                            ),
                            html.Span(
                                "Requires source protection and Manual/OFF. "
                                "Release only closes communication.",
                                className="field-note",
                            ),
                        ],
                        className="diagnostic-tools",
                    ),
                    html.Details(
                        [
                            html.Summary("Full controller readback"),
                            html.Pre("No sample", id="result"),
                        ]
                    ),
                ],
                className="diagnostics",
            ),
            dcc.Store(id="sample"),
            dcc.Store(id="details"),
            dcc.Store(id="settings-context"),
            dcc.Store(id="confirmation-context"),
            dcc.Interval(id="poll", interval=1000, disabled=True),
        ],
        className="shutter-app",
    )

    @app.callback(
        Output("settings-dialog", "open"),
        Input("settings", "n_clicks"),
        Input("settings-close", "n_clicks"),
        prevent_initial_call=True,
    )
    def settings_dialog(_open, _close):
        return ctx.triggered_id == "settings"

    @app.callback(
        Output("source-inhibited", "value"),
        Output("persist", "value"),
        Output("live-readback", "value"),
        Output("confirmation-context", "data"),
        Input("target", "value"),
        Input("sample", "data"),
        State("confirmation-context", "data"),
    )
    def session_confirmation(target, sample, context):
        if (
            ctx.triggered_id == "target"
            or not sample
            or sample.get("name") != target
            or not sample.get("has_device")
        ):
            return [], [], [], None
        scope = {"target": target, "generation": sample.get("generation")}
        if context != scope:
            return [], [], [], scope
        return no_update, no_update, no_update, no_update

    @app.callback(
        Output("poll", "disabled"), Input("live-readback", "value"), Input("sample", "data")
    )
    def polling(values, sample):
        return not ("live" in (values or []) and sample and sample.get("has_device"))

    @app.callback(
        Output("sample", "data"),
        Output("notice", "children"),
        Output("settings-notice", "children"),
        Output("details", "data"),
        [Input(key, "n_clicks") for key in ACTIONS],
        Input("poll", "n_intervals"),
        State("target", "value"),
        State("source-inhibited", "value"),
        State("cycle-on", "value"),
        State("cycle-off", "value"),
        State("cycles", "value"),
        State("continuous", "value"),
        State("persist", "value"),
        State("led-modes", "value"),
        State("details", "data"),
        prevent_initial_call=True,
    )
    def act(*values):
        target, protection, on_ms, off_ms, count, continuous, persist, led_modes, previous = values[
            -9:
        ]
        try:
            sample, message, details = execute_action(
                hub,
                ctx.triggered_id,
                target,
                source_inhibited="protected" in (protection or []),
                cycle_values=(on_ms, off_ms, count, "continuous" in (continuous or [])),
                persist="persist" in (persist or []),
                led_modes=led_modes,
            )
            scope = {"target": target, "generation": sample.generation}
            previous = previous or {}
            same = all(previous.get(key) == value for key, value in scope.items())
            extra = no_update
            if not sample.has_device:
                extra = None
            elif not same or details is not None:
                extra = {
                    **scope,
                    "values": dict(previous.get("values") or {}) if same else {},
                    "action": ctx.triggered_id if details is not None else "reset",
                    "observed_at": sample.electrical_observed_at,
                }
                extra["values"].update(details or {})
            # Healthy polling preserves messages; a retained owner fault must stay visible.
            if sample.error:
                notice = (
                    (message + " " if not sample.has_device else "")
                    + f"Controller fault remains: {sample.error}. "
                    "Output activation is blocked; protected recovery is required."
                )
            else:
                notice = no_update if ctx.triggered_id == "poll" else message
            return asdict(sample), notice, notice, extra
        except Exception as exc:
            snapshot = no_update
            if target in {c.name for c in hub.configs}:
                snapshot = asdict(hub.connection_snapshot(target))
            message = (
                "Refused or unconfirmed: "
                + str(exc)
                + " "
                + " ".join(getattr(exc, "__notes__", []))
            )
            return snapshot, message, message, no_update

    @app.callback(
        Output("channel-reading", "children"),
        Output("bay-reading", "children"),
        Output("update-request", "children"),
        Output("event-data", "children"),
        Output("led-reading", "children"),
        Output("interlock-reading", "children"),
        Output("led-modes", "value"),
        Input("details", "data"),
        Input("sample", "data"),
        Input("target", "value"),
    )
    def detail_values(details, sample, target):
        details, sample = details or {}, sample or {}
        valid = (
            sample.get("name") == target
            and sample.get("has_device")
            and not sample.get("error")
            and details.get("target") == target
            and details.get("generation") == sample.get("generation")
        )
        values = details.get("values", {}) if valid else {}
        enabled, bay, modes = (
            values.get("channel_enabled"),
            values.get("bay"),
            values.get("led_modes"),
        )
        required = (
            sample.get("interlock_required")
            if (
                sample.get("name") == target
                and sample.get("has_device")
                and not sample.get("error")
            )
            else None
        )
        led_value = no_update
        if not valid:
            led_value = []
        elif ctx.triggered_id == "details":
            if details.get("action") == "reset":
                led_value = []
            elif details.get("action") in ("read-led", "apply-led"):
                led_value = [bit for bit, _ in LED_MODES if modes is not None and modes & bit]
        return (
            "Channel enable: "
            + ("Not read" if enabled is None else "Enabled" if enabled else "Disabled"),
            "Raw bay: " + ("Not read" if bay is None else f"{bay} (0x{bay:02X})"),
            "Device messages: " + values.get("update_request", "No request"),
            json.dumps(values["events"], indent=2) if "events" in values else "No events collected",
            "LED modes: "
            + ("Not read" if modes is None else f"0x{modes:04X}")
            + (
                ". Extra flags present; Apply replaces all flags."
                if modes is not None and modes & ~0x0B
                else ""
            ),
            "Interlock requirement: "
            + ("Unknown" if required is None else "Required" if required else "Not required"),
            led_value,
        )

    @app.callback(
        Output("cycle-on", "value"),
        Output("cycle-off", "value"),
        Output("cycles", "value"),
        Output("continuous", "value"),
        Output("settings-context", "data"),
        Input("sample", "data"),
        Input("target", "value"),
        State("settings-context", "data"),
        prevent_initial_call=True,
    )
    def settings_values(sample, target, context):
        sample = sample or {}
        if (
            ctx.triggered_id == "target"
            or sample.get("name") != target
            or not sample.get("has_device")
        ):
            return None, None, None, [], None
        scope = {"target": target, "generation": sample.get("generation")}
        context = context or {}
        changed = any(context.get(key) != value for key, value in scope.items())
        settings, stamp = sample.get("cycle_parameters"), sample.get("settings_observed_at")
        if not settings or not stamp:
            if changed:
                return None, None, None, [], {**scope, "stamp": None}
            return no_update, no_update, no_update, no_update, no_update
        if not changed and stamp == context.get("stamp"):
            return no_update, no_update, no_update, no_update, no_update
        return (
            settings["on_ms"],
            settings["off_ms"],
            settings["cycles"] or None,
            [] if settings["cycles"] else ["continuous"],
            {**scope, "stamp": stamp},
        )

    mode_outputs = [
        Output(mode, prop) for mode in MODES.values() for prop in ("className", "disabled")
    ]

    @app.callback(
        Output("serial-label", "children"),
        Output("connection-label", "children"),
        Output("route-label", "children"),
        Output("on-label", "children"),
        Output("off-label", "children"),
        Output("on-duration", "children"),
        Output("off-duration", "children"),
        Output("cycle-count", "children"),
        Output("readback-time", "children"),
        Output("result", "children"),
        *mode_outputs,
        *[
            Output(key, "disabled")
            for key in (
                "on",
                "off",
                "settings-stop",
                "pulse",
                "identify",
                "read-settings",
                "apply-settings",
                *DETAIL_ACTIONS,
            )
        ],
        *[
            Output(key, prop)
            for key in ("key-lamp", "ready-lamp", "error-lamp", "output-lamp", "active-lamp")
            for prop in ("className", "aria-label")
        ],
        *[
            Output(key + "-value", "children")
            for key in ("key-lamp", "ready-lamp", "error-lamp", "output-lamp", "active-lamp")
        ],
        Input("sample", "data"),
        Input("target", "value"),
    )
    def render(sample, target):
        config = next((c for c in hub.configs if c.name == target), None)
        sample = sample if sample and sample.get("name") == target else {}
        connected, fault = bool(sample.get("has_device")), bool(sample.get("error"))
        mode = sample.get("operating_mode", "unknown")
        ready = connected and not fault
        cycle = sample.get("cycle_parameters") or {}
        result = [
            ("Verified S/N " + sample["identity"]["serial_number"])
            if sample.get("identity")
            else ("Configured S/N " + config.serial_number if config else "S/N —"),
            "Fault" if fault else "Connected" if connected else "Disconnected",
            config.route.endpoint or "USB " + config.serial_number
            if config
            else "No controller selected",
            "Open / ON"
            if mode in ("manual", "unknown")
            else "Prime / Start"
            if mode == "triggered"
            else "Start",
            "Close / OFF" if mode in ("manual", "unknown") else "Stop / OFF",
            str(cycle["on_ms"]) + " ms" if cycle else "Not read",
            str(cycle["off_ms"]) + " ms" if cycle else "Not read",
            (str(cycle["cycles"]) if cycle.get("cycles") else "Continuous")
            if cycle
            else "Not read",
            "Last electrical read: " + (sample.get("electrical_observed_at") or "none"),
            json.dumps(sample, indent=2) if sample else "No sample",
        ]
        for item in MODES.values():
            result.extend(
                [
                    "mode-button selected" if mode == item else "mode-button",
                    not ready,
                ]
            )
        result.extend(
            [
                not ready
                or sample.get("electrical_state") == "on"
                or sample.get("requested_state") == "start",
                not connected,
                not connected,
                not (ready and mode == "manual" and sample.get("electrical_state") == "off"),
                not ready,
                not ready,
                not ready,
                *[not ready for _ in DETAIL_ACTIONS],
            ]
        )
        lamps = [
            ("unknown", "Unknown"),
            ("unknown", "Unknown"),
            ("fault", "Reported")
            if fault
            else ("off", "None reported")
            if connected
            else ("unknown", "Unknown"),
            ("unknown", "Unknown")
            if fault
            else ("on", "On")
            if sample.get("electrical_state") == "on"
            else ("off", "Off")
            if sample.get("electrical_state") == "off"
            else ("unknown", "Unknown"),
            ("requested", "Start requested")
            if sample.get("requested_state") == "start"
            else ("unknown", "Unknown"),
        ]
        for key, (kind, label) in zip(
            ("Key Enabled", "Is Ready", "Error", "Output ON", "Activity"), lamps, strict=True
        ):
            result.extend(["lamp " + kind, key + ": " + label])
        result.extend(label for _, label in lamps)
        return result

    return app


def run(hub, *, port=8050):
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("WebUI port must be an integer in 1..65535")
    app = create_app(hub)
    original = None
    try:
        app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False, threaded=True)
    except BaseException as exc:
        original = exc
    for cleanup in (hub.shutdown_outputs, hub.close):
        try:
            cleanup()
        except BaseException as exc:
            if original is None:
                original = exc
            else:
                original.add_note(f"{cleanup.__name__} failed: {exc}")
    if original is not None:
        raise original
