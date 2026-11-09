"""Standalone server lifecycle checks over localhost; no instrument access."""

import json
from threading import Event, Thread
from types import SimpleNamespace
from urllib.request import Request, urlopen

from thorlabs_shutter_control import gui


def test_embedded_app_has_no_shutdown_control():
    app = gui.create_app(SimpleNamespace(configs=[]))
    client = app.server.test_client()
    assert b"shutdown-server" not in client.get("/_dash-layout").data
    assert b"shutdown-server" not in client.get("/_dash-dependencies").data


def test_standalone_shutdown_replies_closes_listener_and_cleans_up(monkeypatch):
    from werkzeug.serving import make_server

    ready = Event()
    calls, servers, errors = [], [], []
    hub = SimpleNamespace(
        configs=[],
        shutdown_outputs=lambda: calls.append("off"),
        close=lambda: calls.append("release"),
    )

    def listen(host, port, app, **kwargs):
        assert host == "127.0.0.1" and kwargs == {"threaded": True}
        server = make_server(host, 0, app, **kwargs)  # OS-assigned test-only port.
        servers.append(server)
        ready.set()
        return server

    monkeypatch.setattr("werkzeug.serving.make_server", listen)

    def serve():
        try:
            gui.run(hub)
        except BaseException as exc:
            errors.append(exc)

    worker = Thread(target=serve, daemon=True)
    worker.start()
    assert ready.wait(3)
    server = servers[0]
    url = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(url + "/_dash-dependencies", timeout=3) as response:
            dependencies = json.load(response)
        key = next(d["output"] for d in dependencies if "shutdown-server.children" in d["output"])
        payload = {
            "output": key,
            "outputs": [
                {"id": "shutdown-server", "property": "children"},
                {"id": "shutdown-server", "property": "disabled"},
            ],
            "changedPropIds": ["shutdown-server.n_clicks"],
            "inputs": [{"id": "shutdown-server", "property": "n_clicks", "value": 1}],
            "state": [],
        }
        request = Request(
            url + "/_dash-update-component",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=3) as response:
            result = json.load(response)["response"]["shutdown-server"]
        assert result["disabled"] is True and "Shutting down" in result["children"]
        worker.join(3)
        assert not worker.is_alive() and not errors
        assert calls == ["off", "release"]
        assert server.socket.fileno() == -1
    finally:
        if worker.is_alive():
            raise AssertionError("Standalone shutdown did not exit its server loop")
