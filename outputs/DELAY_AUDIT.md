# Software delay and SDK-call audit

REQ-109 follow-up: cached ownership checks in Discover and combined Read TTL /
known-Trigger prerequisites are now implemented; GUI refresh is now 100 ms.
See [delivery](REPORT.md) and [current validation](../records/gui-feedback-validation.json).
The audit below retains its REQ-108 snapshot, including the former 1 s interval
and then-proposed GUI reductions. Discovery completeness/metadata work remains open.

2026-10-27; REQ-107 audit and REQ-108 implementation. Reviewed the working tree
at HEAD e01054c431bc128a1ac1543e809569e26fcb1919, including the pending LAN rename.
Runtime/test/notebook hashes identify the exact pre-change and final sources in
[audit evidence](../records/delay-audit.json) and
[removal validation](../records/delay-removal-validation.json).

The largest fixed feedback cost was the driver's unconditional 250 ms wait after
each request group. Those three sleep sites are now removed. Remaining dominant
software delays are discovery completion policy and serialized native work.
No real device, SDK device method, network scan or actuation was executed.

## Scope and method

Inspected all five maintained production Python files, four test files, GUI CSS,
both notebook code paths, configuration, package metadata and current operating
docs. Environment/vendor binaries, private inputs and historical diagnostic
scratch are outside maintained application source. Tests and notebooks replace
the SDK loader before any device operation.

Used tests/conftest.py's fictional USB/LAN devices, virtual clock, and the actual
Dash Flask callback request helper. Instrumented device and manager methods and
sleep timestamps. The 81 observations cover both transports, all four modes,
TTL actions, direct getters, 1/2/3/6-panel refresh, discovery and both notebooks.
Every fake method takes zero virtual time: results count requested software
waiting, not SDK overhead or physical response. Counts omit SDK property accesses
and provider/comspec accessors. Raw traces/probes remain in ignored
tmp/delay-audit; the compact evidence retains hashes, call counts and timing.

## Findings and changes

1. **Fixed feedback waits were coupled to SDK polling, without acknowledgement.**
   In controller.py, `_read_status(include_triggers=False)`,
   `_read_trigger_config()` and `_get_value()` each slept polling_ms/1000 before
   getters. Defaults added 250 ms per group, configurable from 100 to 1,000 ms.
   Full snapshots used the TTL helper's one sleep, rather than two sleeps.
   These three delays are removed. All explicit requests/getters and pre/post
   connection checks remain. Returned values are the SDK's latest available
   observations; an immediate getter may precede its request's response.

2. **Status work still serializes commands across panels.**
   gui.py's `update()` holds hub.lock for the whole callback and reads panels
   sequentially. __main__.py serves one HTTP request at a time. Previously a
   1/3/6-connected-panel refresh added 250/750/1,500 ms of sleeps; these now add
   zero feedback sleeps. Native request/getter time still serializes, and Close
   cannot preempt an in-progress callback/native call. The GUI disables its own
   refresh interval while the callback is running; unlimited periodic backlog
   in a single browser was not demonstrated. HTTP threads alone would not remove
   the hub lock. Measure real native/queue time before introducing a worker;
   command prioritization cannot interrupt an already blocked native call.

3. **Two GUI paths retain avoidable split feedback groups.**
   Read TTL reads trigger config, then `update()` reads operating feedback.
   Trigger Start reads operating prerequisites, separately reads TTL config,
   writes Active, then reads operating results. These formerly cost 500 and
   750 ms respectively. Fixed waits are now zero, but request/getter and connection
   metadata counts are unchanged. Read TTL can reuse one full snapshot, reducing
   duplicate transport checks. Trigger readiness can also use a combined full
   snapshot; account explicitly for extra TTL requests on other Open modes.
   Do not replace current prerequisite checks with old display snapshots.

4. **LAN scans always collect identities for the full timeout after finding a host.**
   `scan_lan()` exits its identity loop only when the deadline expires. An
   immediately visible identity still produced 5 s of paced collection, with
   52 fake refresh/enumeration passes and 104 transport metadata reads. The exact
   iteration count includes floating-point clock effects; it is not a hardware
   performance promise. Zero returned hosts bypass this loop. SDK range-scan time
   is additional. Default 256 addresses x 100 ms gives a 25.6 s serial timeout
   budget calculation, not an observed duration or SDK bound. No sleep removal
   was applied here: a completeness/settling policy for asynchronously appearing
   bays requires a separate choice. Returning the first identity could hide later
   bays; deleting retry pacing would produce busy polling.

5. **Selected LAN Connect waits for unrelated configured routes.**
   `_HubChannel.discover()` -> `_discover_slot()` -> whole-hub `discover()`.
   With one selected identity present and a second configured endpoint absent,
   Connect waited 5 s before creating the selected handle, versus zero discovery
   sleeps when only its present route was configured. The absent-route run made
   263 transport metadata reads across 52 discovery passes. Scope connection
   discovery to its selected route while retaining identity, route and ownership
   validation. Whole-hub discovery remains useful for explicit Discover.

6. **Unified discovery rebuilds/enumerates repeatedly and hides early results.**
   `discover_available()` performs USB discovery, optional configured-route
   discovery, then a range scan. A discovered host produces two BuildDeviceList
   calls without configured routes and three with them. Immediate identities
   still waited 5 s; an absent configured route plus the scan waited 10 s, excluding
   native work. Discovery polling calls GetTransportInfo repeatedly per candidate,
   per configured channel and again for completion/grouping. Snapshot each
   enumeration's transport metadata once, then filter/group that snapshot; preserve
   rebuild/refresh ordering and partial-discovery diagnostics. Avoid persisting
   old route metadata across commands. GUI `discover_panels()` additionally calls
   `get_operating_status()` merely to inspect has_device: cached handle state is
   sufficient for that ownership question. That formerly added 250 ms per held
   healthy panel and still adds unnecessary requests. Preserve a separate explicit
   refresh if updated feedback is wanted.

## Programmed feedback waits before and after

Normal successful actions; no discovery delay, native duration, queue/browser
time or physical motion included. USB and LAN matched in both probes.

| Operation | Before | After | Other observations |
| --- | ---: | ---: | --- |
| Direct Open / Close setters | 0 ms | 0 ms | No reads/sleeps in setters |
| Any one snapshot, TTL or scalar getter | 250 ms | 0 ms | Same requests/getters |
| Four scalar getters in sequence | 1,000 ms | 0 ms | Still four request groups; RequestStatus twice |
| GUI Connect | 250 ms | 0 ms | Discovery/initialization remain additional |
| GUI Manual / Single / Auto Open or Start | 500 ms | 0 ms | Previously 250 ms before + 250 ms after write |
| GUI Trigger Start | 750 ms | 0 ms | Previously 500 ms before + 250 ms after write |
| GUI Close / Stop | 250 ms | 0 ms | Previous wait followed Inactive write |
| GUI mode change | 500 ms | 0 ms | Prerequisite and result groups remain |
| GUI Apply TTL / Arm TTL / Read TTL | 500 ms | 0 ms | Actual TTL comparison remains on Apply |
| GUI Disarm TTL | 250 ms | 0 ms | Inactive then Manual preserved |
| Refresh, per healthy connected panel | 250 ms | 0 ms | Sequential SDK calls remain |
| Disconnect / shutdown | 0 ms | 0 ms | Native release may block; no closure verification |

## Complete application timing inventory

| Mechanism | Current treatment | Basis / limit |
| --- | --- | --- |
| Three feedback sleep sites | Removed | No prescribed polling-interval settling delay identified in installed vendor header/API signatures |
| WaitForSettingsInitialized(timeout) | Retained when initialization incomplete | SDK readiness wait, then initialization is checked again |
| StartPolling(polling_ms), default 250 ms | Retained | SDK-managed periodic status acquisition; not a Python sleep |
| Two discovery `sleep(min(0.1, remaining))` sites | Retained | Application retry pacing until identity condition/deadline; not a hardware minimum |
| Discovery timeout, default 5 s | Retained | Configured-route readiness deadline; unconditional collection window for scan |
| ScanEthernetRange open timeout, default 100 ms/address | Retained | Vendor API scan parameter; native concurrency/duration not measured |
| dcc.Interval, 1 s | Retained | GUI sampling cadence; disabled by callback running outputs |
| server.timeout, 0.5 s | Retained | Idle request-listener timeout; not a mandatory delay before incoming requests |
| Locks / native SDK methods | Retained | Potential blocking has no measured upper bound here |
| Notebook HOLD_SECONDS | Retained | Explicit experiment hold, not transport settling; USB default 1 s, LAN requires operator input |
| CSS activity reveal, 0.7 s delay + 0.12 s animation | Retained | Visual indicator only; no SDK/status blocking |

Repeated explicit request calls for status/mode/state are not all automatically
redundant: prerequisites and post-command observations have
different purposes. Background SDK polling overlaps explicit RequestStatus, but
this audit does not establish which other fields it refreshes or response freshness.
Do not remove request types, route checks, polling, or initialization on that basis.

## Validation and remaining work

E152 / TEST-162: pre-change 26 source tests passed; 81 observations recorded.
E153 / TEST-163: the focused seven-getter no-delay check first failed with 1.75 s
added virtual time; final suite passes 27 tests. Before/after probes preserve
recorded SDK method calls in all 81 scenarios; only sleep events/timestamps change.
Runtime lint/format, documentation and final evidence checks are recorded in
delay-removal-validation.json. No new wheel or hardware qualification.

Installed primary references inspected without calling a device: Kinesis
Thorlabs.MotionControl.KCube.Solenoid.h (RequestStatus/GetStatusBits and operating/
trigger request/get pairs) and reflection-only .NET API metadata. They expose
requests/getters and SDK initialization/polling, without prescribing these Python
feedback sleeps. The header describes status getters as latest-received values.
Opaque native request implementations were not proven synchronous, and the
installed CHM did not extract successfully. The code therefore makes no new
freshness guarantee. Physical response age/readback reliability needs a separately
authorized bench session; source/fake PASS does not establish it.

Suggested next software work: scoped selected-route discovery, fewer metadata
lookups per discovery pass, cached handle ownership checks in Discover, then
combined Read TTL/Trigger readiness reads. Define discovery completeness policy
before shortening its collection window. Measure native response and queue time
before adding concurrency or claiming a click/optical latency target.
