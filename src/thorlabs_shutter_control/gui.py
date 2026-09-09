"""Local single-operator Dash UI; every device action goes through the controller."""

from pathlib import Path

from dash import Dash, Input, Output, State, ctx, dcc, html, no_update

from .controller import KSC101Controller, ShutterError


def create_app(controller: KSC101Controller) -> Dash:
    app = Dash(__name__, assets_folder=str(Path(__file__).with_name("assets")))
    app.title = "Shutter control"
    initial_serial = controller.serial_number
    app.layout = html.Main(
        [
            html.Header(
                [
                    html.P("LAB CONTROL", className="eyebrow"),
                    html.H1("Shutter control"),
                    html.P("Thorlabs KSC101", className="subtitle"),
                ]
            ),
            html.Section(
                [
                    html.Label("Device serial number", htmlFor="serial"),
                    dcc.Dropdown(
                        id="serial",
                        options=[initial_serial] if initial_serial else [],
                        value=initial_serial,
                        placeholder="Discover devices, or connect the only attached controller",
                    ),
                    html.Div(
                        [
                            html.Button("Discover", id="discover", n_clicks=0),
                            html.Button("Connect", id="connect", n_clicks=0),
                            html.Button(
                                "Close & disconnect", id="disconnect", n_clicks=0, disabled=True
                            ),
                        ],
                        className="connection-actions",
                    ),
                ],
                className="panel",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.Span("Connection", className="label"),
                            html.Strong("Disconnected", id="connection"),
                        ]
                    ),
                    html.Div(
                        [
                            html.Span("Device identity", className="label"),
                            html.Span("Unknown", id="identity"),
                        ]
                    ),
                    html.Div(
                        [
                            html.Span("Shutter state · controller reported", className="label"),
                            html.Strong("Unknown", id="shutter-state", className="shutter-state"),
                        ]
                    ),
                    html.P(
                        "Reported state does not independently verify optical shutter operation.",
                        className="note",
                    ),
                    html.P("Key / interlock: unknown", id="safeguards", className="note"),
                    html.Div(
                        [
                            html.Button(
                                "Open", id="open", n_clicks=0, disabled=True, className="primary"
                            ),
                            html.Button("Close", id="close", n_clicks=0, disabled=True),
                        ],
                        className="shutter-actions",
                    ),
                ],
                className="panel status-panel",
            ),
            html.Div(
                "Discover a device to begin.",
                id="message",
                role="status",
                **{"aria-live": "polite"},
            ),
            html.P(
                "Close & disconnect attempts to close the shutter before releasing it. "
                "Closing this browser tab does not shut down the controller.",
                className="note",
            ),
            dcc.Interval(id="refresh", interval=1000, n_intervals=0),
        ],
        className="app",
    )

    @app.callback(
        Output("connection", "children"),
        Output("identity", "children"),
        Output("shutter-state", "children"),
        Output("safeguards", "children"),
        Output("message", "children"),
        Output("serial", "options"),
        Output("serial", "value"),
        Output("serial", "disabled"),
        Output("discover", "disabled"),
        Output("connect", "disabled"),
        Output("disconnect", "disabled"),
        Output("open", "disabled"),
        Output("close", "disabled"),
        Input("discover", "n_clicks"),
        Input("connect", "n_clicks"),
        Input("disconnect", "n_clicks"),
        Input("open", "n_clicks"),
        Input("close", "n_clicks"),
        Input("refresh", "n_intervals"),
        State("serial", "value"),
        prevent_initial_call=False,
        running=[(Output("refresh", "disabled"), True, False)],
    )
    def update(_discover, _connect, _disconnect, _open, _close, _refresh, serial):
        options, selected, message = no_update, no_update, no_update
        try:
            action = ctx.triggered_id
            if action == "discover":
                serials = controller.discover()
                options = serials
                selected = (
                    serial if serial in serials else (serials[0] if len(serials) == 1 else None)
                )
                message = f"Found {len(serials)} device(s)."
            elif action == "connect":
                status = controller.connect(serial)
                selected = status.serial_number
                options = [status.serial_number]
                message = "Connected."
            elif action == "disconnect":
                controller.safe_shutdown()
                message = "Close completed with controller feedback; disconnected."
            elif action == "open":
                controller.open_shutter()
                message = "Open completed with controller feedback."
            elif action == "close":
                controller.close_shutter()
                message = "Close completed with controller feedback."
        except ShutterError as exc:
            message = str(exc)
        status = controller.get_status()
        if status.error:
            message = status.error
        connected = status.connection == "connected"
        active = status.has_device
        identity = (
            " / ".join(v for v in (status.description, status.serial_number) if v) or "Unknown"
        )

        def enabled(value):
            return "unknown" if value is None else ("enabled" if value else "not enabled")

        safeguards = (
            f"Key: {enabled(status.key_enabled)} · Interlock: {enabled(status.interlock_enabled)}"
        )
        return (
            status.connection.title(),
            identity,
            status.shutter_state.title(),
            safeguards,
            message,
            options,
            selected,
            active,
            active,
            active,
            not active,
            not (connected and status.key_enabled and status.interlock_enabled),
            not active,
        )

    return app
