# Architecture

Device -> byte transport -> APT Session -> KSC101 driver -> ShutterHub ->
Python / CLI / GUI / notebooks. There is one implementation and no service,
SDK cache, receiver worker, simulator in the examples or notebook connection manager.

- transport.py selects exact D2XX, VCP or TCP routes; ethernet.py supplies TCP bytes.
- protocol.py owns framing, deadlines, one receive path and terminal ambiguity handling.
- device.py implements manufacturer requests/commands and fresh status-bit decoding.
- controller.py owns identity, locks, policy, normalized feedback and recovery.
- ownership.py provides per-serial/endpoint OS locks and persistent output uncertainty.

The ordinary path is connect, get_status, release. Construction/imports are
passive. Connection verifies exact serial/model/firmware/channel count without
enable, output, mode or EEPROM commands. get_status requests identity, mode,
interlock requirement and status bits; all clients receive the same schema.
An explicit raw solenoid-state diagnostic is separate from electrical feedback.

KEH3 docked bays use the same owner/session and qualified Manual output contract
as D2XX. The control-route check refuses VCP and KEH3 external USB OUT writes;
every other write still requires the reviewed load policy and exact controller
identity. The selected middle-bay SH05R now has actual Manual ON/OFF/readback evidence;
hub identity/recovery, other topology and independent optical acceptance remain open.
The former candidate probe/analyzer CLI and duplicate Ethernet notebook wrapper
were removed; existing captures remain records, not runtime configuration.

One per-controller lock serializes I/O; OS claims cover serial and endpoint across
processes in the same user account. These cannot exclude vendor software/other
accounts/hosts. A failed close retains handles/claims. Context exit releases
communication and preserves original errors; it never implicitly actuates output.

Qualified D2XX/docked-KEH3 writes validate mode/interlock/load limits, record uncertainty,
send once and confirm electrical output through a fresh status-bit request.
Protective callers signal cancellation before waiting for the lock; reads use
20ms slices. Cleanup has a separate deadline and visits all applicable targets.
Read-only sessions have no incidental output-cleanup obligation, even with a
configured write policy. Their faults remain visible without an output command.
Minimum OFF rest starts after electrical OFF readback, not command dispatch.
Every ON attempt invalidates the prior interval. Confirmed-safe release retires
that connection's output history; active or faulted uncertainty survives release.
Protected recovery verifies Manual/OFF/interlock before clearing stale requests
without sending output. Native Stop during an explicit mode change is reflected
in requested state, independent of the unknown native-activity feedback.

The WebUI scopes settings drafts and operator assertions to target plus owner
connection generation. New connections clear stale edits/permissions; polling
within a connection preserves drafts. A shared software callback-test helper
keeps HTTP test dispatch consistent without another runtime backend.

End-to-end deadlines use perf_counter, including lock time. No retries, fallback,
reconnect or ON replay occur. Framing/freshness failures quarantine the session;
partial/unknown writes also lose transmit alignment and block protective frames.
Recovery requires independent source protection, observed optical closure and
fresh OFF/Manual/interlock checks. Neither a command nor electrical feedback
establishes optical state, exposure timing or driver/native dispatch guarantees.
