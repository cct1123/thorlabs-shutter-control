# Engineering task for KSC101 shutter and KEH3 hub control

Date: 4 November 2026
Status: Engineering requirements
Project management: uv

## Comprehensive review (user request, 5 November 2026)

Review all pending changes together, remove obsolete implementations, fix supported
defects, simplify code and verification scripts, reconcile operator documentation,
and commit the result. Derived acceptance: preserve the shared DiamondGUI owner
surface and safety boundaries; pass full source and isolated-wheel checks plus
affected integration tests; retain unresolved physical acceptance explicitly.
This review authorizes local implementation, software verification and a local
commit. It does not authorize device operations, driver changes or publication.

## Beginner tutorials (user request, 5 November 2026)

Deliver separate beginner example notebooks for device discovery, connection,
status query, settings, shutter modes, and ON/OFF. Derived acceptance: each is
standalone, uses the current API, runs hardware-free by default, explains its
prerequisites and expected result, and gates explicit device access and writes.
Unsupported discovery/routes/modes must be identified rather than invented.
Validate offline execution and supported opt-in examples on simulated transports;
this request does not authorize physical operation.

## Implementation references

Implementation reference: [QMI Thorlabs instruments](https://github.com/QuTech-Delft/QMI/tree/main/qmi/instruments/thorlabs)

Additional implementation reference (user instruction, 5 November 2026):
`C:/repo/thorlabs-control`. Inspect its controllers, protocol and transports for
supported improvements. Manufacturer contracts and this task's acceptance criteria
remain authoritative; the reference does not grant hardware authority or expand
scope to rotation mounts.

## Objective

User addition, 5 November 2026: add explicit informational D2XX `discover` and
VCP `discover --vcp` commands equivalent to the local thorlabs-control inventory.
Keep device selection explicit and verify configured identity before control.

Develop reliable Python control of KSC101 shutter controllers connected directly by USB or through a KEH3 hub, without requiring Kinesis, APT desktop software, pythonnet, or Thorlabs SDK DLLs.

Establish direct KEH3 Ethernet communication and exact routing to each configured shutter. Deliver a reusable control interface, command-line access, verification evidence, operator documentation, and integration with the existing DiamondGUI shutter owner.

Treat application independence, Ethernet compatibility, physical shutter behavior, and Windows driver stability as separate acceptance results. Direct USB through D2XX or a virtual COM port retains an FTDI driver dependency; hub Ethernet must be validated before claiming that it removes that dependency from the Windows host.

## Sources of truth

Use the applicable manufacturer specifications, operating manuals, and developer guides as authoritative for each exact controller, hub, attached shutter, and firmware revision.

| Source | Authority |
| --- | --- |
| KSC101 and shutter specifications | Supported shutter loads, electrical limits, duty cycle, switching and exposure limits |
| KSC101 operating manual | Modes, trigger wiring, polarity, priming, local controls, interlocks, startup and recovery behavior |
| KEH3 specifications and manual | Supported devices, power limits, bay connections, Ethernet/USB operation, addressing and installation |
| Manufacturer developer and protocol guides | Commands, binary layouts, initialization, routing, replies, fault messages and firmware applicability |
| QMI Thorlabs implementation | Reference for transport separation, APT framing, message handling and software organization |

Manufacturer entry points are [KSC101](https://www.thorlabs.com/item/KSC101), [KEH3](https://www.thorlabs.com/item/KEH3), and the applicable [host controller protocol](https://www.thorlabs.com/Software/Motion%20Control/APT_Communications_Protocol.pdf). Obtain documentation for the actual attached shutter model as well.

Maintain a source register recording document revisions, URLs, applicable hardware/firmware, and relevant sections. Trace each implemented command, operating limit, and physical-state interpretation to its manufacturer source.

Record the QMI reference revision and licensing obligations. QMI is an implementation reference and must not override manufacturer documentation or establish undocumented KSC101 or KEH3 support. Resolve missing or conflicting contracts before releasing the affected behavior; obtain manufacturer clarification where necessary.

## Goals

Follow-up (5 November 2026): focus on KEH3 Ethernet, use the local reference and
manufacturer documentation to resolve the protocol blocker where supported, and
implement/validate everything possible offline. No live device or lab-network
operation is authorized by this offline work. Retain unmet contract/bench criteria.

1. Control and query each intended shutter through its exact configured identity and route.
2. Support explicit mode configuration and solenoid ON/OFF without hidden output changes.
3. Establish independently verified optical open/closed behavior and preserve interlocks.
4. Prove KEH3 Ethernet framing, discovery, addressing, routing and recovery behavior.
5. Prevent wrong-shutter commands, stale-state success, uncontrolled retries and competing owners.
6. Preserve other laboratory instruments and provide a persistent, validated driver arrangement wherever USB remains in use.
7. Make installation, verification and diagnostics reproducible through uv.

## Scope

Include one or more explicitly configured KSC101 controllers, their attached shutters, a KEH3 hub, direct USB access where selected, and direct Ethernet access through supported hub routes.

Include reusable library and command-line interfaces, automated offline verification, physical validation, and integration through the existing DiamondGUI shutter owner.

Exclude rotation mounts, other actuator families, chiller protocol changes, unrelated camera software, automatic firmware upgrades, general repository cleanup, and a new network control service. Preserve unrelated work and instrument configuration.

## Project management requirements

Use uv for Python version, environment, dependency, execution and development-tool management. Maintain pyproject.toml, a version-controlled uv.lock, declared development dependencies, and a pinned tested Python minor version compatible with the deployment environment.

Keep native transport dependencies explicit and optional where practical. Document OS drivers and native libraries separately from Python dependencies; uv does not install or repair device bindings.

All documented setup and execution workflows must use uv. Reproducible verification must reject a missing or outdated lockfile rather than silently changing dependency resolution. A clean environment must support offline imports, help and verification without Thorlabs application or SDK components.

## Device identity and route requirements

Identify every shutter by its KSC101 model and serial number. Associate logical names with explicit physical roles and transport routes established by the operator. Do not infer beam paths, shutter roles, or safe states from names or channel numbers.

For hub connections, retain hub identity, network address, selected bay or external route, and expected controller serial as separate configuration fields. Verify the actual controller identity on that exact route before output commands.

Reject missing devices, identity mismatches, duplicate assignments, empty bays and unsupported firmware. Do not select the first discovered device or silently fall back to another serial, bay, address or transport.

Discovery must be explicit and bounded. Imports, help and offline verification must not enumerate hardware, open connections, start polling or initialize application owners. Connection must not energize outputs, prime triggers, change modes, reset the hub or alter persistent settings.

## KSC101 control requirements

Provide identity, operating-mode query, controller-state query, supported fault/interlock information, explicit mode configuration, solenoid ON and solenoid OFF. Expose supported timing/cycle configuration only within manufacturer limits and the attached shutter's rating.

Define command prerequisites for each supported mode. Reject operations that conflict with the active mode or require an unapproved mode change. Any mode transition must be explicit, account for its possible output effects, and use readback where supported.

Keep persistent configuration changes separate from ordinary operation. Do not write EEPROM or change startup behavior implicitly.

Maintain requested state, controller-reported electrical state, and independently observed optical state as distinct information. Record freshness and provenance. If the hardware provides no independent blade-position feedback, expose that limitation rather than inventing confirmed optical status.

Establish the attached shutter model, wiring, energized/de-energized behavior, and intended optical safe state before presenting ON/OFF as open/closed. Enforce electrical, switching-rate, exposure and duty-cycle constraints at the shared command boundary.

Preserve manufacturer and laboratory interlocks. Software must not bypass an interlock to satisfy an output request.

## Trigger and local-control requirements

If TTL or externally triggered operation is selected, verify supported trigger modes, voltage thresholds, polarity, edge/level semantics, priming, cycle behavior and trigger-output meaning against the applicable documentation.

Verify behavior on disconnected input, power loss, power restoration, local mode changes and reconnect. Do not assume that deasserting a trigger or disconnecting a cable produces optical closure.

Define how local controls, external triggers and software share authority. Detect changes where supported and invalidate stale software assumptions. Cancellation must address any active cycle or external trigger source that could reopen the shutter, rather than only changing a cached software state.

## KEH3 control requirements

Establish the documented Ethernet connection type, port mapping, framing, addressing, initialization, firmware requirements and supported devices. A network connection alone is insufficient evidence of direct command compatibility.

Verify hub identity and controller identity for every selected route. Test occupied, empty and swapped bays, including multiple controllers of the same model. Establish external USB-route compatibility separately; do not infer it from the presence of a connector.

Observe manufacturer restrictions on USB/Ethernet operating modes, hub power and supported combinations. Do not assume that an unwrapped APT stream is accepted over TCP or that generic USB/rack addresses apply to hub routes.

Support fragmented and coalesced network data, interleaved messages, bounded connection attempts, disconnect detection and explicit reconnection. Reconnection must revalidate identities and must not automatically replay ON commands or restore an active trigger cycle.

Separate hub configuration from shutter control. Network-address changes, persistent settings, reset and firmware management must not occur implicitly. Include only documented hub configuration functions required for deployment; otherwise provide clear operator prerequisites.

Report failures per controller and for the hub as a whole. Hub loss must invalidate affected observations without claiming that attached shutters have closed. Failure on one route must not redirect commands to another shutter.

Unsupported or unresolved routes must remain unavailable and explicitly identified.

## Communication and ownership requirements

Separate transport access, APT framing and device behavior. Validate message lengths, addresses, channels and payloads. Retain complete fault details and handle fragmented reads and asynchronous messages without losing alignment where recovery is possible.

Maintain one owner and one receive path for each device connection. Serialize writes and prevent competing CLI, GUI and task handles. Define concurrency across hub routes without creating competing owners for the same controller.

Make cancellation and a validated safe-state request reachable through the active owner during long operations. Prioritize these requests over ordinary queued work. Use an initial healthy-transport dispatch target of 250 ms and measure achieved latency. Dispatch time and physical shutter-closure time must be reported separately.

Use monotonic end-to-end deadlines covering preflight, writes, response handling and polling. Validate all public arguments before I/O and reject late success. Initial configurable software defaults are 5 seconds for connection/identity, 3 seconds for ordinary queries, and a separate 5-second cleanup budget. Set cycle-operation deadlines from documented cycle duration and validated margins.

APT has no transaction identifiers. Define single-flight query handling and a policy for delayed same-type replies. Require fresh evidence for operation results; stale state or an old acknowledgement must not produce success.

## Failure and safe-state requirements

Treat partial writes, timeouts and connection loss as possibly applied output commands. Do not automatically replay output or cycle commands after an ambiguous result.

Preserve both the original error and cleanup outcome. An unconfirmed safe-state request must retain unknown physical state and block new ON or cycle-start requests until explicit recovery.

Keep bounded cancellation and a validated safe-state action available during fault lockout where the physical mapping and transport allow it. Electrical OFF is a safe-state action only when that mapping has been established. Failure of recovery must retain uncertainty.

Document the operator response to communication loss and the independent protection needed where software cannot establish the optical safe state. Handle closure, application exit, hub disconnection and controller acknowledgements must not count as proof of optical closure.

Define behavior for normal shutdown, interrupted operation, process failure, power cycling and an unavailable controller. Preserve cleanup obligations even when another controller's cleanup fails.

## Driver and application integration requirements

Maintain a device/transport matrix covering Python dependencies, native libraries, OS drivers, exact routes, firmware, verification status and rollback arrangements.

Demonstrate Thorlabs application/SDK independence separately from avoidance of Windows FTDIBUS. Do not claim that replacing application software resolves the crash mechanism.

Where USB remains selected, validate matching driver packages, device bindings and persistence. Any alternative USB stack requires validation of bridge initialization, endpoints and packet handling for the actual hardware.

Before a driver cutover, inventory current packages, loaded drivers, active serial instruments and rollback material. Use supported package-management mechanisms, preserve unrelated instruments, and do not manually replace shared driver files.

Integrate through the existing DiamondGUI shutter owner. Preserve public interfaces, logical channel mappings, exact identities/routes, task cancellation, interlocks, cleanup and fault propagation. Avoid hidden startup actuation or competing managers.

## Verification and acceptance requirements

| Area | Required evidence |
| --- | --- |
| Identity and routing | Wrong serial/model, duplicate mapping, swapped/empty bay, changed device after reconnect and wrong hub cannot reach output commands |
| Protocol | Reference frames, representative split boundaries, coalesced frames, malformed lengths, interleaved replies, wrong addresses/channels and controller faults |
| Modes and constraints | Unsupported mode transitions, invalid timing/cycle values, nonfinite inputs and duty-limit violations are rejected before output writes |
| Freshness and deadlines | Delayed same-type replies and stale state cannot produce false success; total deadlines and separately bounded cleanup are verified |
| Recovery | Partial writes, disconnects, failed safe-state requests, cancellation and repeated cleanup preserve uncertainty and prevent automatic replay |
| Multiple shutters | Concurrent requests retain exact routing; a route failure does not operate another shutter; hub failure invalidates all affected observations |
| Isolation and dependencies | Imports, help and offline verification remain hardware-free; a clean uv environment requires no Kinesis, pythonnet or Thorlabs SDK DLLs |
| Physical behavior | Independently observed opening/closure, timing, local controls, trigger behavior and interlocks match the approved configuration |
| Persistence | Reconnect, hub/controller restart and Windows reboot retain validated routing/binding without automatic output activation |

Physical testing requires an approved bounded window covering exact controllers, hub routes, attached shutters, beam configuration, permitted actions, initial states, interlocks and cleanup. Reuse that authorization within its confirmed scope; renew it when the setup, permitted actions or window changes. Driver changes require downtime for all affected instruments.

Begin with identity and state queries, then validate mode transitions and output operations in an appropriate optical setup. Establish physical switching tolerances and safe cycle counts from the actual shutter specifications before testing. Include local/TTL interactions where selected and communication loss while an output is active.

Initial persistence targets are three controlled reboot checks and ten authorized reconnect cycles. The initial endurance target is a representative 24-hour coexistence run with the intended shutter/hub connections and other serial instruments. Finalize these quantities against equipment ratings and operational constraints before execution.

Record controller/hub/shutter identity, firmware, topology, network routes, OS/driver state, dependency/code revisions, timestamps, requested and reported states, physical observations and cleanup outcomes. Distinguish offline, simulated and physical evidence.

## Delivery and completion criteria

Deliver the uv-managed control implementation, reproducible lockfile, operator documentation, manufacturer source register, command/state traceability, QMI reference/deviation record, route/driver matrix, verification results, application integration and a cutover/rollback procedure.

Report direct USB, each KEH3 Ethernet route and optional TTL operation independently. Identify which routes remove Windows FTDI dependence and which retain it.

The task is complete when every required shutter can be identified, configured, controlled and recovered through its selected route without Thorlabs application/SDK dependencies; all agreed software and physical acceptance requirements pass; interlocks and ownership are preserved; and the deployment survives the agreed reconnect, reboot and endurance tests.

Unresolved manufacturer contracts, unsupported hub routes, unconfirmed optical behavior or an unverified driver arrangement require an explicit scope decision before closure.
