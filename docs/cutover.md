# Cutover and rollback

The runtime has one implementation: `thorlabs_shutter_control.ShutterHub`.
Current examples use the logical name `shutter`; configuration's integer
`channel` is an application index, separate from APT channel 1. The legacy
DiamondGUI method names and status fields remain intentional integration
contracts; no second backend or constructor-argument shim is retained.

| Retired path | Current replacement |
| --- | --- |
| Kinesis/pythonnet shutter backend and SDK caches | Direct APT driver and fresh `get_status()` through the shared owner |
| `keh3-probe`, `keh3-analyze` and candidate `keh3.py` connection path | Explicit TOML route, `identify` / `status`, or owner `connect()` / `identify_device()` |
| Notebook-specific Ethernet connection wrapper and duplicated route maps | `shutter_config.SHUTTER`, loaded from `config/shutter.ethernet.toml` |
| Ambiguous solenoid scalar as normalized OFF/ON | Fresh status-bit output; raw `get_solenoid_state_reply()` only for explicit diagnostics |
| Passive `direct_control.py` gate example | README/Python API context examples and CLI `check-config` for passive validation |

There is no automatic data/configuration migration. Copy and validate the explicit
TOML before deploying; retired CLI commands fail rather than falling back.
Saved notebook outputs, older JSON field names and historical reports preserve
their original evidence. Their existence does not make them current runtime APIs.

The selected Ethernet controller's E181 commissioning and local software checks
are recorded separately. The external DiamondGUI checkout is unavailable here;
its factory/page integration must be revalidated before deploying this revision.

1. Keep independent source protection engaged. Stop tasks and release all shutter
   owners. Confirm optical state independently. Record the old source revision and
   exact configuration; retain current logs, notebooks, datasets and rollback media.
2. Inventory all serial instruments, device identities/locations/bindings,
   signed driver packages and versions, loaded FTDI/native libraries, COM ports,
   Windows version and approved package restoration procedure. Read-only inventory
   must be reviewed before any driver change. No inventory or cutover ran here.
3. Install the new uv environment from its lockfile. Verify offline imports/help,
   source/wheel tests and explicit configuration. Remove old application processes;
   do not run old and new owners concurrently.
4. Supply qualification records and exact local routes. Keep policy absent and
   startup passive until approved identity/state checks pass. Never reuse a firmware
   allowlist as proof of the protocol contract. Docked KEH3 writes are implemented
   under the shared load policy; commission only the exact approved setup and
   retain broader hub/physical gaps. Preserve unrelated rotator/camera software
   and dependencies.
5. Execute the approved bench procedure and persistence/endurance campaign. Capture
   electrical and optical evidence separately. Promote only routes with current
   PASS evidence; unresolved required routes keep the project BLOCKED.

If a driver cutover is necessary, obtain downtime for every instrument sharing
that stack, export the known package/rollback arrangement and use supported
Windows package management. Do not manually replace shared DLL/SYS files, run
Zadig against a guessed device, or remove FTDIBUS as an incidental experiment.

Rollback is an explicit deployment choice: protect the source, stop the new owner,
restore the captured revision/configuration and approved signed package/binding,
then requalify identities and physical states before output. There is no runtime
compatibility layer or automatic transport/software fallback.
