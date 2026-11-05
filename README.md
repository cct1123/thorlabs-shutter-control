# Direct KSC101 shutter control

Python control through the documented APT binary protocol. The runtime requires
no Kinesis, APT application, pythonnet or Thorlabs SDK DLLs. This is a breaking
rewrite: the former library, SDK discovery workflow and SDK notebooks are removed.
Six [beginner notebooks](docs/examples/README.md) teach the current API, from
device inventory to qualified Manual ON/OFF, with hardware off by default.

**Engineering status: offline software verified; deployment is blocked.** Direct USB has offline coverage. KEH3 Ethernet, optical behavior,
TTL, driver persistence and endurance are not qualified. See [state](STATE.md)
and [delivery report](outputs/REPORT.md).

Use Python 3.12 and [uv](https://docs.astral.sh/uv/):

```powershell
uv sync --locked --group dev --extra gui
uv run --locked shutter-control --help
uv run --locked shutter-control --config config/shutters.example.toml check-config
uv run --locked python scripts/verify.py
```

Imports, help, configuration checks and verification never open hardware. An
absent or outdated lockfile fails the locked workflows. Optional USB dependencies:

```powershell
uv sync --locked --extra d2xx  # FTDI native D2XX library/driver installed separately
uv sync --locked --extra vcp   # Explicit virtual COM port; read-only commissioning
```

Explicit informational discovery needs no configuration file and opens no controller:

```powershell
uv run --locked --extra d2xx shutter-control discover
uv run --locked --extra vcp shutter-control discover --vcp
```

D2XX lists FTDI serials, USB IDs, descriptions and open flags; VCP lists port
names, hardware IDs and descriptions. Results can include other instruments and
are not verified KSC101 identities. No device is automatically selected or saved.
Control still requires an explicit configured target and matching model, serial
and allowed firmware read back over APT before control.

Copy the fictional example to ignored `shutters.local.toml`. Set exact controller
serial, firmware allowlist, physical role and transport. An omitted policy keeps
the controller read-only. No deployment policy has been validated by this rewrite.
Never infer shutter wiring or optical safety from a logical name.
KSC101 remembers changed modes across power cycles. Actual mode transitions also
require `policy.allow_persistent_mode_changes = true`; ordinary output permission
does not authorize that persistent effect. Selecting an already active Manual
mode reads back the state without rewriting it.

Only after the approved physical test prerequisites are met:

```powershell
uv run --locked shutter-control --target example identify
uv run --locked shutter-control --target example status
uv run --locked shutter-control gui
```

The GUI binds to localhost:8050 and connects only on a click. Qualified manual
ON/OFF, explicit Manual selection and bounded holds use the same owner as Python
and DiamondGUI. Electrical feedback never confirms optical closure. Close and
disconnect release communication; `shutdown_outputs()` is a separate explicit
cleanup operation. A lost process cannot guarantee a safe shutter.

USB retains FTDI driver dependence. Replacing Kinesis does not demonstrate a fix
for Windows FTDIBUS crashes. KEH3 ports are documented, but direct framing and hub
identity remain unresolved; configured Ethernet routes fail before opening a socket.

Read [setup](docs/getting-started.md), [API](docs/python-api.md),
[architecture](docs/architecture.md), [protocol traceability](docs/INTERFACE.md),
[sources](docs/sources.md), [transport/driver matrix](docs/hardware.md),
[commissioning](docs/HARDWARE_VALIDATION.md), [cutover](docs/cutover.md), and
[DiamondGUI integration](docs/diamondgui.md).
The [controller reference review](docs/controller-reference-review.md) records
the improvements taken from `C:/repo/thorlabs-control` and the remaining differences.
