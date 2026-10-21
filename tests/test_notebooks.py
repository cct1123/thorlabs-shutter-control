"""Run each published notebook once with fictional software devices."""

import json
from pathlib import Path

import pytest

from thorlabs_shutter_control import controller


@pytest.mark.parametrize("transport", ["usb", "lan"])
def test_notebook_completes_one_cycle_and_releases(bench, transport, capsys):
    filename = "shutter_lan_tutorial" if transport == "lan" else "shutter_open_close_tutorial"
    path = Path(__file__).resolve().parents[1] / "docs/examples" / f"{filename}.ipynb"
    cells = [
        c for c in json.loads(path.read_text(encoding="utf-8"))["cells"] if c["cell_type"] == "code"
    ]
    assert all(c["execution_count"] is None and not c["outputs"] for c in cells)
    namespace = {}
    for cell in cells:
        exec(compile("".join(cell["source"]), cell["id"], "exec"), namespace)
        if cell["id"] == "settings":
            namespace.update(
                SERIAL=bench.usb.serial,
                HUB_IP="192.0.2.10",
                CUBE_SERIAL=bench.lan.serial,
                HOLD_SECONDS=0.1,
                sleep=controller.time.sleep,
                perf_counter=controller.time.monotonic,
            )
    device = bench.lan if transport == "lan" else bench.usb
    assert not device.IsConnected and device.position == "Closed"
    assert ("state", "Active") in device.calls
    output = capsys.readouterr().out
    assert "Open: open" in output and "Close: closed" in output
