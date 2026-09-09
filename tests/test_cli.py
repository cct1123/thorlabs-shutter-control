import sys

import pytest

from thorlabs_shutter_control import __main__ as cli
from thorlabs_shutter_control import controller as module


def test_list_does_not_connect_or_actuate(rig, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["shutter-control", "--list"])
    assert cli.main() == 0
    assert capsys.readouterr().out.strip() == "68000001"
    assert rig.device.calls == []


def test_missing_sdk_is_an_actionable_nonzero_exit(monkeypatch, capsys):
    monkeypatch.setattr(module, "_loaded_sdk", None)
    monkeypatch.setattr(
        sys, "argv", ["shutter-control", "--list", "--kinesis-dir", "tmp/nonexistent-sdk-for-test"]
    )
    assert cli.main() == 1
    assert "Kinesis SDK not found" in capsys.readouterr().err


def test_server_exception_still_attempts_shutdown(rig, monkeypatch):
    from thorlabs_shutter_control import gui

    rig.controller.connect()

    class Server:
        def run(self, **kwargs):
            assert kwargs["debug"] is False
            assert kwargs["use_reloader"] is False
            assert kwargs["host"] == "127.0.0.1"
            raise RuntimeError("server failure")

    monkeypatch.setattr(cli, "KSC101Controller", lambda *a, **k: rig.controller)
    monkeypatch.setattr(gui, "create_app", lambda controller: Server())
    monkeypatch.setattr(sys, "argv", ["shutter-control"])
    with pytest.raises(RuntimeError, match="server failure"):
        cli.main()
    assert rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]
