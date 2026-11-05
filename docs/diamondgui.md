# DiamondGUI integration

The integration was applied to the existing checkout at
`C:/Users/HFNV/diamondgui`, preserving unrelated dirty changes. Its shutter module
imports the canonical `ShutterHub`, status and error types from this package;
there is one implementation and no SDK compatibility backend.

DiamondGUI declares this package's D2XX extra and a uv source pointing to the
reviewed local checkout. Its lockfile retains the other instrument dependencies,
including pythonnet where used by other hardware. Shutter independence does not
authorize removing camera/rotator dependencies.

`HardwareManager` retains its single shutter owner and disabled registration.
The prepared `build_shutter_owner` factory takes the explicit new TOML path plus
the existing `SHUTTER_CH_MAP` metadata and hub address. It rejects differences in
logical names, application CH, serials or selected hub routes before connection.
The existing mapping is retained; no USB fallback is substituted for its LAN
route. The exact hub identity/firmware and new local TOML are still missing.

The page reuses command results rather than issuing another status read. Its
Close request reaches the active owner before waiting for the page presentation
lock, so cancellation can interrupt active owner work. The existing public target
methods, status schema and manager cleanup hook remain. Enable now rejects as an
output alias, and recovered observations/fault lockout follow the stricter task
requirements. No legacy constructor arguments are accepted.
The reference follow-up keeps this public owner surface. Changed modes require
`allow_persistent_mode_changes` in the reviewed local policy; an already Manual
controller is not rewritten. A partial/unknown-count write disables all further
frames on that connection, including a page Close request, and reports unknown
state until protected recovery. No DiamondGUI source was edited in that follow-up.

The unexecuted shutter notebook is migrated to an explicitly gated read-only
example. The default Run All path has hardware access off and no saved execution
results. Driver/page guides and focused tests are updated. No application launch,
device discovery, output, native driver change or hardware registration occurred.

Integration tests are recorded in `records/diamondgui-tests.xml`. They establish
the passive import/configuration boundary, mapping refusals, page result/schema
behavior and protective dispatch around the page lock. They do not establish
real task cancellation, beam routing, optical safety or native driver timing.
