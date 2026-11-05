# KEH3 Ethernet investigation and offline commissioning support

REQ-217 / TEST-217, 5 November 2026. No laboratory connection or probe was run.

The blocker is narrowed, not declared resolved: SRC-003 Rev E section 4.3 and
Figure 17 establish the hub address/port topology and the requirement to remove
USB IN for Ethernet operation. They do not establish TCP vs UDP, raw APT framing,
hub identity exchange, per-route addresses or firmware applicability. The APT
Issue 42.1 manufacturer-authored document (443 pages) was retrieved from the
mirror cited by the reference and hash-verified as
`b2a6badd7c00b3042ba383e291667e7eab10746c14c4f92cea45fc480c7304ed`.
Its full text contains no KEH3 or 40303-specific contract. Generic references to
Ethernet and rack addresses do not establish KEH3 compatibility.

The official Thorlabs Motion_Control_Examples and Light_Control_and_Manipulation_Examples
recursive inventories were inspected through the GitHub API. They contain no
KEH3 example. The BBD30X Ethernet example is for a different device and uses the
SDK; it cannot supply a KEH3 wire contract. This is a bounded search result,
not a claim that no private or future manufacturer contract exists.

The local reference's devices/keh3.py also describes raw APT as an unresolved
candidate. Its query probe is useful diagnostic structure; a matching controller
reply does not identify the hub or establish supported firmware. This project
does not adopt a JSON acceptance-file override to enable such a route.

Exact manufacturer URLs, PDF hashes, official example tree IDs, inspected reference
revision, implementation hashes and validation commands are captured in
[records/keh3-validation.json](../records/keh3-validation.json). TEST-217 passed
18 focused diagnostic tests and the full 131-case suite in both source and an
isolated installed wheel. Earlier intermittent localhost connect timeouts are
recorded there with cause unconfirmed; final passing runs do not establish KEH3
network reliability.

## Implemented preparation

`ethernet.TCPTransport` supplies bounded standard-library TCP byte access, single
send without command replay, fragmented/coalesced reads and EOF detection. It is
used only by the separate candidate diagnostic, not by the operational owner.

`keh3.analyze_capture` is pure offline analysis. `KEH3Probe` takes one exact
configured route and one explicitly chosen candidate address, claims the same
controller serial/endpoint as the shared owner, and sends exactly one HW_REQ_INFO.
There is no address scan, alternate bay, reconnect, output, mode, polling-enable,
hub reset or persistent write. The receive capture is bounded to 4096 bytes and
the end-to-end default budget is 5 s. Identity, malformed/fault/duplicate/partial
frames and late data have separate diagnostic verdicts. Late bytes are retained
as evidence but cannot count as a successful observation. Close failures retain
the handle and ownership claim for explicit retry; original and cleanup errors
are reported separately.

A candidate match reports `hub_identity_verified=false` and
`operational_route_available=false`. A wrong hub containing the expected controller
cannot be distinguished by this query, so it is never accepted for operation.
Normal ShutterHub.connect still rejects every KEH3 route before opening a socket.

## Offline use

With an explicitly configured `keh3` target and a raw binary RX capture:

```powershell
uv run --locked shutter-control --config shutters.local.toml --target beam keh3-analyze --destination 0x50 --capture capture.bin
```

0x50 here is a candidate supplied by the operator, not an established hub address.
Analysis performs no network access. Exit 0 means a candidate controller match;
it never means route qualification. Other diagnostic verdicts return exit 2.

The future live counterpart is `keh3-probe --destination <candidate>
--query-authorized` with the same explicit config/target. The flag is an operator
assertion of an already approved bounded query window, not authorization granted
by this document or by the software. Without it the probe fails before I/O.
No such window exists in this session. Protect the optical source independently
before any future commissioning and observe the manufacturer's connection rules.

## Remaining precise contract request

Obtain from Thorlabs the KEH3 developer contract for the actual hub/controller
firmware: connection type, framing/initialization, hub model/serial/firmware
identity query, bay and external-route addressing, supported KSC101 combinations,
reply ordering and reconnect behavior. Then replace the candidate interpretation
with that contract and validate wrong hub, occupied/empty/swapped bays, concurrent
controllers, shared hub loss and no replay. Capture evidence can help distinguish
competing framing hypotheses under a later approved window, but cannot replace
manufacturer support or independently observed optical behavior.
