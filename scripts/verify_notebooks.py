"""Statically validate live-hardware tutorials without executing their cells.

Run: uv run --locked --group notebooks python scripts/verify_notebooks.py
Hardware execution belongs in an operator-controlled notebook session.
"""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inspect_notebook(path):
    """Check syntax/links and inventory saved execution; never execute or erase it."""
    notebook = json.loads(path.read_text(encoding="utf-8"))
    if notebook["nbformat"] != 4:
        raise ValueError(f"Unsupported notebook format: {path}")
    code_cells = 0
    saved_output_cells = 0
    for index, cell in enumerate(notebook["cells"]):
        source = cell["source"]
        source = source if isinstance(source, str) else "".join(source)
        if cell["cell_type"] == "code":
            if cell["execution_count"] is not None or cell["outputs"]:
                saved_output_cells += 1
            compile(source, f"{path}:cell-{index}", "exec")
            code_cells += 1
        elif cell["cell_type"] == "markdown":
            for target in re.findall(r"\]\(([^)]+)\)", source):
                target = target.split("#", 1)[0]
                if target and "://" not in target and not (path.parent / target).is_file():
                    raise ValueError(f"Broken link in {path}: {target}")
    return dict(
        notebook=path.name,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        python_syntax="PASS",
        markdown_links="PASS",
        saved_output_cells=saved_output_cells,
        hardware_execution="NOT RUN",
        code_cells=code_cells,
    )


def main():
    import nbformat

    results = []
    for path in sorted((ROOT / "docs/examples").glob("*.ipynb")):
        nbformat.validate(nbformat.read(path, as_version=4))
        result = inspect_notebook(path)
        result["schema"] = "PASS"
        results.append(result)
        print(path.name, "PASS static checks; hardware NOT RUN", flush=True)
    (ROOT / "records/notebook-validation.json").write_text(
        json.dumps(
            dict(
                scope="static notebook validation only; no cell execution or hardware substitute",
                results=results,
            ),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
