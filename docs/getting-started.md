# Setup and diagnosis

Use a 64-bit Python 3.12 deployment through uv. All setup, tests and execution
use uv; Windows device bindings and native libraries remain separate.

```powershell
uv sync --locked --extra gui --group dev
uv run --locked python scripts/verify.py
```

Launch the GUI from the repository root:

```powershell
uv run shutter-control gui
```

The GUI defaults to the tracked Ethernet profile
and http://127.0.0.1:9860; it opens no device until you select an exact target and
click Connect. Override with `--config PATH` before `gui` or `gui --port PORT`.
Other CLI commands continue to default to `shutters.local.toml`.

The default package has no Python runtime dependencies. Optional `d2xx` uses
ftd2xx 1.3.8 and the installed FTDI D2XX native library; it never uses a Thorlabs
DLL. Optional `vcp` uses pyserial 3.5 and an exact configured port. The VCP bridge
reset equivalence is unresolved, so VCP connections are read-only commissioning.
Do not change USB bindings as part of installation; follow [cutover](cutover.md).

To explicitly list host metadata without opening a controller or loading config:

```powershell
uv run --locked --extra d2xx shutter-control discover
uv run --locked --extra vcp shutter-control discover --vcp
```

The first command enumerates all FTDI D2XX descriptors, including unrelated
devices; the second enumerates OS serial ports. Neither identifies a controller
over APT, selects a target, changes configuration or falls back to another route.
An empty list does not prove absence on the other transport. Copy reviewed
identity/route information into local configuration; connection verifies the
configured model, serial and allowed firmware before control. Imports and help
never run this inventory. Native enumeration duration depends on the OS driver.

Configuration is strict TOML, loaded without discovery or I/O. Start from
`config/shutters.example.toml`; local configuration is ignored by Git. Each entry
requires name, application channel, physical role, exact KSC101 serial, firmware
allowlist and an explicit route. Model must read back KSC101, with one channel.
Duplicate serials/names/channels/routes fail before connecting.

For KEH3, supply host and bay. Omit hub_serial/hub_firmware when unknown;
do not insert placeholder identities. The controller reply does not identify
the hub. Optional known metadata is checked for consistency across its routes.

`policy` is omitted by default. Writes require an operator-reviewed qualification
record covering shutter model, wiring, OFF -> optical closed mapping, interlocks,
continuous-duty permission and minimum OFF interval. The current implementation
only activates continuous-duty loads in permitted modes: finite exposure/duty policies fail
closed until an independent cutoff and applicable limits are qualified.
Changing a policy requires revalidation; setting a boolean is not qualification.
`allow_persistent_mode_changes` is a legacy compatibility field and does not gate
mode selection; electrical OFF and interlock/readback checks remain. KSC101 mode changes
persist automatically (SRC-002 p20) even without an explicit EEPROM command.

| Symptom | Meaning / response |
| --- | --- |
| Missing ftd2xx/native DLL | Install optional Python extra and matching official FTDI native package; no Thorlabs application required |
| Already owned | Release the active owner; a failed release retains claims; do not delete lock files to bypass ownership |
| Identity mismatch | Check exact controller/route with source protected; no fallback or output cleanup to a mismatched device |
| Fault lockout | Keep independent optical protection; explicit Stop/OFF resets after verified OFF/interlock. A poisoned session needs Release/Connect first; passive protected recovery is another option. Never repeat ON |
| Control route unavailable | VCP and KEH3 external USB OUT writes are refused; docked KEH3 writes require the reviewed load policy and mode/interlock checks |
| Trigger->Manual refused | Check electrical OFF and enabled interlock requirement; no source confirmation is required for mode selection |
| OFF unconfirmed | Physical state remains unknown; use independent source protection and inspect the shutter |
| Write framing unknown | No more frames, including OFF, are sent on that connection; independently inhibit the source and perform protected recovery |

Defaults cover complete operations: connection/identity 5 s, ordinary query or
command 3 s, separate cleanup 5 s. Driver/native calls can exceed their requested
timeouts; a late return is rejected, but hard dispatch/closure bounds require
physical validation and independent protection.
