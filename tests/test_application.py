"""The maintained launcher and GUI workflows through real Dash callback HTTP."""

from contextlib import contextmanager
from types import SimpleNamespace

from thorlabs_shutter_control import ShutterHub, gui
from thorlabs_shutter_control import __main__ as launcher


def click(app, action, serial=None):
    key, callback = next(iter(app.callback_map.items()))
    states = []
    for item in callback["state"]:
        name = item["id"]
        value = (
            serial
            if name == "serial"
            else ("high" if "polarity" in name else "input" if "trig1" in name else "output")
        )
        states.append(dict(item, value=value))
    response = app.server.test_client().post(
        "/_dash-update-component",
        json={
            "output": key,
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


def test_gui_discovers_and_connects_the_selected_lan_route(bench):
    hub = ShutterHub(slots=1)
    app = gui.create_app(hub)
    assert not bench.loads
    found = click(app, "discover")
    assert len(found["serial"]["options"]) == 2
    assert not bench.lan.IsConnected
    connected = click(app, "connect", bench.lan.serial)
    assert connected["connection"]["children"] == "Connected"
    assert connected["serial"]["disabled"]
    assert hub.ethernet_endpoints == (bench.endpoint,)
    click(app, "disconnect", bench.lan.serial)
    assert not bench.lan.IsConnected


def test_gui_operates_four_modes_and_stops_the_owned_server(bench):
    stopped = []
    app = gui.create_app(ShutterHub(slots=1), on_shutdown=lambda: stopped.append(True))
    click(app, "connect", bench.usb.serial)
    for mode in ("manual", "single", "auto", "triggered"):
        selected = click(app, f"mode-{mode}", bench.usb.serial)
        assert selected[f"mode-{mode}"]["aria-pressed"] == "true"
        started = click(app, "open", bench.usb.serial)
        assert started["open"]["children"] == ("Open" if mode == "manual" else "Start")
        assert bench.usb.operation == "Active"
        click(app, "close", bench.usb.serial)
        assert bench.usb.operation == "Inactive"
    click(app, "stop-server", bench.usb.serial)
    assert stopped == [True] and not bench.usb.IsConnected


def test_gui_keeps_activation_disabled_for_unknown_feedback(bench):
    bench.usb.operation = "0"  # Observed KSC101 startup value; not Inactive.
    app = gui.create_app(ShutterHub(slots=1))
    result = click(app, "connect", bench.usb.serial)
    assert result["connection"]["children"] == "Connected"
    assert result["open"]["disabled"] and result["arm-ttl"]["disabled"]
    click(app, "disconnect", bench.usb.serial)


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
