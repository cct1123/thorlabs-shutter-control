"""Local single-operator Dash UI for configured independently owned shutters."""

from dash import Dash, Input, Output, State, ctx, dcc, html, no_update

from .controller import KCubeShutter, ShutterError, ShutterHub, TriggerConfig


def _message(text, component_id):
    return html.Div(
        text, id=component_id, role="status", className="message", **{"aria-live": "polite"}
    )


def _readout(label, value):
    return html.Div([html.Span(label, className="label"), value])


def _enabled(value):
    return "unknown" if value is None else ("enabled" if value else "not enabled")


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


def _panel(slot, serial_number, serials, suffix):
    return html.Section(
        [
            html.Div(
                [
                    html.H2(f"Shutter {slot + 1}"),
                    html.Span("Disconnected", id=f"connection{suffix}", className="badge offline"),
                ],
                className="panel-heading",
            ),
            html.Label("Device serial number", htmlFor=f"serial{suffix}"),
            dcc.Dropdown(
                id=f"serial{suffix}",
                options=serials,
                value=serial_number,
                placeholder="Discover, then select a controller",
            ),
            html.Div(
                [
                    html.Button("Connect", id=f"connect{suffix}", className="connect-button"),
                    html.Button(
                        "Close & disconnect",
                        id=f"disconnect{suffix}",
                        disabled=True,
                        title="Send Close and release this controller connection",
                    ),
                ],
                className="connection-actions",
            ),
            html.P("No controller connected", id=f"identity{suffix}", className="device-identity"),
            html.Div(
                [
                    html.Span("Shutter · controller reported", className="state-label"),
                    html.Strong(
                        "Unknown", id=f"shutter-state{suffix}", className="shutter-state is-unknown"
                    ),
                    html.P("Key / interlock: unknown", id=f"safeguards{suffix}", className="note"),
                ],
                className="state-display",
            ),
            html.Div(
                [
                    html.Button(
                        "Open",
                        id=f"open{suffix}",
                        disabled=True,
                        **{"aria-describedby": f"control-hint{suffix}"},
                    ),
                    html.Button("Close", id=f"close{suffix}", disabled=True, className="primary"),
                ],
                className="shutter-actions",
            ),
            html.P(
                "Connect this shutter to enable manual controls.",
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


def create_app(controller: KCubeShutter | ShutterHub | None = None) -> Dash:
    """Build passive panels for the supplied hub, defaulting to three slots."""
    hub = (
        controller
        if isinstance(controller, ShutterHub)
        else ShutterHub(controllers=[controller] if controller is not None else None)
    )
    count = len(hub.controllers)
    single = count == 1
    suffixes = [""] if single else [f"-{slot + 1}" for slot in range(count)]
    serials = [c.serial_number for c in hub.controllers if c.serial_number]
    transports = {"Ethernet" if endpoint else "USB" for endpoint in hub.ethernet_endpoints}
    transport_label = " / ".join(sorted(transports))
    last_ttl_settings = [None] * count  # Display only; Arm always reads device settings.
    app = Dash(__name__)
    app.title = "Shutter control"
    app_class = "app" if single else "app multi-app"
    app.layout = html.Main(
        [
            html.Header(
                [
                    html.Div(
                        [
                            html.P("OPTICS / LAB CONTROL", className="eyebrow"),
                            html.H1("Shutter control"),
                            html.P(f"KSC101 controllers · {transport_label}", className="subtitle"),
                        ]
                    ),
                    html.Div(
                        [
                            html.Button(
                                "Discover",
                                id="discover",
                                title="Find controllers on configured transports",
                            ),
                            html.Button(
                                "Close & disconnect all",
                                id="shutdown-all",
                                className="shutdown-button",
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
                    _panel(slot, shutter.serial_number, serials, suffixes[slot])
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
                    serials = hub.discover()
                    for index, shutter in enumerate(hub.controllers):
                        options[index] = serials
                        if shutter.get_operating_status().has_device:
                            # A discovery snapshot may omit a retained/lost device. Keep
                            # its identity visible until cleanup actually releases it.
                            selected[index] = shutter.serial_number
                            options[index] = sorted(set(serials + [shutter.serial_number]))
                            continue
                        # Never assign the same sole device to multiple slots automatically.
                        selected[index] = (
                            selections[index]
                            if selections[index] in serials
                            else (serials[0] if single and len(serials) == 1 else None)
                        )
                    noun = "controller" if len(serials) == 1 else "controllers"
                    hub_message = (
                        f"Found {len(serials)} {transport_label} {noun}. "
                        "Select a serial, then Connect."
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
                        status = (
                            shutter.connect(selections[slot])
                            if isinstance(controller, KCubeShutter)
                            else hub.connect(slot, selections[slot])
                        )
                        selected[slot] = status.serial_number
                        last_ttl_settings[slot] = hub.get_trigger_config(slot)
                        messages[slot] = "Connected."
                    elif command == "disconnect":
                        hub.disconnect(slot)
                        messages[slot] = (
                            "Close command sent; disconnected. Verify physical closure."
                        )
                    elif command in ("open", "close"):
                        if command == "open":
                            status = hub.get_operating_status(slot)
                            if not _open_ready(status):
                                raise ShutterError(
                                    "Open refused: verify feedback, key and disarm TTL."
                                )
                        getattr(hub, f"{command}_shutter")(slot)
                        messages[slot] = f"{command.title()} command sent."
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
                elif status.operating_mode == "triggered":
                    hint = "Use Disarm / Close before manual Open."
                elif status.key_enabled is None:
                    hint = "Controller key feedback is unknown; Open is unavailable."
                elif not status.key_enabled:
                    hint = "Unlock the controller key to enable Open."
                elif not _open_ready(status):
                    hint = (
                        "Operating feedback is unknown or mode is not Manual; use Disarm / Close."
                    )
                else:
                    hint = (
                        "Manual control ready. Users manage the physical interlock. "
                        "Use Disarm / Close to return to Manual."
                    )
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
                        f"Interlock: {_enabled(status.interlock_enabled)}"
                        + (" (operator verified)" if status.operator_interlock_confirmed else ""),
                        messages[index],
                        options[index],
                        selected[index],
                        active,
                        active,
                        not active,
                        not _open_ready(status),
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
            return result

    return app
