# Simple GUI latency delivery

## Result - REQ-105

GUI Connect and Apply TTL now use the existing combined operating/TTL snapshot
and pass that current action's result back to the callback for display. The
callback avoids an extra operating read when a completed snapshot is returned.
Other actions keep their existing feedback path. No worker, persistent cache or
new dependency was added.

| Action | Prior programmed waits | Current programmed waits | Reduction |
| --- | ---: | ---: | ---: |
| Connect | 500 ms | 250 ms | 50% |
| Apply TTL | 750 ms | 500 ms | 33% |

Values use the default 250 ms poll interval and a virtual-clock fake SDK. Native
calls, discovery, HTTP queuing, transport and mechanical time are additional;
these are not measured physical response times or maximum latency guarantees.

## Safety and readability

Connect still validates identity, route and exclusive ownership, with no Enable,
mode, output or TTL write. A failed full read remains a fault with activation
blocked and its retained handle available for cleanup. Apply still requires
Closed/Inactive/Manual before its write, rejects read failures, and compares actual
TTL feedback with the requested draft before reporting success.

The action helper returns either its completed snapshot or None. The callback
uses that result only for the selected panel during the current event. Driver
contracts, polling intervals, discovery, other action paths, layout, normal workflow messages and
cleanup policy are retained. The existing [developer walkthrough](../docs/architecture.md#developer-walkthrough)
explains the flow; the new comments explain why feedback is shared.

## Validation and delivery

E148 / TEST-158 validates Connect, committed separately as 448b6b4. E149 / TEST-159
records Apply and final integrated validation in the second implementation commit.
The focused timing tests first failed with the old waits, then passed with the
intended reductions. The essential suite covers USB/LAN, one/three-panel GUI,
four modes, TTL, identity/ownership, failure/cleanup and both notebook workflows.
Final source and extracted wheel each pass **26 tests**. Package/source bytes,
README/import origin, lint/format and local documentation checks pass.

A 59-callback comparison preserves all browser responses, discovery calls and
non-target device-call sequences. Request sets for Connect/Apply are unchanged;
only their batched order and one fewer programmed wait are intentional differences.
See [current machine evidence](../records/latency-validation.json) and
[stage records](../records/RECORDS.md) for source/package results and configuration.

No real SDK, network discovery, hardware operation or physical qualification was
performed. Prior physical limits, including the active-low TTL issue, remain open.
No beginner handoff study was performed. The earlier readability delivery and its
publication are historical in [readability evidence](../records/readability-validation.json).
The user subsequently requested updated documentation and publication. README,
operator timing, setup, API and developer guidance now explain the combined reads,
retained safety checks and software-only timing scope. Documentation/publication
validation is recorded as E150 / TEST-160. The README now starts with installation
and first use; overview and trigger screenshots were refreshed from a fake-only
browser preview. No production source or styling changed in this documentation step.
