"""Localhost control panel; all device actions use the canonical APT owner."""

import json
import math
from dataclasses import asdict
from pathlib import Path

from .device import MODES, CycleParameters
from .errors import ShutterError

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
)


def execute_action(hub, action, target, *, source_inhibited=False, parameters=None, persist=False):
    """One device dispatch path for the UI; no alternate backend or cached success."""
    if target not in {c.name for c in hub.configs}:
        raise ValueError("Select an exact configured target before using a control")
    if action == "connect":
        if not hub.connection_snapshot(target).has_device:
            hub.connect(target)
        return hub.get_status(target), "Connected to the exact controller; fresh feedback received."
    if action in ("read", "poll"):
        sample = hub.get_status(target)
        return sample, (
            "Readback updated."
            if sample.has_device
            else "Disconnected; no device feedback was requested."
        )
    if action == "release":
        if hub.connection_snapshot(target).requested_state in ("on", "start"):
            raise ShutterError("Stop / OFF before releasing an active output or native sequence")
        hub.disconnect(target)
        return hub.connection_snapshot(
            target
        ), "Communication released. Optical state is not measured."
    if action in MODES.values():
        return hub.set_operating_mode(target, action, source_inhibited=source_inhibited), (
            "Mode selected and read back. Changed modes are remembered at power-up."
        )
    if action == "on":
        return hub.start(target, source_inhibited=source_inhibited), (
            "Open / Start sent once. Electrical feedback does not confirm activity."
        )
    if action in ("off", "settings-stop"):
        return hub.safe_state(target), "Stop / OFF sent; fresh electrical OFF readback received."
    if action == "pulse":
        return hub.pulse(target, 1.0), "One 1-second host hold completed; electrical OFF read back."
    if action == "identify":
        return hub.blink_identify(
            target
        ), "Identify LED flash requested. APT provides no flash acknowledgement."
    if action == "read-settings":
        return hub.get_cycle_parameters(
            target
        ), "Device cycle settings read. No defaults were written."
    if action == "apply-settings":
        sample = hub.set_cycle_parameters(
            target, parameters, source_inhibited=source_inhibited, persist=persist
        )
        return sample, "Cycle settings match fresh readback. " + sample.settings_persistence
    raise ValueError("Unknown WebUI action")


def _integer(value, label):
    if type(value) not in (int, float) or not math.isfinite(value) or int(value) != value:
        raise ValueError(f"{label} must be a whole number")
    return int(value)


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

    def unavailable(label, explanation, controls):
        return html.Fieldset(
            [
                html.Legend(label),
                html.P(explanation, className="field-note"),
                *controls,
            ],
            className="settings-group unavailable",
            disabled=True,
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
                                                    "Prime for qualified external trigger control",
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
                "Native modes need a reviewed load policy. Mode changes persist.",
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
                                                "disabled": True,
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
                            unavailable(
                                "Device display",
                                "Display settings need a verified KSC101 APT layout.",
                                [
                                    html.Label("Display intensity (%)"),
                                    dcc.Input(
                                        type="number",
                                        min=0,
                                        max=100,
                                        placeholder="Not read",
                                        disabled=True,
                                    ),
                                    html.Label("Dim on inactivity"),
                                    dcc.Checklist(
                                        options=[
                                            {
                                                "label": "Dim display",
                                                "value": "dim",
                                                "disabled": True,
                                            }
                                        ],
                                        value=[],
                                    ),
                                    html.Label("Display timeout (min)"),
                                    dcc.Input(type="number", min=1, max=480, disabled=True),
                                    html.Label("Dimmed intensity (%)"),
                                    dcc.Input(type="number", min=0, max=10, disabled=True),
                                ],
                            ),
                            unavailable(
                                "Trigger I/O",
                                "Trigger settings need a verified KSC101 APT layout.",
                                [
                                    html.Label("Trigger 1 mode / polarity"),
                                    dcc.Dropdown(
                                        options=["Disabled", "Input", "Output"],
                                        placeholder="Not read",
                                        disabled=True,
                                    ),
                                    dcc.Dropdown(
                                        options=["Active high", "Active low"],
                                        placeholder="Not read",
                                        disabled=True,
                                    ),
                                    html.Label("Trigger 2 mode / polarity"),
                                    dcc.Dropdown(
                                        options=["Disabled", "Input", "Output"],
                                        placeholder="Not read",
                                        disabled=True,
                                    ),
                                    dcc.Dropdown(
                                        options=["Active high", "Active low"],
                                        placeholder="Not read",
                                        disabled=True,
                                    ),
                                ],
                            ),
                        ],
                        className="settings-grid",
                    ),
                    dcc.Checklist(
                        id="persist",
                        options=[
                            {
                                "label": "Persist cycle settings to device EEPROM",
                                "value": "persist",
                                "disabled": True,
                            }
                        ],
                        value=[],
                    ),
                    html.P(
                        "EEPROM requests need separate permission and restart verification.",
                        className="field-note",
                    ),
                    html.Button(
                        "Apply cycle settings", id="apply-settings", className="apply-button"
                    ),
                ],
                id="settings-dialog",
                open=False,
            ),
            html.Details(
                [html.Summary("Readback and diagnostics"), html.Pre("No sample", id="result")],
                className="diagnostics",
            ),
            dcc.Store(id="sample"),
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
        [Input(key, "n_clicks") for key in ACTIONS],
        Input("poll", "n_intervals"),
        State("target", "value"),
        State("source-inhibited", "value"),
        State("cycle-on", "value"),
        State("cycle-off", "value"),
        State("cycles", "value"),
        State("continuous", "value"),
        State("persist", "value"),
        prevent_initial_call=True,
    )
    def act(*values):
        target, protection, on_ms, off_ms, count, continuous, persist = values[-7:]
        try:
            if target not in {c.name for c in hub.configs}:
                raise ValueError("Select an exact configured target before using a control")
            parameters = None
            if ctx.triggered_id == "apply-settings":
                count = 0 if "continuous" in (continuous or []) else _integer(count, "Cycle count")
                if count == 0 and "continuous" not in (continuous or []):
                    raise ValueError("Select Continuous explicitly to use cycle count 0")
                parameters = CycleParameters(
                    _integer(on_ms, "On duration"), _integer(off_ms, "Off duration"), count
                )
            sample, message = execute_action(
                hub,
                ctx.triggered_id,
                target,
                source_inhibited="protected" in (protection or []),
                parameters=parameters,
                persist="persist" in (persist or []),
            )
            # A background status refresh must not erase a command/refusal message.
            return asdict(sample), no_update if ctx.triggered_id == "poll" else message
        except Exception as exc:
            snapshot = no_update
            if target in {c.name for c in hub.configs}:
                snapshot = asdict(hub.connection_snapshot(target))
            return snapshot, "Refused or unconfirmed: " + str(exc) + " " + " ".join(
                getattr(exc, "__notes__", [])
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
        context = context if isinstance(context, dict) else {}
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
        Output("profile-note", "children"),
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
            )
        ],
        Output("persist", "options"),
        Output("continuous", "options"),
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
        feedback = sample.get("feedback", {})
        policy = config.policy if config else None
        connected, fault = bool(sample.get("has_device")), bool(sample.get("error"))
        mode = feedback.get("operating_mode", "unknown")
        qualified = policy.qualified_modes if policy else ()
        controllable = bool(
            policy
            and config.route.kind != "vcp"
            and not (config.route.kind == "keh3" and config.route.bay == "external")
        )
        ready = connected and not fault and controllable and mode in qualified
        cycle = sample.get("cycle_parameters") or {}
        note = "No controller selected."
        if config:
            note = "Qualified modes: " + (", ".join(qualified) or "read-only")
            if policy:
                note += (
                    f" · OFF rest ≥ {policy.min_off_s:g} s · cycle limit {policy.max_cycle_count}"
                )
            note += ". Mode changes persist; physical protection is an operator condition."
        result = [
            ("Verified S/N " + sample["observed_serial_number"])
            if sample.get("identity_verified")
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
            "Last electrical read: " + (feedback.get("electrical_observed_at") or "none"),
            note,
            json.dumps(sample, indent=2) if sample else "No sample",
        ]
        for item in MODES.values():
            result.extend(
                [
                    "mode-button selected" if mode == item else "mode-button",
                    not (connected and not fault and controllable and item in qualified),
                ]
            )
        result.extend(
            [
                not ready
                or feedback.get("electrical_state") == "on"
                or sample.get("requested_state") == "start",
                not (connected and controllable),
                not (connected and controllable),
                not (ready and mode == "manual" and feedback.get("electrical_state") == "off"),
                not (connected and not fault),
                not (connected and not fault),
                not (ready and policy and policy.allow_device_settings and mode == "manual"),
                [
                    {
                        "label": "Persist cycle settings to device EEPROM",
                        "value": "persist",
                        "disabled": not bool(policy and policy.allow_persistent_settings),
                    }
                ],
                [
                    {
                        "label": "Continuous (count 0)",
                        "value": "continuous",
                        "disabled": not bool(policy and policy.allow_continuous_cycles),
                    }
                ],
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
            if feedback.get("electrical_state") == "on"
            else ("off", "Off")
            if feedback.get("electrical_state") == "off"
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
