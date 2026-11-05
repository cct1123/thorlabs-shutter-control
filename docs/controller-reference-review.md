# Controller reference review - 5 November 2026

The user selected `C:/repo/thorlabs-control` as an implementation reference. The
inspected checkout was clean at `d70f2a6e8f494516a3aed169f33bcf6775fdd982`. It was
read only; no code, tests, notebooks or device-control tools were executed there.
The reference is not a dependency, replacement owner or manufacturer authority.
No code was copied. Its project metadata declares an MIT license; no separate LICENSE file was found.
This review uses independent implementations of the supported engineering concepts.

| Reference area | Finding | Applied here |
| --- | --- | --- |
| deadline.py | Uses high-resolution monotonic timing on Windows Python 3.12 | Deadlines, OFF intervals, dispatch timestamps, fake timestamps and verification durations use perf_counter consistently; clock resolution is recorded |
| apt/frames.py | Validates known message form/length and addressing from the header; framing failures are terminal | Reject malformed identity/mode/fault headers before awaiting a body, use the SRC-001 p34 255-byte bound, retain diagnostics and refuse reuse of a failed decoder |
| link.py write failure handling | A partial/unknown write can lose the controller's command framing | Stop all further frames on that connection, including cleanup OFF, after a short/unknown-count write. A complete-but-late write or receive-only failure can still allow qualified OFF; neither proves optical closure |
| devices/ksc101.py and TRACEABILITY KSC-PERSIST | Mode changes can have a persistent effect without an explicit EEPROM command | Confirmed independently in SRC-002 p20. Require allow_persistent_mode_changes in the reviewed policy for a real transition, default false; do not rewrite an already Manual/OFF controller |
| devices/keh3.py and TRANSPORTS.md | The reference also reports missing KEH3 wire/address/identity contracts; its probe assumes a candidate stream for diagnosis only | Keep operational routes disabled. No probe was run or added as an implicit connection/fallback; exact hub/controller validation is still required |
| devices/ksc101.py state separation | Requested, controller and optical states are distinct; current interlock continuity remains undocumented | Preserve this existing separation; do not import the reference's physical-state labels as independent optical evidence |
| link.py delayed replies | Sequence/orphan tracking and quiet-period resync require assumptions about reply ordering/latency | Retain stricter session quarantine; no documented latency bound exists to justify clearing ambiguity after a quiet interval |
| transport/d2xx.py and routes.py | Explicit D2XX serial selection and documented bridge setup | Already present. Keep the optional ftd2xx transport rather than adding a second native backend. Preserve current firmware/model checks, cross-process claims and per-controller route ownership |

The reference also implements a rotation mount. That code remains outside this
shutter task. Its older DiamondGUI comments, driver inventory, simulator results
and hypothetical acceptance-file mechanism do not qualify the current shutters,
hub, firmware, optical mapping or driver arrangement. No text-only acceptance
record can enable an unsupported route in this controller.

REQ-213 / TEST-213 records the comparison and focused regressions. Tests reproduce
the former malformed-header wait, coarse-clock deadline, redundant/persistent-mode
write and partial-write cleanup behaviors, then verify their corrected behavior.
The selected controller source/wheel tests and existing DiamondGUI integration
checks were rerun for that historical reference checkpoint (E162). The current
verifier always runs the full suite and rejects source/test/tutorial/configuration
or dependency drift; see E168 and the current report. Physical acceptance remains
blocked as described in STATE.md.
