"""Local single-operator Dash UI for up to three independently owned shutters."""

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


def _panel(slot, serial_number, serials, suffix):
    return html.Section(
        [
            html.H2(f"Shutter {slot + 1}"),
            html.Label("Device serial number", htmlFor=f"serial{suffix}"),
            dcc.Dropdown(
                id=f"serial{suffix}",
                options=serials,
                value=serial_number,
                placeholder="Discover and select this shutter's serial",
            ),
            html.Div(
                [
                    html.Button("Connect", id=f"connect{suffix}"),
                    html.Button("Close & disconnect", id=f"disconnect{suffix}", disabled=True),
                ],
                className="connection-actions",
            ),
            _readout("Connection", html.Strong("Disconnected", id=f"connection{suffix}")),
            _readout("Device identity", html.Span("Unknown", id=f"identity{suffix}")),
            _readout(
                "Shutter state · controller reported",
                html.Strong("Unknown", id=f"shutter-state{suffix}", className="shutter-state"),
            ),
            html.P("Key / interlock: unknown", id=f"safeguards{suffix}", className="note"),
            html.Div(
                [
                    html.Button("Open", id=f"open{suffix}", disabled=True, className="primary"),
                    html.Button("Close", id=f"close{suffix}", disabled=True),
                ],
                className="shutter-actions",
            ),
            html.H3("TTL · TRIG1 / TRIG2"),
            _readout("Controller readback", html.Span("Unknown", id=f"ttl-status{suffix}")),
            *[
                html.Div(
                    [
                        html.Label(f"TRIG{port} direction", htmlFor=f"trig{port}-mode{suffix}"),
                        dcc.Dropdown(
                            id=f"trig{port}-mode{suffix}",
                            options=["disabled", "input", "output"],
                            value="input" if port == 1 else "output",
                            clearable=False,
                        ),
                        html.Label(
                            f"TRIG{port} active polarity", htmlFor=f"trig{port}-polarity{suffix}"
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
            html.Div(
                [
                    html.Button("Apply TTL settings", id=f"apply-ttl{suffix}", disabled=True),
                    html.Button("Read TTL settings", id=f"read-ttl{suffix}", disabled=True),
                    html.Button("Arm TTL", id=f"arm-ttl{suffix}", disabled=True),
                    html.Button("Disarm / Close", id=f"disarm-ttl{suffix}", disabled=True),
                ],
                className="connection-actions",
            ),
            html.P(
                "Selections are drafts until Apply. Apply requires Disarm/Close. "
                "Arm uses device readback and may open immediately. An open input is LOW; "
                "active-low can open with no cable. Read replaces drafts. Close disarms TTL.",
                className="note",
            ),
            _message("Select a device to begin.", f"message{suffix}"),
        ],
        className="panel status-panel",
    )


def create_app(controller: KCubeShutter | ShutterHub | None = None) -> Dash:
    """Build a passive three-slot GUI, or use injected controller(s) for integration."""
    hub = (
        controller
        if isinstance(controller, ShutterHub)
        else ShutterHub(controllers=[controller] if controller is not None else None)
    )
    count = len(hub.controllers)
    single = count == 1
    suffixes = [""] if single else [f"-{slot + 1}" for slot in range(count)]
    serials = [c.serial_number for c in hub.controllers if c.serial_number]
    app = Dash(__name__)
    app.title = "Shutter control"
    app.layout = html.Main(
        [
            html.Header(
                [
                    html.P("LAB CONTROL", className="eyebrow"),
                    html.H1("Shutter control"),
                    html.P("KSC101 · up to three shutters through KEH3 USB", className="subtitle"),
                ]
            ),
            html.Div(
                [
                    html.Button("Discover", id="discover"),
                    html.Button("Close & disconnect all", id="shutdown-all"),
                ],
                className="connection-actions",
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
                className="note",
            ),
            dcc.Interval(id="refresh", interval=1000),
        ],
        className="app" if single else "app multi-app",
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
        [Output("hub-message", "children")]
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
        running=[(Output("refresh", "disabled"), True, False)],
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
            try:
                if action == "discover":
                    serials = hub.discover()
                    for index, shutter in enumerate(hub.controllers):
                        options[index] = serials
                        if shutter.get_status().has_device:
                            # A discovery snapshot may omit a retained/lost device. Keep
                            # its identity visible until cleanup actually releases it.
                            selected[index] = shutter.serial_number
                            options[index] = sorted(set(serials + [shutter.serial_number]))
                            continue
                        # Never assign the same sole device to all three slots automatically.
                        selected[index] = (
                            selections[index]
                            if selections[index] in serials
                            else (serials[0] if single and len(serials) == 1 else None)
                        )
                    hub_message = (
                        f"Found {len(serials)} device(s). Select a distinct serial per shutter."
                    )
                elif action == "shutdown-all":
                    had_devices = [c.get_status().has_device for c in hub.controllers]
                    hub.safe_shutdown()
                    hub_message = "Shutdown attempts completed. Check each shutter's status."
                    messages = [
                        "Close completed with controller feedback; disconnected."
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
                            if single
                            else hub.connect(slot, selections[slot])
                        )
                        selected[slot] = status.serial_number
                        messages[slot] = "Connected."
                    elif command == "disconnect":
                        shutter.safe_shutdown()
                        messages[slot] = "Close completed with controller feedback; disconnected."
                    elif command == "open":
                        shutter.open_shutter()
                        messages[slot] = "Open completed with controller feedback."
                    elif command == "close":
                        shutter.close_shutter()
                        messages[slot] = "Close completed with controller feedback."
                    elif command == "apply-ttl":
                        shutter.configure_triggers(TriggerConfig(*ttl_drafts[slot]))
                        messages[slot] = "TTL settings applied and read back; disarmed."
                    elif command == "read-ttl":
                        config = shutter.get_trigger_config()
                        drafts[slot] = [
                            config.trig1_mode,
                            config.trig1_polarity,
                            config.trig2_mode,
                            config.trig2_polarity,
                        ]
                        messages[slot] = "TTL settings read; draft selections replaced."
                    elif command == "arm-ttl":
                        shutter.arm_triggers()
                        messages[slot] = (
                            "TTL armed with controller feedback. Input controls shutter."
                        )
                    elif command == "disarm-ttl":
                        shutter.disarm_triggers()
                        messages[slot] = "TTL disarmed; Close completed with controller feedback."
            except (ShutterError, ValueError) as exc:
                if slot is None:
                    hub_message = str(exc)
                else:
                    messages[slot] = str(exc)

            result = [hub_message]
            for index, shutter in enumerate(hub.controllers):
                status = shutter.get_status()
                if status.error:
                    messages[index] = status.error
                connected, active = status.connection == "connected", status.has_device
                identity = (
                    " / ".join(v for v in (status.description, status.serial_number) if v)
                    or "Unknown"
                )
                config = status.trigger_config
                ttl = "Unknown"
                if config is not None:
                    armed = {True: "Armed", False: "Disarmed", None: "Unknown"}[status.ttl_armed]
                    ttl = (
                        f"{armed} · {status.operating_mode}/{status.operating_state} · "
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
                        not (
                            connected
                            and status.key_enabled
                            and status.interlock_enabled
                            and status.operating_mode != "triggered"
                        ),
                        not active,
                        ttl,
                        not (
                            connected
                            and status.operating_mode == "manual"
                            and status.operating_state == "inactive"
                            and status.shutter_state == "closed"
                        ),
                        not connected,
                        not (
                            connected
                            and config is not None
                            and status.ttl_armed is False
                            and status.key_enabled
                            and status.interlock_enabled
                            and "input" in (config.trig1_mode, config.trig2_mode)
                        ),
                        not active,
                        *drafts[index],
                    ]
                )
            return result

    return app
