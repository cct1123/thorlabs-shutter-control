# Integrated change review

2026-10-27; REQ-110; complete pending diff against HEAD
e01054c431bc128a1ac1543e809569e26fcb1919. Reviewed REQ-106 through REQ-109 together:
LAN naming, three feedback-sleep removals, GUI read batching and 100 ms refresh.
No runtime or test source was changed during this documentation/review pass.

## Outcome

No additional confirmed code defect was found in static inspection and the current
software tests. The public API break is intentional and documented. Readiness,
route/ownership/fault checks and post-command reads remain structurally present;
that finding does not establish fresh hardware feedback after removing sleeps.

The significant open validation gap is the immediate SDK request/getter contract.
A getter may expose a previously received value. The fake responds immediately and
therefore cannot demonstrate whether a real prerequisite or settings comparison
belongs to the latest request/write. No physical qualification or response-age
bound is inferred from the passing tests. A documented acknowledgement mechanism
or authorized bench evidence is needed before asserting fresh-response behavior.

## Review by change

| Change | Review result |
| --- | --- |
| LAN capitalization | Definitions, constructors, return/field annotations and exports agree. No mixed-case aliases; extracted-wheel imports verify the intended break. |
| Feedback sleeps | Exactly the three unconditional polling-period feedback sleeps are removed. Requests/getters, connection checks and fault paths remain. Initialization and two bounded discovery retry sleeps remain. |
| Discover ownership | Uses local retained-handle state, including failed disconnects. It does not use cached feedback to authorize output. The periodic refresh remains responsible for status updates. |
| Read TTL | One full snapshot; checks errors/settings before replacing the draft; returns that event's result. Failure keeps fault/cleanup controls available. |
| Trigger Start | Cached mode selects read breadth only. Requested operating/input feedback still gates Start; changed-mode fallback obtains inputs. Actual output command is followed by a separate operating read. |
| 100 ms refresh | Interval is 100 ms for one/three-panel layouts. Callback pause is retained; the lock and single-request server preserve serialization. It is not a measured response rate. |
| Tests | USB/LAN workflows, key/input/Active/unknown/read-failure refusals, ownership after failed release, TTL mismatch and cleanup are exercised. The fake has no physical timing or delayed-response model. |

At a nominal ten refreshes per second, three explicit request types imply 30 request
calls per second per healthy connected panel, plus automatic SDK polling. This is
a source-derived call-rate calculation, not an observed bus load. Callback duration
can reduce the achieved rate; multi-panel native timing remains unmeasured. No
threading or lock weakening was introduced to hide that limit.

## Documentation corrections made

- Replaced unsupported "fresh" feedback/settings claims with requested or
  SDK-returned values, and clarified that settings comparison is not write acknowledgement.
- Replaced the README's easily misread 0 ms action timing table with distinct GUI
  cadence, SDK polling, feedback-sleep and discovery-retry mechanisms.
- Documented uppercase public LAN names and absence of compatibility aliases.
- Explained Trigger read-breadth selection, changed-mode fallback, Read TTL result
  reuse, retained discovery pacing and 100 ms callback pause.
- Rewrote the delivery report around the final system and labelled older timing/
  review evidence as historical. Screenshots remain dated illustrations of the
  unchanged layout, not timing evidence.

## Verification

Source: 40 passed in 0.69 s. Newly built/extracted wheel: 40 passed in 0.62 s.
Six application files match source byte-for-byte and wheel metadata contains the
current README. Uppercase exports, construction and passive import pass from the
extracted wheel. Ruff lint/format pass for all nine Python files. The review's
final documentation, snippet and evidence-hash checks are recorded in
[change-review-validation.json](../records/change-review-validation.json).

The isolated offline uv build initially lacked hatchling in the selected empty
workspace cache. Building through already cached hatchling 1.32.4 and its existing
cached dependencies succeeded without a download or dependency change. Package
contents were independently inspected after building.

No hardware, real SDK device method, network discovery, commit or push occurred.
The existing [physical qualification gaps](../docs/HARDWARE_VALIDATION.md) remain;
software PASS does not close them.
