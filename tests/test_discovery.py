"""TEST-216: explicit inventory never opens/selects a device or bypasses identity."""

import sys
from types import SimpleNamespace

import pytest
from conftest import FakeTransport

from thorlabs_shutter_control import ShutterHub
from thorlabs_shutter_control import __main__ as cli


def forbid(*args, **kwargs):
    pytest.fail("Inventory unexpectedly loaded config, selected or opened a device")


@pytest.fixture
def inventory_only(monkeypatch):
    monkeypatch.setattr(cli, "load_config", forbid)
    monkeypatch.setattr(cli, "ShutterHub", forbid)


def test_d2xx_inventory_snapshot_without_open(inventory_only, monkeypatch, capsys):
    calls = []

    def snapshot():
        calls.append("snapshot")
        return 2

    def detail(index, *, update):
        assert update is False
        calls.append(index)
        return {
            "serial": (b"68000001", b"OTHER")[index],
            "description": (b"KSC101", b"Other FTDI instrument")[index],
            "id": 0x04036001,
            "flags": index,
        }

    monkeypatch.setitem(
        sys.modules,
        "ftd2xx",
        SimpleNamespace(createDeviceInfoList=snapshot, getDeviceInfoDetail=detail, openEx=forbid),
    )
    assert cli.main(["--config", "does-not-exist.toml", "discover"]) == 0
    out = capsys.readouterr()
    assert "68000001\tVID:PID=0403:6001\tKSC101\tclosed" in out.out
    assert "OTHER\tVID:PID=0403:6001\tOther FTDI instrument\tOPEN" in out.out
    assert "informational only" in out.err
    assert calls == ["snapshot", 0, 1]


def test_vcp_inventory_without_open(inventory_only, monkeypatch, capsys):
    ports = [
        SimpleNamespace(device="COM7", hwid="USB VID:PID=0403:6001", description="FTDI"),
        SimpleNamespace(device="COM2", hwid="PNP", description="Other serial instrument"),
    ]
    monkeypatch.setitem(sys.modules, "ftd2xx", SimpleNamespace(createDeviceInfoList=forbid))
    monkeypatch.setitem(sys.modules, "serial", SimpleNamespace(Serial=forbid))
    monkeypatch.setitem(
        sys.modules,
        "serial.tools",
        SimpleNamespace(list_ports=SimpleNamespace(comports=lambda: ports)),
    )
    assert cli.main(["discover", "--vcp"]) == 0
    out = capsys.readouterr()
    assert out.out.splitlines() == [
        "COM2\tPNP\tOther serial instrument",
        "COM7\tUSB VID:PID=0403:6001\tFTDI",
    ]
    assert "verified on connection before control" in out.err


@pytest.mark.parametrize("vcp", [False, True])
def test_empty_inventory_is_explicit(inventory_only, monkeypatch, capsys, vcp):
    monkeypatch.setitem(sys.modules, "ftd2xx", SimpleNamespace(createDeviceInfoList=lambda: 0))
    monkeypatch.setitem(
        sys.modules,
        "serial.tools",
        SimpleNamespace(list_ports=SimpleNamespace(comports=lambda: [])),
    )
    assert cli.main(["discover", *(["--vcp"] if vcp else [])]) == 0
    assert capsys.readouterr().out == "(none)\n"


@pytest.mark.parametrize("vcp,module", [(False, "ftd2xx"), (True, "serial.tools")])
def test_missing_optional_dependency_is_failure(inventory_only, monkeypatch, capsys, vcp, module):
    monkeypatch.setitem(sys.modules, module, None)
    assert cli.main(["discover", *(["--vcp"] if vcp else [])]) == 1
    out = capsys.readouterr()
    assert not out.out
    assert ("vcp extra" if vcp else "d2xx extra") in out.err


def test_enumeration_error_is_not_empty_success(inventory_only, monkeypatch, capsys):
    def failed():
        raise OSError("FTDI enumeration failed")

    monkeypatch.setitem(sys.modules, "ftd2xx", SimpleNamespace(createDeviceInfoList=failed))
    assert cli.main(["discover"]) == 1
    out = capsys.readouterr()
    assert not out.out and "FTDI enumeration failed" in out.err


def test_control_still_requires_target(config, monkeypatch, capsys):
    monkeypatch.setattr(cli, "load_config", lambda path: [config])
    monkeypatch.setattr(ShutterHub, "connect", forbid)
    assert cli.main(["status"]) == 1
    assert "--target is required" in capsys.readouterr().err


@pytest.mark.parametrize(
    "attribute,value", [("serial", "68000002"), ("model", "TSC001"), ("firmware", (8, 0, 1))]
)
def test_cli_identity_mismatch_prevents_control(
    config, tmp_path, monkeypatch, capsys, attribute, value
):
    device = FakeTransport(config)
    setattr(device, attribute, value)
    hub = ShutterHub([config], transport_factory=lambda c, d: device, lock_directory=tmp_path)
    monkeypatch.setattr(cli, "load_config", lambda path: [config])
    monkeypatch.setattr(cli, "ShutterHub", lambda configs: hub)
    assert cli.main(["--target", "beam", "manual"]) == 1
    assert "mismatch" in capsys.readouterr().err.lower()
    assert device.closed and not device.output_frames
