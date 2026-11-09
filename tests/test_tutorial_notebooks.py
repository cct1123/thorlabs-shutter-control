"""Static checks for live tutorials; no simulated notebook execution or device I/O."""

import json
import re
import socket
import sys
from pathlib import Path

import nbformat
import pytest

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((ROOT / "docs/examples").glob("*.ipynb"))


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.stem)
def test_live_notebook_static_checks(path):
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    code_cells = 0
    for index, cell in enumerate(notebook.cells):
        if cell.cell_type == "code":
            compile(cell.source, f"{path}:cell-{index}", "exec")
            code_cells += 1
        elif cell.cell_type == "markdown":
            for target in re.findall(r"\]\(([^)]+)\)", cell.source):
                target = target.split("#", 1)[0]
                if target and "://" not in target:
                    assert (path.parent / target).is_file(), f"Broken link in {path}: {target}"
    assert code_cells > 0


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.stem)
@pytest.mark.parametrize("directory", [ROOT, ROOT / "docs/examples"])
def test_ethernet_setup_is_passive_and_exact(path, directory, monkeypatch):
    monkeypatch.chdir(directory)
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.delitem(sys.modules, "shutter_config", raising=False)
    monkeypatch.setattr(
        socket, "create_connection", lambda *a, **kw: pytest.fail("Setup opened hardware")
    )
    setup = next(
        cell["source"]
        for cell in json.loads(path.read_text(encoding="utf-8"))["cells"]
        if cell["cell_type"] == "code"
    )
    namespace = {}
    exec(compile("".join(setup), str(path), "exec"), namespace)
    selected = namespace["SHUTTER"]
    assert selected.name == "shutter" and selected.serial_number == "68800777"
    assert selected.route.kind == "keh3"
    assert selected.route.endpoint == "192.168.1.19:40305"
    assert selected.policy.shutter_model == "SH05R"
