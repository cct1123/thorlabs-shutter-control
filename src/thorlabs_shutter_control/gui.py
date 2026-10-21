"""Local single-operator Dash UI for configured independently owned shutters."""

from collections.abc import Callable

from dash import Dash, Input, Output, State, ctx, dcc, html, no_update

from .controller import ShutterError, ShutterHub, TriggerConfig


def _message(text, component_id):
    return html.Div(
        text, id=component_id, role="status", className="message", **{"aria-live": "polite"}
    )


def _readout(label, value):
    return html.Div([html.Span(label, className="label"), value])


def _enabled(value):
    return "unknown" if value is None else ("enabled" if value else "not enabled")


def _route_label(endpoint):
    return f"Ethernet LAN · {endpoint}" if endpoint else "USB"


def _device_options(routes):
    return [
        {"label": f"{serial} · {_route_label(endpoint)}", "value": serial}
        for serial, endpoint in routes.items()
    ]


def _open_ready(status):
    return (
        status.connection == "connected"
        and status.key_enabled is True
        and status.operating_mode == "manual"
        and status.operating_state in ("active", "inactive")
        and status.shutter_state in ("open", "closed")
    )


def _arm_ready(status, config):
    return (
        status.is_closed_manual
        and status.key_enabled is True
        and config is not None
        and "input" in (config.trig1_mode, config.trig2_mode)
    )


MODES = (("manual", "Manual"), ("auto", "Auto"), ("single", "Single"), ("triggered", "Trigger"))


def _lamp(value, *, error=False):
    text = "Unknown" if value is None else ("On" if value else "Off")
    state = "unknown" if value is None else ("on" if value else "off")
    return html.Span(
        className=f"lamp lamp-{state}" + (" lamp-error" if error else ""),
        role="img",
        title=text,
        **{"aria-label": text},
    )


def _mode_ready(status):
    return (
        status.connection == "connected"
        and status.operating_state == "inactive"
        and status.shutter_state == "closed"
    )


def _action_ready(status, config):
    if status.operating_mode not in ("single", "auto", "triggered"):
        return _open_ready(status)
    return (
        _mode_ready(status)
        and status.key_enabled is True
        and (
            status.operating_mode != "triggered"
            or (config is not None and "input" in (config.trig1_mode, config.trig2_mode))
        )
    )


def _panel(slot, serial_number, serials, suffix, endpoint):
    return html.Section(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("KSC101", className="model-label"),
                            html.H2(f"Shutter {slot + 1}"),
                        ]
                    ),
                    html.Span("Disconnected", id=f"connection{suffix}", className="badge offline"),
                ],
                className="panel-heading",
            ),
            html.P(
                _route_label(endpoint),
                id=f"transport{suffix}",
                className="device-identity",
            ),
            html.Div(
                [
                    html.Label("Device serial", htmlFor=f"serial{suffix}"),
                    dcc.Dropdown(
                        id=f"serial{suffix}",
                        options=serials,
                        value=serial_number,
                        placeholder="Discover, then select a controller",
                    ),
                    html.Div(
                        [
                            html.Button(
                                "Connect", id=f"connect{suffix}", className="connect-button"
                            ),
                            html.Button(
                                "Close & disconnect",
                                id=f"disconnect{suffix}",
                                disabled=True,
                                title="Send Close and release this controller connection",
                            ),
                        ],
                        className="connection-actions",
                    ),
                ],
                className="device-connection",
            ),
            html.P("No controller connected", id=f"identity{suffix}", className="device-identity"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Button(
                                        label,
                                        id=f"mode-{mode}{suffix}",
                                        className="mode-button",
                                        disabled=True,
                                        **{"aria-pressed": "false"},
                                    )
                                    for mode, label in MODES
                                ],
                                className="mode-grid",
                                role="group",
                                **{"aria-label": "Operating mode"},
                            ),
                            html.Div(
                                [
                                    html.Button(
                                        "Close",
                                        id=f"close{suffix}",
                                        disabled=True,
                                        className="action-control stop-control",
                                    ),
                                    html.Button(
                                        "Open",
                                        id=f"open{suffix}",
                                        disabled=True,
                                        className="action-control start-control manual-control",
                                        **{"aria-describedby": f"control-hint{suffix}"},
                                    ),
                                ],
                                className="shutter-actions",
                            ),
                        ],
                        className="instrument-controls",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(label),
                                    html.Span(_lamp(None), id=f"lamp-{key}{suffix}"),
                                ],
                                className="indicator-row",
                            )
                            for key, label in (
                                ("key", "Key enabled"),
                                ("ready", "Ready"),
                                ("error", "Error"),
                                ("active", "Active"),
                                ("open", "Open"),
                            )
                        ],
                        className="indicator-bank",
                        title="Controller feedback and GUI command readiness",
                    ),
                ],
                className="instrument-body",
            ),
            html.Div(
                [
                    html.Span("POSITION", className="state-label"),
                    html.Strong(
                        "Unknown", id=f"shutter-state{suffix}", className="shutter-state is-unknown"
                    ),
                    html.Span("MODE", className="state-label"),
                    html.Strong("Unknown", id=f"operating-mode{suffix}", className="mode-readback"),
                ],
                className="state-display",
            ),
            html.P(
                "Key / interlock: unknown", id=f"safeguards{suffix}", className="note safeguards"
            ),
            html.P(
                "Connect this shutter to enable controls.",
                id=f"control-hint{suffix}",
                className="control-hint",
            ),
            _message("No action yet in this view.", f"message{suffix}"),
            html.Details(
                [
                    html.Summary(
                        ["Trigger settings ", html.Span("TRIG1 / TRIG2", className="note")]
                    ),
                    html.Div(
                        [
                            _readout(
                                "Controller readback",
                                html.Span("Unknown", id=f"ttl-status{suffix}"),
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Label(
                                                f"TRIG{port} direction",
                                                htmlFor=f"trig{port}-mode{suffix}",
                                            ),
                                            dcc.Dropdown(
                                                id=f"trig{port}-mode{suffix}",
                                                options=["disabled", "input", "output"],
                                                value="input" if port == 1 else "output",
                                                clearable=False,
                                            ),
                                            html.Label(
                                                f"TRIG{port} active polarity",
                                                htmlFor=f"trig{port}-polarity{suffix}",
                                            ),
                                            dcc.Dropdown(
                                                id=f"trig{port}-polarity{suffix}",
                                                options=["high", "low"],
                                                value="high",
                                                clearable=False,
                                            ),
                                        ],
                                        className="ttl-port",
                                    )
                                    for port in (1, 2)
                                ],
                                className="ttl-grid",
                            ),
                            html.Div(
                                [
                                    html.Button(
                                        "Read TTL settings", id=f"read-ttl{suffix}", disabled=True
                                    ),
                                    html.Button(
                                        "Apply TTL settings", id=f"apply-ttl{suffix}", disabled=True
                                    ),
                                    html.Button("Arm TTL", id=f"arm-ttl{suffix}", disabled=True),
                                    html.Button(
                                        "Disarm / Close", id=f"disarm-ttl{suffix}", disabled=True
                                    ),
                                ],
                                className="connection-actions",
                            ),
                            html.P(
                                "Selections are drafts until Apply. Read replaces drafts. "
                                "Apply requires Disarm/Close. Arm uses device readback "
                                "and may open immediately. An open input is LOW; "
                                "active-low can open with no cable. "
                                "Close requests Inactive; Disarm also selects Manual.",
                                className="note",
                            ),
                        ],
                        className="ttl-content",
                    ),
                ],
                id=f"trigger-settings{suffix}",
                className="trigger-settings",
                open=False,
            ),
        ],
        className="panel status-panel",
    )


def create_app(
    hub: ShutterHub,
    *,
    on_shutdown: Callable[[], None] | None = None,
) -> Dash:
    """Build passive panels; an owning server may supply its stop notification."""
    if not isinstance(hub, ShutterHub):
        raise TypeError("create_app requires a ShutterHub.")
    count = len(hub.controllers)
    single = count == 1
    suffixes = [""] if single else [f"-{slot + 1}" for slot in range(count)]
    last_ttl_settings = [None] * count  # Display only; Arm always reads device settings.
    discovered_routes = {}  # Only successful discovery supplies automatic routes.
    discovery_attempted = False
    app = Dash(__name__)
    app.title = "Shutter control"
    app_class = "app" if single else "app multi-app"
    app.layout = html.Main(
        [
            html.Header(
                [
                    html.Div(
                        [
                            html.P("INSTRUMENT CONTROL", className="eyebrow"),
                            html.H1("Shutter control"),
                            html.P(
                                "KSC101 controllers · USB / Ethernet LAN",
                                className="subtitle",
                                id="transport-summary",
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Button(
                                "Discover",
                                id="discover",
                                title="Find USB and Ethernet controllers using config.py defaults",
                            ),
                            html.Button(
                                "Close & disconnect all",
                                id="shutdown-all",
                                className="shutdown-button",
                            ),
                            *(
                                [html.Button("Shut down GUI & devices", id="stop-server")]
                                if on_shutdown is not None
                                else []
                            ),
                        ],
                        className="hub-actions",
                    ),
                ]
            ),
            html.Div(
                [
                    html.Span(f"0 of {count} connected", id="connection-summary"),
                    html.Span("Status auto-refreshes", className="note"),
                    html.Span(
                        "Communicating with controller…",
                        className="activity",
                        **{"aria-hidden": "true"},
                    ),
                ],
                className="session-bar",
            ),
            _message("Discovery and connection start only when requested.", "hub-message"),
            html.Div(
                [
                    _panel(
                        slot,
                        shutter.serial_number,
                        [shutter.serial_number] if shutter.serial_number else [],
                        suffixes[slot],
                        hub.ethernet_endpoints[slot],
                    )
                    for slot, shutter in enumerate(hub.controllers)
                ],
                className="shutter-grid",
            ),
            html.P(
                "Reported state does not independently verify optical shutter operation. "
                "Closing this browser tab does not shut down any controller. "
                "Close & disconnect all attempts cleanup for every connected shutter; "
                "verify physical closure independently.",
                className="note footer-note",
            ),
            dcc.Interval(id="refresh", interval=1000),
        ],
        id="shutter-app",
        className=app_class,
        **{"aria-busy": "false"},
    )

    fields = [
        ("connection", "children"),
        ("identity", "children"),
        ("shutter-state", "children"),
        ("safeguards", "children"),
        ("message", "children"),
        ("serial", "options"),
        ("serial", "value"),
        ("serial", "disabled"),
        ("connect", "disabled"),
        ("disconnect", "disabled"),
        ("open", "disabled"),
        ("close", "disabled"),
        ("ttl-status", "children"),
        ("apply-ttl", "disabled"),
        ("read-ttl", "disabled"),
        ("arm-ttl", "disabled"),
        ("disarm-ttl", "disabled"),
        ("trig1-mode", "value"),
        ("trig1-polarity", "value"),
        ("trig2-mode", "value"),
        ("trig2-polarity", "value"),
        ("connection", "className"),
        ("shutter-state", "className"),
        ("control-hint", "children"),
        ("message", "className"),
    ]
    fields += [
        ("operating-mode", "children"),
        ("open", "children"),
        ("close", "children"),
        ("open", "className"),
        ("close", "className"),
    ]
    fields += [(f"lamp-{key}", "children") for key in ("key", "ready", "error", "active", "open")]
    fields += [
        (f"mode-{mode}", prop)
        for mode, _ in MODES
        for prop in ("className", "disabled", "aria-pressed")
    ]
    fields += [("transport", "children")]
    actions = {
        f"{action}{suffix}": (slot, action)
        for slot, suffix in enumerate(suffixes)
        for action in (
            "connect",
            "disconnect",
            "open",
            "close",
            "apply-ttl",
            "read-ttl",
            "arm-ttl",
            "disarm-ttl",
            *(f"mode-{mode}" for mode, _ in MODES),
        )
    }

    @app.callback(
        [
            Output("hub-message", "children"),
            Output("connection-summary", "children"),
            Output("hub-message", "className"),
        ]
        + [Output(f"{name}{suffix}", prop) for suffix in suffixes for name, prop in fields],
        inputs={
            "_events": [
                Input("discover", "n_clicks"),
                Input("shutdown-all", "n_clicks"),
                Input("refresh", "n_intervals"),
            ]
            + ([Input("stop-server", "n_clicks")] if on_shutdown is not None else [])
            + [Input(name, "n_clicks") for name in actions],
            "selections": [State(f"serial{suffix}", "value") for suffix in suffixes],
            "ttl_drafts": [
                [
                    State(f"trig{port}-{prop}{suffix}", "value")
                    for port in (1, 2)
                    for prop in ("mode", "polarity")
                ]
                for suffix in suffixes
            ],
        },
        running=[
            (Output("refresh", "disabled"), True, False),
            (Output("shutter-app", "className"), app_class + " is-busy", app_class),
            (Output("shutter-app", "aria-busy"), "true", "false"),
        ],
    )
    def update(_events, selections, ttl_drafts):
        nonlocal discovered_routes, discovery_attempted
        with hub.lock:
            messages = [no_update] * count
            options = [no_update] * count
            selected = [no_update] * count
            drafts = [[no_update] * 4 for _ in range(count)]
            hub_message = no_update
            action = ctx.triggered_id
            slot = None
            error_slots = set()
            hub_error = False
            try:
                if action == "discover":
                    discovery_attempted = True
                    discovered_routes = {}
                    discovered_routes, warnings = hub.discover_available()
                    for index, shutter in enumerate(hub.controllers):
                        routes = dict(discovered_routes)
                        if hub.get_operating_status(index).has_device:
                            routes[shutter.serial_number] = hub.ethernet_endpoints[index]
                            selected[index] = shutter.serial_number
                        else:
                            selected[index] = (
                                selections[index]
                                if selections[index] in routes
                                else (next(iter(routes)) if single and len(routes) == 1 else None)
                            )
                        options[index] = _device_options(routes)
                    noun = "controller" if len(discovered_routes) == 1 else "controllers"
                    hub_message = (
                        f"Found {len(discovered_routes)} USB / Ethernet {noun}. "
                        "Select a device, then Connect."
                    )
                    if warnings:
                        hub_message += " " + " ".join(warnings)
                        hub_error = True
                elif action == "stop-server" and on_shutdown is not None:
                    hub.safe_shutdown()
                    on_shutdown()
                    hub_message = (
                        "Devices released; GUI server shutting down. Verify physical closure."
                    )
                elif action == "shutdown-all":
                    had_devices = [c.get_cached_status().has_device for c in hub.controllers]
                    hub.safe_shutdown()
                    hub_message = "Shutdown attempts completed. Check each shutter's status."
                    messages = [
                        "Close command sent; disconnected. Verify physical closure."
                        if had_device
                        else no_update
                        for had_device in had_devices
                    ]
                elif action in actions:
                    slot, command = actions[action]
                    shutter = hub.controllers[slot]
                    if command == "connect":
                        serial = selections[slot]
                        if discovery_attempted and serial not in discovered_routes:
                            raise ShutterError("Discover and select a currently available device.")
                        if serial in discovered_routes:
                            endpoint = discovered_routes[serial]
                            if endpoint != hub.ethernet_endpoints[slot]:
                                hub.configure_slot(slot, ethernet_endpoint=endpoint)
                                shutter = hub.controllers[slot]
                                last_ttl_settings[slot] = None
                                drafts[slot] = ["input", "high", "output", "high"]
                        status = hub.connect(slot, serial)
                        selected[slot] = status.serial_number
                        last_ttl_settings[slot] = hub.get_trigger_config(slot)
                        messages[slot] = "Connected."
                    elif command == "disconnect":
                        hub.disconnect(slot)
                        messages[slot] = (
                            "Close command sent; disconnected. Verify physical closure."
                        )
                    elif command.startswith("mode-"):
                        status = hub.get_operating_status(slot)
                        if not _mode_ready(status):
                            raise ShutterError(
                                "Stop/Close and verify Inactive/Closed before changing mode."
                            )
                        mode = command.removeprefix("mode-")
                        hub.set_operating_mode(slot, mode)
                        messages[slot] = f"{dict(MODES)[mode]} mode command sent."
                    elif command in ("open", "close"):
                        if command == "open":
                            status = hub.get_operating_status(slot)
                            config = None
                            if status.operating_mode == "triggered":
                                config = hub.get_trigger_config(slot)
                                last_ttl_settings[slot] = config
                            if not _action_ready(status, config):
                                raise ShutterError(
                                    "Open refused: verify feedback, key and input settings; "
                                    "timed modes require Inactive/Closed."
                                )
                        timed_action = shutter.get_cached_status().operating_mode in (
                            "single",
                            "auto",
                            "triggered",
                        )
                        getattr(hub, f"{command}_shutter")(slot)
                        label = command.title()
                        if timed_action:
                            label = "Start" if command == "open" else "Stop"
                        messages[slot] = f"{label} command sent."
                    elif command == "apply-ttl":
                        if not hub.get_operating_status(slot).is_closed_manual:
                            raise ShutterError("Disarm/Close before configuring TTL.")
                        requested = TriggerConfig(*ttl_drafts[slot])
                        hub.configure_triggers(slot, requested)
                        last_ttl_settings[slot] = hub.get_trigger_config(slot)
                        if last_ttl_settings[slot] != requested:
                            raise ShutterError("TTL readback mismatch; settings not confirmed.")
                        messages[slot] = "TTL settings applied and read back; disarmed."
                    elif command == "read-ttl":
                        config = hub.get_trigger_config(slot)
                        last_ttl_settings[slot] = config
                        drafts[slot] = [
                            config.trig1_mode,
                            config.trig1_polarity,
                            config.trig2_mode,
                            config.trig2_polarity,
                        ]
                        messages[slot] = "TTL settings read; draft selections replaced."
                    elif command == "arm-ttl":
                        status = hub.get_status(slot)
                        config = status.trigger_config
                        if config is not None and "input" not in (
                            config.trig1_mode,
                            config.trig2_mode,
                        ):
                            raise ShutterError("Arm refused: configure at least one trigger input.")
                        if not _arm_ready(status, config):
                            raise ShutterError("Arm refused: verify Closed/Manual, key and input.")
                        hub.arm_triggers(slot)
                        messages[slot] = "TTL arm command sent. Input controls shutter."
                    elif command == "disarm-ttl":
                        hub.disarm_triggers(slot)
                        messages[slot] = "Disarm / Close command sent."
            except (ShutterError, ValueError) as exc:
                if slot is None:
                    hub_message = str(exc)
                    hub_error = True
                else:
                    messages[slot] = str(exc)
                    error_slots.add(slot)

            # Setters send commands only. Explicitly read the selected panel's
            # feedback here; unrelated panels keep their previous observations.
            statuses = [
                shutter.get_operating_status()
                if action == "refresh"
                or action is None
                or (index == slot and index not in error_slots)
                else shutter.get_cached_status()
                for index, shutter in enumerate(hub.controllers)
            ]
            connected_count = sum(s.connection == "connected" for s in statuses)
            result = [
                hub_message,
                f"{connected_count} of {count} connected",
                "message message-error"
                if hub_error
                else ("message" if hub_message is not no_update else no_update),
            ]
            for index, status in enumerate(statuses):
                if status.error:
                    messages[index] = status.error
                    error_slots.add(index)
                connected, active = status.connection == "connected", status.has_device
                identity = (
                    " / ".join(v for v in (status.description, status.serial_number) if v)
                    or "Unknown"
                )
                if not connected:
                    last_ttl_settings[index] = None
                elif status.trigger_config is not None:
                    last_ttl_settings[index] = status.trigger_config
                config = last_ttl_settings[index]
                ttl = "Unknown"
                if not connected:
                    hint = (
                        "Resolve the connection fault before Open."
                        if status.error
                        else ("Select a controller, then Connect to enable manual controls.")
                    )
                elif status.key_enabled is None:
                    hint = "Controller key feedback is unknown; Open is unavailable."
                elif not status.key_enabled:
                    hint = "Unlock the controller key to enable Open."
                elif (
                    status.operating_mode in ("single", "auto", "triggered")
                    and status.operating_state == "active"
                ):
                    hint = (
                        f"{dict(MODES)[status.operating_mode]} active. "
                        "Use Stop before changing mode."
                    )
                elif not _action_ready(status, config):
                    hint = (
                        "Operating feedback is unknown or not ready; "
                        "Stop/Close before Start or mode selection."
                    )
                else:
                    mode_name = dict(MODES).get(status.operating_mode, "Manual")
                    detail = (
                        "Trigger may open immediately."
                        if status.operating_mode == "triggered"
                        else "Start uses stored cycle settings."
                        if status.operating_mode in ("single", "auto")
                        else "Open/Close preserve Manual mode."
                    )
                    hint = f"{mode_name} ready. Users manage the physical interlock. {detail}"
                if config is not None:
                    armed = {True: "Armed", False: "Disarmed", None: "Unknown"}[status.ttl_armed]
                    ttl = (
                        f"{armed} · {status.operating_mode}/{status.operating_state} · "
                        "TTL settings last read: "
                        f"TRIG1 {config.trig1_mode}/{config.trig1_polarity} · "
                        f"TRIG2 {config.trig2_mode}/{config.trig2_polarity}"
                    )

                result.extend(
                    [
                        status.connection.title(),
                        identity,
                        status.shutter_state.title(),
                        f"Key: {_enabled(status.key_enabled)} · "
                        f"Interlock: {_enabled(status.interlock_enabled)}",
                        messages[index],
                        options[index],
                        selected[index],
                        active,
                        active,
                        not active,
                        not _action_ready(status, config),
                        not active,
                        ttl,
                        not status.is_closed_manual,
                        not connected,
                        not _arm_ready(status, config),
                        not active,
                        *drafts[index],
                        "badge "
                        + (
                            "online"
                            if connected
                            else ("fault" if status.connection == "fault" else "offline")
                        ),
                        "shutter-state is-" + status.shutter_state,
                        hint,
                        (
                            "message message-error"
                            if index in error_slots
                            else "message message-success"
                        )
                        if messages[index] is not no_update
                        else no_update,
                    ]
                )
                timed = status.operating_mode in ("single", "auto", "triggered")
                result.extend(
                    [
                        dict(MODES).get(status.operating_mode, "Unknown"),
                        "Start" if timed else "Open",
                        "Stop" if timed else "Close",
                        "action-control start-control" + ("" if timed else " manual-control"),
                        "action-control stop-control" + ("" if timed else " manual-control"),
                        _lamp(status.key_enabled),
                        _lamp(_action_ready(status, config) if connected else None),
                        _lamp(bool(status.error), error=True),
                        _lamp(
                            status.operating_state == "active"
                            if connected and status.operating_state != "unknown"
                            else None
                        ),
                        _lamp(
                            status.shutter_state == "open"
                            if connected and status.shutter_state != "unknown"
                            else None
                        ),
                    ]
                )
                for mode, _ in MODES:
                    chosen = status.operating_mode == mode
                    result.extend(
                        [
                            "mode-button" + (" selected" if chosen else ""),
                            not _mode_ready(status),
                            "true" if chosen else "false",
                        ]
                    )
                serial = selected[index] if selected[index] is not no_update else selections[index]
                endpoint = hub.ethernet_endpoints[index]
                if not active and serial in discovered_routes:
                    endpoint = discovered_routes[serial]
                result.append(_route_label(endpoint))
            return result

    return app
