"""Validate saved defaults in a local Jupyter kernel; never enable hardware gates.

Run: uv run --locked --group notebooks python scripts/verify_notebooks.py
Kernel namespace resets between notebooks; saved notebooks are never overwritten.
"""

import hashlib
import json
import os
import re
from pathlib import Path

import nbformat
from jupyter_client import KernelManager
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    os.environ.setdefault("JUPYTER_RUNTIME_DIR", str(ROOT / "tmp/notebook-runtime"))
    os.environ.setdefault("IPYTHONDIR", str(ROOT / "tmp/notebook-ipython"))
    results = []
    manager = KernelManager(kernel_name="python3")
    try:
        manager.start_kernel(cwd=str(ROOT / "docs/examples"))
        for path in sorted((ROOT / "docs/examples").glob("0*.ipynb")):
            notebook = nbformat.read(path, as_version=4)
            nbformat.validate(notebook)
            for cell in notebook.cells:
                if cell.cell_type == "markdown":
                    for target in re.findall(r"\]\(([^)]+)\)", cell.source):
                        if "://" not in target and not (path.parent / target).resolve().is_file():
                            raise ValueError(f"Broken link in {path}: {target}")
            code_cells = sum(cell.cell_type == "code" for cell in notebook.cells)
            notebook.cells.insert(
                0, nbformat.v4.new_code_cell("get_ipython().run_line_magic('reset', '-f')")
            )
            NotebookClient(notebook, km=manager, timeout=30, startup_timeout=30).execute()
            results.append(
                dict(
                    notebook=path.relative_to(ROOT).as_posix(),
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    schema="PASS",
                    markdown_links="PASS",
                    default_kernel_execution="PASS",
                    code_cells=code_cells,
                )
            )
            print(path.name, "PASS", flush=True)
    finally:
        if manager.has_kernel:
            manager.shutdown_kernel(now=True)
    (ROOT / "records/notebook-validation.json").write_text(
        json.dumps(
            dict(
                scope="offline saved defaults, no physical validation",
                method="one local kernel, namespace reset between independent notebooks",
                results=results,
            ),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
