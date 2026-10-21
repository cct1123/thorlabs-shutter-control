# Shutter controller report

KCubeShutter controls one selected KSC101 through official Kinesis .NET;
ShutterHub owns a configured number of independent slots and Dash exposes their controls.
Startup is passive. Identity/communication/key guards, serial-scoped interlock
evidence, explicit output actions and best-effort cleanup remain intact.

## Demonstrated behavior and limits

| Check | Evidence and scope |
| --- | --- |
| Single-pair USB discovery/status/reconnect | Controller readback PASS; firmware 1.0.7 repaired the historical identity mismatch |
| Open/Close | Five-cycle SDK readback PASS and user-confirmed physical sequence; later production/GUI readback PASS |
| Shutdown/GUI lifecycle | Close/release/reconnect and normal Ctrl+C cleanup readback PASS; physical closure timing unmeasured |
| TTL, both ports unconnected | Settings/priming/Disarm/restoration/release PASS; active-low Open expectation FAIL on each port, still reported Closed |
| Manual positive control after TTL tests | Open/1s added hold/Close readback PASS; TTL discrepancy cause unknown |
| Ethernet cube, three actual pairs, external TTL signals/voltage, physical faults/calibrated timing | Not qualified |

[Bench index](../records/hardware-validation.json) and
[TTL observations](../records/ttl-summary.json) preserve these distinctions.
Feedback/host holds do not establish independent blade state or exposure timing.
Last E082 observation: Closed/Inactive/Manual, original input/high + output/high
restored, all handles released; GUI running with slots disconnected. This is
historical state, to be checked before future hardware operation.

## Practical use and documentation

The [hardware reference](../docs/HARDWARE_VALIDATION.md) has three commissioning
checks: connect/read; one Close/Open/hold/Close; GUI/cleanup. Reuse the GUI cycle.
Routine unchanged-bench operation is connect/read, Closed baseline, intended
operation, Close/release. Passive work needs no motion or repeated review gates.

[README](../README.md), [GUI guide](../docs/gui.md) and
[hardware guide](../docs/hardware.md) show the actual unconfigured GUI, expanded
trigger drafts and an attributed manufacturer KSC101/SH05R photo. These images
contain no selected device identities and do not claim connected-bench operation.
[Asset provenance/privacy scope](../docs/assets/README.md) describes their origin.

## Review and retained evidence

Private originals remain in ignored storage; public records use aliases and
refreshed derivative hashes. Current-file checks exclude earlier Git history.
The [evidence index](../records/RECORDS.md) preserves review and publication history.
E084 tightened TTL-helper argument validation; valid-input command sequences and
historical TTL results remain unchanged.

E087 fixes one configurable-GUI inconsistency: a one-slot ShutterHub now requires
an explicit dropdown selection for Connect, like larger hubs. The direct
create_app(KCubeShutter(...)) convenience API retains optional-serial behavior.
Two regression cases reproduced the defect before the fix. Current validation:
489 source and489 extracted-wheel software tests, Ruff/format and package checks
PASS. No SDK or physical hardware was accessed. Corrected the screenshot scope
and stale publication wording; removed redundant report prose. See
[review validation](../records/review-validation.json) for checks and hashes.

## Configurable count and KEH6 USB - E085

The software cap of three is removed. CLI `--slots N` or Python
`ShutterHub(slots=N)` selects any positive panel count; without a count, the
existing three-panel default grows to fit more preselected serials. Distinct
identity/ownership guards and all-slot cleanup remain intact. Independent
six/nine-device software lifecycle tests and actual empty-GUI layout captures
exercise the extension. There is no claim of unlimited physical capacity,
parallel control or bounded total polling/shutdown time.

KEH6 USB compatibility is expected from per-cube SDK addressing and the official
six-bay hub specification; actual KEH6/multiple-pair hardware remains untested.
KEH6 Ethernet is not generalized from KEH3. The historical single-pair and TTL
observations above are unchanged. Latest README privacy section is removed as
requested; current documentation/evidence cleanup remains scoped to current files.

E086 records the prior implementation a6b9e68 and publication checkpoint c9c45c2.
Follow-up publication is recorded in E088; physical qualification gaps above
remain open.
