import sys
from pathlib import Path

import pytest

from thorlabs_shutter_control import KCubeShutter, gui
from thorlabs_shutter_control import __main__ as cli
from thorlabs_shutter_control import controller as module


def install_server(monkeypatch, serve_request):
    """Exercise main's owned-server loop without binding a port or loading the SDK."""
    create = gui.create_app
    owned = {}

    def create_app(*args, **kwargs):
        owned["stop"] = kwargs["on_shutdown"]
        owned["app"] = create(*args, **kwargs)
        return owned["app"]

    class Server:
        server_port = 8050

        def __enter__(self):
            return self

        def __exit__(self, *args):
            owned["closed"] = True

        def handle_request(self):
            serve_request(owned["app"])
            owned["stop"]()

    def make_server(host, port, app, **kwargs):
        assert host == "127.0.0.1" and port == 8050
        assert app is owned["app"].server and kwargs == {"threaded": False}
        return Server()

    monkeypatch.setattr(gui, "create_app", create_app)
    monkeypatch.setattr(cli, "make_server", make_server)
    return owned


def layout_components(app):
    """Inspect the served Dash layout without starting a network listener."""
    components = {}

    def visit(item):
        if isinstance(item, list):
            for child in item:
                visit(child)
        elif isinstance(item, dict):
            props = item.get("props", {})
            if "id" in props:
                components[props["id"]] = props
            visit(props.get("children"))

    response = app.server.test_client().get("/_dash-layout")
    assert response.status_code == 200
    visit(response.get_json())
    return components


@pytest.mark.parametrize("serials", [["68000003", "68000001", "68000002"]])
def test_gui_launch_has_three_passive_panels_with_requested_preselection(rig, monkeypatch, serials):
    inspected = []

    def forbidden_sdk_load(directory):
        pytest.fail("GUI launch and unconnected shutdown must not load the SDK.")

    def inspect_server(self):
        components = layout_components(self)
        assert components["stop-server"]["children"] == "Shut down GUI & devices"
        for slot in range(3):
            assert components[f"serial-{slot + 1}"]["value"] == (
                serials[slot] if slot < len(serials) else None
            )
            assert components[f"connection-{slot + 1}"]["children"] == "Disconnected"
            assert components[f"open-{slot + 1}"]["disabled"] is True
        inspected.append(True)

    monkeypatch.setattr(module, "_load_sdk", forbidden_sdk_load)
    install_server(monkeypatch, inspect_server)
    monkeypatch.setattr(cli.config, "SERIAL_NUMBERS", serials)
    assert cli.main() == 0
    assert inspected == [True]
    assert rig.manager_calls == []
    assert all(device.calls == [] for device in rig.devices.values())


@pytest.mark.parametrize(
    "endpoints,expected_routes",
    [
        (("192.0.2.10:40304",), ["Ethernet LAN · 192.0.2.10:40304"]),
        ((None, "192.0.2.10:40304"), ["USB", "Ethernet LAN · 192.0.2.10:40304"]),
    ],
)
def test_launcher_configures_lan_panels_without_discovering_on_startup(
    rig, monkeypatch, endpoints, expected_routes
):
    def forbidden_sdk(directory):
        pytest.fail("Configured LAN startup must stay passive")

    def inspect_server(app):
        components = layout_components(app)
        suffixes = [""] if len(expected_routes) == 1 else ["-1", "-2"]
        for suffix, route in zip(suffixes, expected_routes, strict=True):
            assert components[f"transport{suffix}"]["children"] == route
            assert components[f"connection{suffix}"]["children"] == "Disconnected"
            assert components[f"open{suffix}"]["disabled"] is True

    monkeypatch.setattr(cli.config, "ETHERNET_ENDPOINTS", endpoints)
    monkeypatch.setattr(module, "_load_sdk", forbidden_sdk)
    install_server(monkeypatch, inspect_server)
    assert cli.main() == 0
    assert not rig.manager_calls and not rig.device.calls


@pytest.mark.parametrize(
    "settings",
    [
        {"SERIAL_NUMBERS": ("68000001", "68000001")},
        {"SERIAL_NUMBERS": ("68000001", 68000001)},
        {"SLOTS": 1, "SERIAL_NUMBERS": ("68000001", "68000002")},
        {"SERIAL_NUMBERS": ("invalid",)},
        {"PORT": 0},
        {"PORT": 65536},
        {"PORT": True},
        {"PORT": "8050"},
        {"SLOTS": 0},
        {"SLOTS": -1},
        {"SLOTS": 1.5},
        {"ETHERNET_ENDPOINTS": "192.0.2.10:40304"},
        {"ETHERNET_ENDPOINTS": ("192.0.2.10:40303",)},
        {"SLOTS": 1, "ETHERNET_ENDPOINTS": (None, "192.0.2.10:40304")},
    ],
)
def test_invalid_project_config_is_rejected_before_sdk_or_server_access(
    rig, monkeypatch, capsys, settings
):
    def forbidden(*args, **kwargs):
        pytest.fail("Invalid project config must not access SDK or start the server.")

    for key, value in settings.items():
        monkeypatch.setattr(cli.config, key, value)
    monkeypatch.setattr(module, "_load_sdk", forbidden)
    monkeypatch.setattr(cli, "make_server", forbidden)
    assert cli.main() == 1
    assert "Invalid project config" in capsys.readouterr().err
    assert rig.manager_calls == []
    assert all(device.calls == [] for device in rig.devices.values())


def test_sdk_path_comes_from_project_config_not_environment(monkeypatch):
    tmp_path = Path("tmp/nonexistent-sdk-path-test")
    monkeypatch.setattr(module, "_loaded_sdk", None)
    monkeypatch.setattr(module.sys, "platform", "win32")
    monkeypatch.setattr(cli.config, "KINESIS_DIR", str(tmp_path / "project-sdk"))
    monkeypatch.setenv("KINESIS_DIR", str(tmp_path / "environment-sdk"))
    with pytest.raises(module.ShutterError, match="project-sdk"):
        module._load_sdk(None)
    with pytest.raises(module.ShutterError, match="explicit-sdk"):
        module._load_sdk(tmp_path / "explicit-sdk")


@pytest.mark.parametrize(
    "interruption,shutdown_failure", [(RuntimeError, True), (KeyboardInterrupt, False)]
)
def test_server_exit_attempts_every_shutter_and_reports_shutdown_failures(
    rig, monkeypatch, capsys, interruption, shutdown_failure
):
    rig.serials[:] = list(rig.devices)
    controllers = [KCubeShutter(timeout=0.5) for _ in range(3)]
    supplied = iter(controllers)
    monkeypatch.setattr(module, "KCubeShutter", lambda *args, **kwargs: next(supplied))

    def interrupt_server(self):
        for controller, serial in zip(controllers, rig.serials, strict=True):
            controller.connect(serial)
            controller.open_shutter()
        if shutdown_failure:
            rig.devices["68000001"].fail.add("set_state")
            rig.devices["68000002"].fail.add("disconnect")
        raise interruption("server failure")

    install_server(monkeypatch, interrupt_server)
    monkeypatch.setattr(sys, "argv", ["shutter-control"])
    if interruption is RuntimeError:
        # Preserving the server exception also preserves its nonzero process exit.
        with pytest.raises(RuntimeError, match="server failure"):
            cli.main()
    else:
        assert cli.main() == (1 if shutdown_failure else 0)

    error_output = capsys.readouterr().err
    if shutdown_failure:
        assert "Shutter 1 (68000001)" in error_output and "set_state" in error_output
        assert "Shutter 2 (68000002)" in error_output and "disconnect" in error_output
    else:
        assert error_output == ""
    for device in rig.devices.values():
        assert device.calls[-2:] == [("stop_poll",), ("disconnect",)]
    assert rig.devices["68000003"].state == "Closed"
    assert not rig.devices["68000003"].IsConnected
    if not shutdown_failure:
        assert all(device.state == "Closed" for device in rig.devices.values())
        assert all(not device.IsConnected for device in rig.devices.values())


def test_shutdown_button_returns_response_then_releases_http_listener(rig, monkeypatch):
    import json
    import socket
    from threading import Event, Thread
    from urllib.request import Request, urlopen

    from werkzeug.serving import make_server

    ready = Event()
    servers = []
    apps = []
    stops = []
    errors = []
    results = []
    create = gui.create_app

    def create_app(*args, **kwargs):
        app = create(*args, **kwargs)
        stops.append(kwargs["on_shutdown"])
        apps.append(app)
        return app

    def bind(host, port, app, **kwargs):
        server = make_server(host, 0, app, **kwargs)  # OS-selected localhost test port.
        servers.append(server)
        ready.set()
        return server

    def run():
        try:
            results.append(cli.main())
        except BaseException as exc:
            errors.append(exc)

    monkeypatch.setattr(gui, "create_app", create_app)
    monkeypatch.setattr(cli, "make_server", bind)
    worker = Thread(target=run, daemon=True)
    worker.start()
    try:
        assert ready.wait(5)
        app = apps[0]
        url = f"http://127.0.0.1:{servers[0].server_port}"
        key, callback = next(iter(app.callback_map.items()))
        payload = {
            "output": key,
            "outputs": [
                {"id": o.component_id, "property": o.component_property} for o in callback["output"]
            ],
            "inputs": [dict(item, value=1) for item in callback["inputs"]],
            "state": [
                dict(item, value=None if item["id"].startswith("serial") else "high")
                for item in callback["state"]
            ],
            "changedPropIds": ["stop-server.n_clicks"],
        }
        request = Request(
            url + "/_dash-update-component",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            result = json.load(response)["response"]
        assert "server shutting down" in result["hub-message"]["children"]
        worker.join(5)
        assert not worker.is_alive() and results == [0] and not errors
        with socket.socket() as probe:
            probe.settimeout(1)
            assert probe.connect_ex(("127.0.0.1", servers[0].server_port)) != 0
        assert not rig.manager_calls and not rig.device.calls
    finally:
        # Bound cleanup even if an assertion fails before the shutdown request.
        if worker.is_alive() and stops:
            stops[0]()
        worker.join(2)
