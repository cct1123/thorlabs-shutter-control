# DiamondGUI integration

**Current deployment is blocked:** the separate dirty checkout at
C:/Users/HFNV/diamondgui exists, but its shutter page is entirely commented out.
The current isolated checks pass 3 owner/factory cases and fail all 26 page cases
because layout, summary and session exports are absent. Its hardware/config.py
still uses the old logical key and left-bay port 40304, differing from this
repository's shutter / middle-bay port 40305 configuration. No external source or
local configuration was changed. The old unavailable-checkout assumption and
historical 29-case PASS are superseded by [current evidence](../records/diamondgui-current-integration.json)
and [test results](../records/diamondgui-current-tests.xml).

## Adapter contract

The external shutter module imports the canonical ShutterHub, status and error
types from this package. There is one implementation and no SDK compatibility
backend. DiamondGUI declares this package's D2XX extra and an editable uv source
pointing at this checkout. Other instrument dependencies, including pythonnet
where needed, remain independent of shutter application/SDK independence.

HardwareManager retains one shutter owner and disabled default registration.
The prepared build_shutter_owner factory accepts an explicit TOML path and the
existing SHUTTER_CH_MAP metadata plus hub address. It rejects differences in
names, application channels, serials and selected routes before connection.
There is no USB fallback. This repository supplies config/shutter.ethernet.toml
for the selected controller, with hub identity/firmware explicitly unknown.
Migrate deployment metadata deliberately; do not rename physical roles by inference.

Public owner methods/status fields remain stable. Enable rejects because it
aliases output; partial/unknown-count writes refuse every subsequent frame,
including OFF, until protected recovery. Operating state stays unknown rather
than being inferred from electrical ON/OFF. Docked KEH3 and D2XX use the same
reviewed Manual/load/interlock/ownership boundary; VCP/external USB writes remain
restricted. Changed modes require separate persistent-mode permission, and
Trigger exit additionally requires established source protection.

## Page restoration and validation

The previous page implementation reused command results rather than issuing a
second status query. Protective Close reached the owner before waiting for the
presentation lock. Its disabled copy and tests remain in the external dirty
checkout. Restoring that page and migrating its stale metadata requires a
separate decision about those existing edits; this package review preserves them.
Do not promote a commented page as a completed application migration.

The current tests were inspected before execution. They use passive construction
and isolated page test doubles, redirect paths to disposable project storage,
and resolve no live HardwareManager, runtime or device. They establish the
adapter PASS and page FAIL only; they do not establish task/beam routing, optical
safety or native driver timing. E181 is the historical exact middle-bay controller
cycle, separate from this application result. After restoring the intended page
and metadata, rerun both focused files against the chosen package revision and
complete physical cutover only within its approved setup/window.
