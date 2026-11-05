# Reviewed direct-protocol shutter control

5 November 2026. **Software review complete; engineering deployment BLOCKED.**
All pending changes were included at the user's request. The direct APT owner
replaces the legacy Kinesis implementation, SDK discovery, old GUI/CSS/screenshots
and obsolete SDK notebook templates. No SDK fallback or second hardware manager
remains. Historical review outputs and evidence records are retained as history.
Runtime Python decreases from 2,062 to 1,702 lines against the preceding HEAD
(360 lines, 17.5%); source size is not used as a substitute for validation.

Optional D2XX/VCP transport, protocol framing, KSC101 messages, shared ownership
and application interfaces are separate modules. The core has no Python runtime
dependencies. Python 3.12, optional GUI/transports/notebooks and development tools
are managed through the checked-in uv lockfile. The DiamondGUI owner surface is
preserved; no DiamondGUI source or dependency changes were made by this review.

## Review findings and simplification

| Finding | Result |
| --- | --- |
| ON/pulse duplicated ambiguity and cleanup logic | One shared output guard; every OFF uses the priority cleanup boundary |
| A new ON retained a previous OFF success message; failed pulse OFF could display stale cleanup | New attempts invalidate earlier cleanup; failed cleanup records the current unconfirmed outcome |
| Recovery could clear a pending protective request | Recovery defers without releasing/reopening the retained handle |
| Cancelled queries accessed receive buffers before checking cancellation | Deadline/cancellation checked before transport access; expired native connections also refuse open |
| Operational/candidate identity layouts and CLI/pulse constraints duplicated | Shared identity decoder/matcher and passive public pulse validation |
| GUI launched through CLI could release communication twice | Cleanup responsibility transfers once to the GUI |
| Empty hub-only fields were accepted on USB routes | Strict rejection, including empty supplied values |
| Capture size was checked separately from an unbounded file read | Read at most 4097 bytes and reject oversized captures at the shared boundary |
| Verification had selected-suite/version assumptions and omitted tutorial/config hashes | Full suite always runs; wheel name is discovered; source/wheel bytes and stable input hashes are checked |

The four cleanup/cancellation regressions failed before their fixes and pass now.
Additional tests cover passive pulse validation, strict route fields, expired
connection budgets and GUI cleanup ownership. The redundant receive queue,
unused diagnostic conversion/receive helpers and duplicate OFF-interval state
were removed. LF formatting is explicit. See E168 / D049 in
[records](../records/RECORDS.md) for commands and scope.

## Current validation

```powershell
uv run --locked --offline --group dev --extra gui python scripts/verify.py
```

| Evidence | Result | Scope |
| --- | --- | --- |
| [Source tests](../records/offline-tests.xml) | 131 PASS, no skips | Simulated control, passive applications/tutorials, localhost TCP |
| [Exact installed-wheel tests](../records/wheel-tests.xml) | Same 131 PASS | Isolated environment without pythonnet/clr/ftd2xx/serial |
| [DiamondGUI tests](../records/diamondgui-tests.xml) | 29 PASS | Existing owner/factory/page tests; device access stubbed |
| [Reproducible verification](../records/direct-validation.json) | All phases PASS | Lock, lint/format, exact wheel parity, input hashes, clean install/help, negative lock cases |
| [KEH3 preparation](../records/keh3-validation.json) | PASS offline preparation | Source investigation, simulated identity diagnostics and local TCP; not KEH3 operation |
| [Notebook execution](../records/notebook-validation.json) | Historical six-notebook kernel run | Current saved defaults/simulated opt-in paths are retested in the full suite; repeated kernel startup remains unqualified |

Initial sandboxed pytest runs failed on Windows temp-directory permissions.
Direct fresh-interpreter runs also encountered localhost TCP connect timeouts;
the isolated failing test passed separately and the complete final verifier passed
using its uv isolated runner. These observations do not establish a timeout cause
or general Windows/network reliability. Build artifacts and pytest temporary
directories are separate. No failure was converted to a skip or physical PASS.

## Operating boundaries and remaining acceptance

Exact serial/model/firmware, one owner/receiver and explicit qualification policy
gate control. Only qualified continuous-duty Manual loads are supported. Changed
modes persist at power-up and require a separate policy permission. Interlocks
are never disabled; no hidden trigger priming, reconnect, fallback or ON replay
occurs. Electrical readback is not optical blade feedback. Close/disconnect
release communication; output cleanup is explicit.

Uncertainty persists across process exit. A partial/unknown write forbids all
later frames, including OFF, on that connection. Receive-only ambiguity can permit
best-effort qualified OFF, but cannot confirm safety. Protected recovery requires
independent source inhibition and optical observation and never replays ON.
Simulated protective dispatch meets the 250 ms test target; native latency and
physical switching remain UNTESTED. APT's arbitrary delayed same-type reply
ordering remains an unresolved protocol limit.

Direct USB retains FTDI native/OS dependencies and is physically UNTESTED; VCP is
read-only commissioning. KEH3 operational routes remain BLOCKED before socket
access. Separate [capture analysis/candidate diagnostics](../docs/keh3-offline-validation.md)
never verify hub identity or unlock control; no lab probe was run. TTL/cycles,
finite exposure/duty loads, actual optical mapping, driver persistence and the
reconnect/reboot/endurance campaign remain unqualified. No hardware, lab-network
query, binding or driver change was performed in this review.

Supply the deployment evidence package in
[STATE.md](../STATE.md#human-action-required---supply-the-deployment-evidence-package)
before preparing an approved physical test window. The local commit is authorized;
publication is outside this request. The built wheel is
`dist/thorlabs_shutter_control-1.0.0-py3-none-any.whl`.

Operator references: [setup](../docs/getting-started.md),
[API](../docs/python-api.md), [architecture](../docs/architecture.md),
[protocol traceability](../docs/INTERFACE.md), [sources](../docs/sources.md),
[route/driver matrix](../docs/hardware.md), [commissioning](../docs/HARDWARE_VALIDATION.md),
[cutover](../docs/cutover.md), [DiamondGUI](../docs/diamondgui.md), and
[beginner tutorials](../docs/examples/README.md).
