# Beginner tutorial notebooks

Each notebook is independent. Start with 1 and work in order:

| Notebook | What you learn |
| --- | --- |
| [1. Device discovery](01_device_discovery.ipynb) | Configured identities, optional COM inventory, discovery limits |
| [2. Connection](02_connection.ipynb) | Passive owner, exact identity verification, communication release |
| [3. Status query](03_status_query.ipynb) | Electrical feedback, timestamps, optical uncertainty |
| [4. Settings](04_settings.ipynb) | TOML, deadlines, qualification policy |
| [5. Shutter modes](05_shutter_modes.ipynb) | Mode readback and explicit persistent Manual selection |
| [6. ON/OFF](06_on_off.ipynb) | Qualified solenoid requests with OFF cleanup in one cell |

From the repository root, use Python 3.12 through uv:

```powershell
uv sync --locked --group notebooks
uv run --locked --group notebooks jupyter lab docs/examples
```

Choose **Python 3 (ipykernel)** from this environment. Alternatively select
the project's `.venv` interpreter in your notebook editor after the sync.
The optional `notebooks` group is locked in `uv.lock`, separate from driver runtime.
Stop the server before syncing other extras. For authorized USB work:

```powershell
uv sync --locked --group notebooks --extra d2xx
uv run --locked --group notebooks --extra d2xx jupyter lab docs/examples
# Optional COM inventory / read-only VCP commissioning instead:
uv sync --locked --group notebooks --extra vcp
uv run --locked --group notebooks --extra vcp jupyter lab docs/examples
```

Native FTDI libraries and Windows bindings are separate prerequisites. These
commands do not authorize driver changes. See [setup](../getting-started.md).

## Default behavior and live use

Run All is hardware-free with saved defaults: access gates are false and config
identities are fictional with no output policy. There are no saved hardware
results. A skipped step is not a PASS. Imports/configuration do not scan devices.

Before a live read-only run, copy `config/shutters.example.toml` to ignored
`shutters.local.toml`, review exact serial/firmware/route/role, then edit `CONFIG`
and `TARGET`. Enable `RUN_HARDWARE` only within authorization. Discovery has a
separate `RUN_PORT_INVENTORY` gate; it never auto-connects to candidates. There is
no network scan. Close other notebook, GUI and CLI owners before connecting.

Mode changes and outputs have additional false-by-default gates. They require
the approved exact physical setup and qualification policy; no valid deployment
policy is supplied. A boolean is not physical qualification. Mode changes can
persist across power cycles. Only Manual output is supported; cycle/TTL setup
and KEH3 Ethernet remain unavailable.

Run a live operation as a complete cell; do not strand ON between cells.
Communication release is separate from OFF. Neither OFF readback nor kernel
shutdown proves optical closure. Keep independent source protection and follow
[protected recovery](../python-api.md) after ambiguity.

The [direct_control.py](direct_control.py) script remains hardware-free by default:

```powershell
uv run --locked python docs/examples/direct_control.py
```

The former Kinesis USB/LAN templates were removed during migration. These new
notebooks use the current direct-protocol API without restoring the SDK workflow.

For offline notebook schema/link and kernel execution checks:

```powershell
uv run --locked --group notebooks python scripts/verify_notebooks.py
```

The verifier uses a local kernel and resets its namespace between notebooks.
It never saves executed outputs into the tutorials. Repeated kernel startup on
the authoring host intermittently timed out in ZeroMQ; default Python-cell tests
and one full six-notebook kernel run passed. No physical result is implied.
