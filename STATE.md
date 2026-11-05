# Engineering state

Updated: 2026-11-05. **BLOCKED engineering deployment; review complete in software.**
REQ-218 / TEST-218: PASS, E168 / D049. The user requested comprehensive review,
legacy removal, fixes, substantial simplification and a local commit, and confirmed
that all pending changes belong in the review. The local commit containing this
checkpoint delivers the reviewed work. No push, hardware actuation, lab-network probe, driver/binding
change or firmware change is authorized by this request. Historical Kinesis bench
results do not qualify this implementation.

## Architecture and working configuration

Optional FTDI D2XX/VCP bytes -> APT single-flight session -> KSC101 driver ->
canonical ShutterHub -> CLI / optional localhost Dash GUI / DiamondGUI owner.
The core has no Python runtime dependencies or SDK backend. Python minor is pinned
to 3.12; 3.12.7 is tested. uv.lock covers the build backend, dev tools, optional
transports/GUI and the separate notebooks group.

Construction/help/configuration are passive. Explicit discovery lists metadata
without opening/selecting controllers. Identity/model/firmware and exact routes
are checked before control. Only qualified continuous-duty Manual loads can be
operated. Actual mode transitions require separate persistent-mode permission;
selecting an already Manual/OFF controller sends no mode write. No policy for the
actual deployment is supplied. VCP remains read-only commissioning.

Operational KEH3 routes fail before socket access. Separate capture analysis and
the explicitly authorized single-query candidate probe never verify hub identity
or enable operation. No live probe has run. TTL/cycles and finite exposure/duty
loads remain unavailable. SRC-003 wire/hub identity/firmware and SRC-004 actual
shutter/setup contracts are unresolved; see docs/sources.md and
docs/keh3-offline-validation.md.

ON/pulse share fault handling and passive duration validation. Every OFF uses the
same priority/cleanup boundary. New output attempts invalidate prior cleanup
messages. Recovery preserves pending protective requests. Short/unknown writes
forbid every later frame, including OFF; receive-only ambiguity can permit a
qualified OFF attempt but cannot confirm safe state. Protected recovery never
replays ON. Requested, electrical and optical observations remain separate.

DiamondGUI at C:/Users/HFNV/diamondgui imports this owner; its passive factory
preserves names/CH/serial/routes. Registration remains disabled and local topology
is absent. This review changed no DiamondGUI source or dependency files. See
docs/diamondgui.md and records/diamondgui-migration.json.

## Requirements and current evidence

Full criteria/source sections are in PROJECT.md. TEST IDs correspond to REQ IDs.
E158..167 preserve earlier scope/source/diagnostic evidence; E168 revalidates the
current integrated software. PASS below is scoped to offline/simulated behavior.

| Requirement | Human source / short criterion | Validation / evidence | Current result |
| --- | --- | --- | --- |
| REQ-201 | Objective; uv/SDK independence | TEST-201: locked clean wheel/import/help; E168 | PASS offline; native drivers unqualified |
| REQ-202 | Identity and route requirements | TEST-202: mismatches, duplicates, changed identity, exact targets; E168 | PASS offline USB/config; live routes UNTESTED |
| REQ-203 | Communication; framing validation | TEST-203: reference/split/coalesced/malformed/fault frames; E168 | PASS offline; actual firmware UNTESTED |
| REQ-204 | Modes and constraints | TEST-204: policy, mode, interlock and duration refusals; E168 | PASS restricted software; actual load/other modes BLOCKED |
| REQ-205 | Freshness and deadlines | TEST-205: stale/late quarantine, total and separate cleanup budgets; E168 | PASS tested cases; arbitrary same-type reply ordering unresolved |
| REQ-206 | Ownership and priority cancellation | TEST-206: process claims, concurrent routes, query/hold cancellation; E168 | PASS offline; native 250 ms target UNTESTED |
| REQ-207 | Ambiguity and cleanup | TEST-207: partial writes, lockout/recovery, all-target cleanup; E168 | PASS offline; optical safety UNTESTED |
| REQ-208 | Direct KEH3 control | TEST-208: supported hub contract, exact occupied/empty/swapped routes | BLOCKED: manufacturer wire/identity/firmware contract |
| REQ-209 | Physical/local/TTL/interlock behavior | TEST-209: actual setup and approved physical procedure | BLOCKED: setup/ratings and authorization |
| REQ-210 | Drivers, persistence and endurance | TEST-210: inventory/rollback, reconnect/reboot/coexistence | BLOCKED: hardware and approved downtime/window |
| REQ-211 | DiamondGUI owner integration | TEST-211: 29 focused owner/factory/page tests; E168 | PASS software; actual task/bench integration UNTESTED |
| REQ-212 | Delivery and reproducibility | TEST-212: lock, source/wheel parity, docs/links/hashes; E168 | PASS software; actual load documentation absent |
| REQ-213 | User-selected controller reference | TEST-213: pinned read-only comparison; E161/E162 | PASS source review; no hardware acceptance transferred |
| REQ-214 | User QMI discovery investigation | TEST-214: pinned source investigation; E163 | PASS source review only |
| REQ-215 | Beginner tutorials (derived) | TEST-215: six saved-default and simulated notebooks; E164/E168 | PASS offline; historical kernel execution; repeat startup unreliable |
| REQ-216 | Explicit D2XX/VCP discovery | TEST-216: fake inventory, no-open/no-selection gates; E166/E168 | PASS offline; native enumeration UNTESTED |
| REQ-217 | KEH3 offline follow-up (derived) | TEST-217: capture verdicts, 90 split boundaries, gated probe, TCP loopback; E167/E168 | PASS preparation; operational routes remain BLOCKED |
| REQ-218 | Comprehensive review/simplification/commit (derived) | TEST-218: reproduced regressions, full source/wheel/integration, final diff; E168 | PASS software; delivered in the local checkpoint commit |

Current evidence: 131 source tests, the same 131 isolated-wheel tests and 29
DiamondGUI tests PASS, with no skips. records/direct-validation.json captures
commands, full-suite selection, source/test/tutorial/config/dependency hashes,
wheel hash and byte parity; XML files retain test cases. Ruff lint/format and
missing/stale-lock rejection PASS. Simulated dispatch meets 250 ms on
QueryPerformanceCounter (100 ns clock resolution); this is not native dispatch or
optical timing. Initial sandbox temp-folder failures and localhost timeouts remain
recorded in E167/E168; final verification passed via the uv isolated runner.

## Highest-priority gap and adaptive next action

Obtain the deployment evidence package,
resolve supported hub contracts, implement only documented routes and revalidate
affected software. Prepare the exact bench procedure before requesting a bounded
physical window. Only after qualification run the agreed persistence/endurance
campaign. Required unresolved routes, physics and drivers prevent completion.

## Human action required - supply the deployment evidence package

1. Known: KEH3 Rev E establishes ports, not a direct wire or hub identity contract.
   Historical KSC101/SH05R metadata does not establish today's bench (E158/E167).
2. Blocked: software cannot infer current firmware, shutter wiring/load ratings,
   optical OFF mapping or a manufacturer-supported Ethernet exchange.
3. Supply hub model/serial/firmware; each controller serial/firmware, logical
   name/CH/physical role and USB/COM or hub address/bay; shutter model/manual and
   wiring; and the manufacturer contract requested in docs/ethernet-assessment.md.
   Do not actuate or change drivers merely to fill this record.
4. Return current state observations with provenance/time and documented switching,
   duty/exposure/electrical limits with units. Mark unknowns unknown.
5. Next: reconcile those facts, finish supported routes and prepare the precise
   test/cleanup procedure. Physical testing needs a separate approved bounded
   window; driver changes need all-affected-instrument downtime.
