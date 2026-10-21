# Hardware acceptance and remaining tests

[Current results](../records/hardware-validation.json) | [Interface](INTERFACE.md) |
[Test tools](hardware_tests/README.md) | [Historical archive](../records/archive/README.md)

## Evidence already established

USB computer -> KEH3 left bay -> KSC10168800777/firmware1.0.7 -> SH05R.
Actual identity/status/reconnect and normal cleanup passed. The user confirmed the
five-cycle SDK Open2s/Close2s sequence. Stage5 production shutdown from Closed and
Open passed electronic readback. Stage6 actual GUI Open/Close, reconnect and normal
Ctrl+C-from-Open cleanup passed, followed by a fresh passive Closed check. E078
redesigned-GUI tests included browser Open,2.015s added visible hold, Close, read-only
trigger settings, keyboard collapse, release/reconnect and global cleanup.

These are single-pair functional/readback results, not a new independent blade
observation for each shutdown or calibrated exposure/shutdown timing. The source
and dirty-file hashes, raw responses and exact exceptions remain in the archive.
Hardware/GUI administrative holds were explicitly removed by the user. Historical
holds and failures describe earlier configurations and are not current restrictions.

## Operating contract

Before a hardware session, match selected serial/physical shutter and actual
transport, exclude competing owners, preserve normal physical interlock/source
protection and establish recovery/operating limits. Recheck transient state before
outputs. Unknown physical facts in hardware-bench.json remain unknown.

The SDK bit did not independently distinguish interlock jack conditions. Preserve
raw unknown indication; use explicit selected-serial session confirmation only
with verified normal physical circuit/protection. Key/identity/comms faults still
inhibit Open. Never infer Inactive from undefined operating0 or alias serials.

On a failure, stop the sequence without automatic replay. Retain an object if its
release failed. Output cleanup is authorized only after verified identity/status;
before that, passive release avoids writing through an unverified target. Preserve
both primary and cleanup failures and use independent physical recovery as needed.

## Stage mapping and expected evidence

| Stage | Method / expected result | Current scope |
| --- | --- | --- |
| 0 | Record installed mapping, power, protection, observation/recovery and limits | Some independent bench fields remain incomplete |
| 1 | Enumerate expected serials without Connect | USB68800777 demonstrated; no COM dependency |
| 2 | Separate passive connect/identity/status/release cycles; stable, matching feedback | Actual USB communication/reconnect demonstrated; formal full bench-record/observation criteria remain distinct |
| 3 | Status first; verified target Close/Inactive, then Manual; cleanup/release | SDK Close baseline passed; production preparation exercised in later tests |
| 4 | Open -> approved added hold -> Close; compare feedback to independent observation | Five-cycle SDK/user confirmation; later production GUI readback |
| 5 | Closed shutdown, Open -> hold -> safe_shutdown itself closes, reconnect | Production electronic readback PASS; independent closure timing unmeasured |
| 6 | Passive GUI start, correct target, Open/Close, refresh/no replay, release/reconnect, Ctrl+C from Open | Actual browser/USB readback PASS; redesigned GUI E078 |
| 7 | Dedicated cycle-count stage | Removed by user; not a PASS |
| 8 | Separately authorized Closed-state communication-loss/recovery checks | Not executed on hardware |
| 9 | Three actual pairs, distinct identities, independent/combined cleanup | Not executed; one-pair success does not satisfy three-pair acceptance |
| 10 | Approved TTL wiring/config/readback/priming/response/disarm across actual pairs | Software tests and passive setting reads only; no electrical qualification |

## Remaining physical criteria

REQ-005/007 require independent agreement/final closure evidence and any required
physical shutdown timing. Record quantity, method, reference, result, uncertainty
and validity conditions when calibration is required. Host sleeps and returned
status do not establish those measurements.

REQ-006 stage8: perform loss injection only with explicit scope, shutters physically
Closed and independently protected. Verify visible fault, Open refusal, error
preservation and explicit recovery. Do not inject open-state USB/power loss as an
incidental software test. No blind repeat after failed closure/release.

REQ-023 stage9: record three installed serial/panel/shutter mappings and per-device
baseline/readback/physical agreement. Operate independently with unchanged
neighbors, then all-slot cleanup. A hung native call is still an unresolved total
shutdown bound. Fewer than three pairs yield partial acceptance only.

REQ-031 stage10: verify manufacturer-approved TTL source/levels/polarity and actual
inactive condition before Apply/Arm. Compare settings, priming and physical
response, including disarm/cleanup on each pair. Active-low with an open LOW input
can open immediately. Do not alter powered interlock/shutter wiring. Physical TTL
requires its own operating authority and observations.

Ethernet is an independent passive branch, not a prerequisite for USB acceptance.
Post-firmware cube Ethernet discovery remains unvalidated; follow the
[endpoint qualification note](ethernet-assessment.md) without changing persistent
IP, firmware or docking as a diagnostic shortcut.

Record each run by requirement/test ID, UTC time, exact source/configuration,
identity/firmware/transport, reported and independent states, limits, errors and
release. Never promote an unexecuted/inconclusive case to PASS. The staged helpers
return readback evidence; software test doubles do not prove physical outcomes.
