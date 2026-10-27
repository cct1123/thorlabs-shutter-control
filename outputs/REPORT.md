# Current system and delivery

The pending delivery includes uppercase LAN discovery types, removal of fixed
Python feedback sleeps, reduced GUI feedback work and a 100 ms background refresh
interval. Source and a newly built wheel each pass 40 software tests. This is
software validation; current hardware feedback freshness and physical timing
remain unqualified.

## Public API and feedback

The exported discovery classes are LANDevice and LANDiscovery. Their constructors,
annotations and documentation use uppercase LAN; mixed-case aliases are absent.
KCubeShutter remains the direct USB API, while ShutterHub owns slots and LAN routes.
Startup and construction remain passive.

Snapshot, TTL and scalar feedback getters request values and sample the SDK without
an added Python sleep. SDK-returned values may precede the request. Neither an
immediate state value nor a settings match acknowledges a particular request/write.
Setters still write without implicit feedback; Close/disconnect remain available
for retained faulted handles. Ownership, identity, route checks and all-slot cleanup
remain in place. No hardware action was performed for this delivery.

## GUI behavior

| Path | Current behavior |
| --- | --- |
| Discover | Enumerates routes; uses cached handle ownership to retain selections without device status requests |
| Connect | Verifies identity/route and reuses one full operating/TTL result for display; no output write |
| Read TTL | One full snapshot supplies draft replacement and display; errors preserve the draft |
| Known Trigger Start | One full prerequisite snapshot includes operating/input settings; result feedback follows the Active command |
| Changed mode | Cached mode only chooses read breadth; reported Trigger mode still requires SDK input settings before readiness passes |
| Ordinary Manual/Single/Auto Start | Operating-only prerequisite; no additional TTL request on the normal path |
| Apply TTL | Reported Closed/Inactive/Manual prerequisite, settings write and SDK-returned settings comparison |
| Background refresh | Requested every 100 ms and disabled during callbacks; SDK work remains serialized |

Automatic SDK polling remains 250 ms by default. Explicit GUI requests also occur;
these intervals do not guarantee fresh samples or 10 Hz physical updates. The two
bounded discovery retry sleeps, SDK initialization wait, native scan parameters,
hub serialization and single-request launcher remain. Native calls and discovery
can delay clicks; Close is not an independent emergency stop.

## Validation and review

E155 / TEST-165 validates the integrated working tree: 40 source tests and 40 tests
against the newly built/extracted wheel, passive uppercase exports/construction,
six package files matching source, README metadata parity, lint/format and current
documentation/evidence checks. The documentation pass changes no runtime/test files.
[Integrated review](CHANGE_REVIEW.md) records the findings and limits;
[current review evidence](../records/change-review-validation.json) identifies the
final source, package and document hashes.

E154 / TEST-164's source hashes still match. Its 81 before/after scenarios preserve
48 normal callback responses, with 71 unchanged SDK sequences and 10 intended
batching/read reductions. Read TTL saves two transport lookups; known Trigger Start
saves two; Discover removes three device requests and two transport lookups per
healthy held panel. See [GUI evidence](../records/gui-feedback-validation.json).
No measured millisecond saving is attributed to those lookups.

The earlier [sleep-removal evidence](../records/delay-removal-validation.json),
[delay audit](DELAY_AUDIT.md) and [staged records](../records/RECORDS.md) retain their
revision-specific results. Earlier 250/500/750 ms wait values and 1 s GUI cadence
are historical. The user subsequently requested commit/push. Delivery commit
54619a01361998ff7edf08063fa01f90125ca71d was pushed normally to existing origin/main;
independent remote readback matched, with a clean checkout. This documentation-only
publication checkpoint accompanies it. E157 / TEST-167 in
[records](../records/RECORDS.md) records verification. TEST-165 document hashes
identify the review checkpoint before publication notes; runtime/test hashes remain current.

## Remaining qualification

The software fake returns responses immediately. It cannot establish real SDK
cache age, acknowledgement of a TTL write, transport throughput, optical timing,
electrical TTL behavior or bench safety. Removal of sleeps did not supply a response
acknowledgement mechanism. Existing active-low no-cable TTL observations remain
unresolved. Follow the separately authorized [commissioning procedure](../docs/HARDWARE_VALIDATION.md)
for physical qualification, with current configuration and independent observations.
