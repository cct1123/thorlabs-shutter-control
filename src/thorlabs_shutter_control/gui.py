"""Small optional local GUI using the same active owner as library and CLI."""

import json
from dataclasses import asdict


def create_app(hub):
    from dash import Dash, Input, Output, State, ctx, dcc, html

    app = Dash(__name__)
    app.layout = html.Main(
        [
            html.H1("KSC101 direct control"),
            html.P("Electrical readback is not an optical observation. No automatic connection."),
            html.P(
                "Connect reads the current mode and electrical output. Before ON, keep Manual "
                "selected and wait the configured minimum OFF interval."
            ),
            dcc.Dropdown(id="target", options=[c.name for c in hub.configs], clearable=False),
            html.Div(
                [
                    html.Button(label, id=key)
                    for key, label in (
                        ("connect", "Connect exact route"),
                        ("read", "Read state"),
                        ("manual", "Set Manual (remembered at power-up)"),
                        ("on", "Solenoid ON"),
                        ("off", "Cancel / qualified OFF"),
                        ("release", "Release communication"),
                    )
                ]
            ),
            html.Pre("Select a configured target.", id="result"),
        ],
        style={"maxWidth": "900px", "margin": "3rem auto", "fontFamily": "sans-serif"},
    )

    def connect(target):
        hub.connect(target)
        return hub.get_status(target)  # Show fresh feedback and begin observed OFF rest.

    @app.callback(
        Output("result", "children"),
        [Input(key, "n_clicks") for key in ("connect", "read", "manual", "on", "off", "release")],
        State("target", "value"),
        prevent_initial_call=True,
    )
    def act(*values):
        target = values[-1]
        try:
            if target not in {c.name for c in hub.configs}:
                raise ValueError("Select an exact configured target before using a control")
            method = {
                "connect": connect,
                "read": hub.get_status,
                "manual": hub.set_manual_mode,
                "on": lambda name: hub.set_solenoid(name, True),
                "off": hub.safe_state,
                "release": hub.disconnect,
            }[ctx.triggered_id]
            result = method(target)
            return (
                json.dumps(asdict(result), indent=2)
                if result
                else ("Communication released; optical state unknown.")
            )
        except Exception as exc:
            return "Unconfirmed: " + str(exc) + "\n" + "\n".join(getattr(exc, "__notes__", []))

    return app


def run(hub, *, port=8050):
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("WebUI port must be an integer in 1..65535")
    app = create_app(hub)
    original = None
    try:
        # Threaded requests keep protective OFF reachable during an active query.
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
