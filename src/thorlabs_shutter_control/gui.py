"""Local single-operator Dash UI for configured independently owned shutters."""

from collections.abc import Callable

from dash import Dash, Input, Output, State, ctx, dcc, html, no_update

from .controller import ShutterError, ShutterHub, ShutterStatus, TriggerConfig


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


def _control_hint(status, config):
    """Explain the current command prerequisites without requesting hardware feedback."""
    if status.connection != "connected":
        if status.error:
            return "Resolve the connection fault before Open."
        return "Select a controller, then Connect to enable manual controls."
    if status.key_enabled is None:
        return "Controller key feedback is unknown; Open is unavailable."
    if not status.key_enabled:
        return "Unlock the controller key to enable Open."
    if (
        status.operating_mode in ("single", "auto", "triggered")
        and status.operating_state == "active"
    ):
        return f"{dict(MODES)[status.operating_mode]} active. Use Stop before changing mode."
    if not _action_ready(status, config):
        return (
            "Operating feedback is unknown or not ready; Stop/Close before Start or mode selection."
        )
    mode_name = dict(MODES).get(status.operating_mode, "Manual")
    if status.operating_mode == "triggered":
        detail = "Trigger may open immediately."
    elif status.operating_mode in ("single", "auto"):
        detail = "Start uses stored cycle settings."
    else:
        detail = "Open/Close preserve Manual mode."
    return f"{mode_name} ready. Users manage the physical interlock. {detail}"


def _panel_view(
    status: ShutterStatus,
    config: TriggerConfig | None,
    *,
    message=no_update,
    options=no_update,
    selected=no_update,
    draft=None,
    error=False,
    endpoint=None,
):
    """Map panel component names to browser properties; perform no device I/O.

    These names also define the callback outputs in _panel_outputs(). Add a
    readout here and in _panel(); there is no separate positional field list.
    no_update preserves a browser value, while None explicitly clears it.
    """
    connected = status.connection == "connected"
    has_handle = status.has_device
    timed = status.operating_mode in ("single", "auto", "triggered")
    if draft is None:
        draft = [no_update] * 4
    if connected:
        badge = "online"
    elif status.connection == "fault":
        badge = "fault"
    else:
        badge = "offline"
    message_class = no_update
    if message is not no_update:
        message_class = "message message-error" if error else "message message-success"
    ttl = "Unknown"
    if config is not None:
        armed = {True: "Armed", False: "Disarmed", None: "Unknown"}[status.ttl_armed]
        ttl = (
            f"{armed} · {status.operating_mode}/{status.operating_state} · "
            "TTL settings last read: "
            f"TRIG1 {config.trig1_mode}/{config.trig1_polarity} · "
            f"TRIG2 {config.trig2_mode}/{config.trig2_polarity}"
        )

    view = {
        "connection": {"children": status.connection.title(), "className": "badge " + badge},
        "identity": {
            "children": " / ".join(v for v in (status.description, status.serial_number) if v)
            or "Unknown"
        },
        "shutter-state": {
            "children": status.shutter_state.title(),
            "className": "shutter-state is-" + status.shutter_state,
        },
        "safeguards": {
            "children": f"Key: {_enabled(status.key_enabled)} · "
            f"Interlock: {_enabled(status.interlock_enabled)}"
        },
        "message": {"children": message, "className": message_class},
        "serial": {"options": options, "value": selected, "disabled": has_handle},
        "connect": {"disabled": has_handle},
        "disconnect": {"disabled": not has_handle},
        "open": {
            "disabled": not _action_ready(status, config),
            "children": "Start" if timed else "Open",
            "className": "action-control start-control" + ("" if timed else " manual-control"),
        },
        "close": {
            "disabled": not has_handle,
            "children": "Stop" if timed else "Close",
            "className": "action-control stop-control" + ("" if timed else " manual-control"),
        },
        "ttl-status": {"children": ttl},
        "apply-ttl": {"disabled": not status.is_closed_manual},
        "read-ttl": {"disabled": not connected},
        "arm-ttl": {"disabled": not _arm_ready(status, config)},
        "disarm-ttl": {"disabled": not has_handle},
        "trig1-mode": {"value": draft[0]},
        "trig1-polarity": {"value": draft[1]},
        "trig2-mode": {"value": draft[2]},
        "trig2-polarity": {"value": draft[3]},
        "control-hint": {"children": _control_hint(status, config)},
        "operating-mode": {"children": dict(MODES).get(status.operating_mode, "Unknown")},
        "transport": {"children": _route_label(endpoint)},
    }
    lamps = {
        "key": status.key_enabled,
        "ready": _action_ready(status, config) if connected else None,
        "error": bool(status.error),
        "active": status.operating_state == "active"
        if connected and status.operating_state != "unknown"
        else None,
        "open": status.shutter_state == "open"
        if connected and status.shutter_state != "unknown"
        else None,
    }
    for name, value in lamps.items():
        view[f"lamp-{name}"] = {"children": _lamp(value, error=name == "error")}
    for mode, _ in MODES:
        chosen = status.operating_mode == mode
        view[f"mode-{mode}"] = {
            "className": "mode-button" + (" selected" if chosen else ""),
            "disabled": not _mode_ready(status),
            "aria-pressed": "true" if chosen else "false",
        }
    return view


def _panel_outputs(suffix):
    """Wire the named view properties to this panel's existing component IDs."""
    outputs = {}
    # Only the property names are used; rendering this empty snapshot is passive.
    for component, properties in _panel_view(ShutterStatus(), None).items():
        outputs[component] = {prop: Output(f"{component}{suffix}", prop) for prop in properties}
    return outputs


def create_app(
    hub: ShutterHub,
    *,
    on_shutdown: Callable[[], None] | None = None,
) -> Dash:
    """Build passive panels and keep one hub's GUI state in this closure.

    discover_panels() owns discovery choices; run_panel_action() owns commands;
    update() coordinates feedback and _panel_view() renders values without I/O.
    An owning server may supply a nonblocking shutdown notification.
    """
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

    def discover_panels(selections, panel_updates):
        """Remember the latest routes and populate choices without replacing held handles."""
        nonlocal discovered_routes, discovery_attempted
        hub_error = False
        discovery_attempted = True
        discovered_routes = {}
        discovered_routes, warnings = hub.discover_available()
        for index, shutter in enumerate(hub.controllers):
            routes = dict(discovered_routes)
            if hub.get_operating_status(index).has_device:
                routes[shutter.serial_number] = hub.ethernet_endpoints[index]
                panel_updates[index]["selected"] = shutter.serial_number
            elif selections[index] in routes:
                panel_updates[index]["selected"] = selections[index]
            elif single and len(routes) == 1:
                panel_updates[index]["selected"] = next(iter(routes))
            else:
                panel_updates[index]["selected"] = None
            panel_updates[index]["options"] = _device_options(routes)
        noun = "controller" if len(discovered_routes) == 1 else "controllers"
        hub_message = (
            f"Found {len(discovered_routes)} USB / Ethernet {noun}. Select a device, then Connect."
        )
        if warnings:
            hub_message += " " + " ".join(warnings)
            hub_error = True
        return hub_message, hub_error

    def run_panel_action(slot, command, serial, ttl_draft, updates) -> ShutterStatus | None:
        """Check prerequisites and issue one panel action under the caller's hub lock.

        Change only this action's browser values and last-read TTL display cache.
        Errors propagate to update(), which preserves partial updates and chooses
        whether to request result feedback. Return a snapshot when this action has
        already read its full result; None asks update() to read it as usual.
        """
        if command == "connect":
            if discovery_attempted and serial not in discovered_routes:
                raise ShutterError("Discover and select a currently available device.")
            if serial in discovered_routes:
                endpoint = discovered_routes[serial]
                if endpoint != hub.ethernet_endpoints[slot]:
                    hub.configure_slot(slot, ethernet_endpoint=endpoint)
                    last_ttl_settings[slot] = None
                    updates["draft"] = ["input", "high", "output", "high"]
            status = hub.connect(slot, serial)
            updates["selected"] = status.serial_number
            # One full snapshot shares the operating and TTL feedback wait.
            status = hub.get_status(slot)
            if status.error:
                raise ShutterError(status.error)
            last_ttl_settings[slot] = status.trigger_config
            updates["message"] = "Connected."
            return status
        elif command == "disconnect":
            hub.disconnect(slot)
            updates["message"] = "Close command sent; disconnected. Verify physical closure."
        elif command.startswith("mode-"):
            status = hub.get_operating_status(slot)
            if not _mode_ready(status):
                raise ShutterError("Stop/Close and verify Inactive/Closed before changing mode.")
            mode = command.removeprefix("mode-")
            hub.set_operating_mode(slot, mode)
            updates["message"] = f"{dict(MODES)[mode]} mode command sent."
        elif command in ("open", "close"):
            shutter = hub.controllers[slot]
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
            if command == "open":
                hub.open_shutter(slot)
            else:
                hub.close_shutter(slot)
            label = command.title()
            if timed_action:
                label = "Start" if command == "open" else "Stop"
            updates["message"] = f"{label} command sent."
        elif command == "apply-ttl":
            if not hub.get_operating_status(slot).is_closed_manual:
                raise ShutterError("Disarm/Close before configuring TTL.")
            requested = TriggerConfig(*ttl_draft)
            hub.configure_triggers(slot, requested)
            # Compare actual TTL readback and display operating feedback from one read.
            status = hub.get_status(slot)
            if status.error:
                raise ShutterError(status.error)
            last_ttl_settings[slot] = status.trigger_config
            if status.trigger_config != requested:
                raise ShutterError("TTL readback mismatch; settings not confirmed.")
            updates["message"] = "TTL settings applied and read back; disarmed."
            return status
        elif command == "read-ttl":
            config = hub.get_trigger_config(slot)
            last_ttl_settings[slot] = config
            updates["draft"] = [
                config.trig1_mode,
                config.trig1_polarity,
                config.trig2_mode,
                config.trig2_polarity,
            ]
            updates["message"] = "TTL settings read; draft selections replaced."
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
            updates["message"] = "TTL arm command sent. Input controls shutter."
        elif command == "disarm-ttl":
            hub.disarm_triggers(slot)
            updates["message"] = "Disarm / Close command sent."
        return None

    @app.callback(
        output={
            "hub_message": Output("hub-message", "children"),
            "connection_summary": Output("connection-summary", "children"),
            "hub_message_class": Output("hub-message", "className"),
            "panels": [_panel_outputs(suffix) for suffix in suffixes],
        },
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
        """Handle one event, read its feedback, then return named browser properties.

        Periodic refresh reads all panels. Other actions read only the affected
        panel after success; unrelated or failed actions keep display snapshots.
        """
        with hub.lock:
            # Each panel keeps its own action updates; no parallel positional lists.
            panel_updates = [
                {
                    "message": no_update,
                    "options": no_update,
                    "selected": no_update,
                    "draft": [no_update] * 4,
                }
                for _ in range(count)
            ]
            hub_message = no_update
            action = ctx.triggered_id
            slot = None
            action_status = None
            error_slots = set()
            hub_error = False
            try:
                if action == "discover":
                    hub_message, hub_error = discover_panels(selections, panel_updates)
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
                    for index, had_device in enumerate(had_devices):
                        if had_device:
                            panel_updates[index]["message"] = (
                                "Close command sent; disconnected. Verify physical closure."
                            )
                elif action in actions:
                    slot, command = actions[action]
                    action_status = run_panel_action(
                        slot, command, selections[slot], ttl_drafts[slot], panel_updates[slot]
                    )
            except (ShutterError, ValueError) as exc:
                if slot is None:
                    hub_message = str(exc)
                    hub_error = True
                else:
                    panel_updates[slot]["message"] = str(exc)
                    error_slots.add(slot)

            # Reuse feedback only from this event, never from a prior action.
            # Other successful panel actions still need their result read here.
            statuses = []
            for index, shutter in enumerate(hub.controllers):
                read_feedback = action in (None, "refresh") or (
                    index == slot and index not in error_slots
                )
                if index == slot and action_status is not None:
                    statuses.append(action_status)
                elif read_feedback:
                    statuses.append(shutter.get_operating_status())
                else:
                    statuses.append(shutter.get_cached_status())
            if hub_error:
                hub_message_class = "message message-error"
            elif hub_message is no_update:
                hub_message_class = no_update
            else:
                hub_message_class = "message"
            connected_count = sum(s.connection == "connected" for s in statuses)
            result = {
                "hub_message": hub_message,
                "connection_summary": f"{connected_count} of {count} connected",
                "hub_message_class": hub_message_class,
                "panels": [],
            }
            for index, status in enumerate(statuses):
                if status.error:
                    panel_updates[index]["message"] = status.error
                    error_slots.add(index)
                if status.connection != "connected":
                    last_ttl_settings[index] = None
                elif status.trigger_config is not None:
                    last_ttl_settings[index] = status.trigger_config
                serial = panel_updates[index]["selected"]
                if serial is no_update:
                    serial = selections[index]
                endpoint = hub.ethernet_endpoints[index]
                if not status.has_device and serial in discovered_routes:
                    endpoint = discovered_routes[serial]
                result["panels"].append(
                    _panel_view(
                        status,
                        last_ttl_settings[index],
                        error=index in error_slots,
                        endpoint=endpoint,
                        **panel_updates[index],
                    )
                )
            return result

    return app
