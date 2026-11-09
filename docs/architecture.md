# Architecture

Device -> byte transport -> APT Session -> KSC101 driver -> ShutterHub ->
Python / CLI / GUI / notebooks. There is one implementation and no service,
SDK cache, receiver worker, simulator in the examples or notebook connection manager.

- transport.py defines Route, validates connections, implements TCP/D2XX/VCP
  bytes and provides explicit informational inventory.
- protocol.py owns framing, deadlines, one receive path and terminal ambiguity handling.
- controller.py contains configuration/TOML loading, the KSC101 command driver,
  identity checks, per-serial/endpoint OS locks, persistent output uncertainty,
  policy, normalized feedback and recovery. Read operations share one serialized
  identity/fault boundary; disconnected/fault-tolerant status remains explicit.
  The owner's policy check also enforces route-specific write restrictions.

Exceptions live with their contracts: shared/protocol errors in protocol.py,
identity mismatch in controller.py and unsupported routes in transport.py. Package
imports of ShutterError and UnsupportedRoute remain the public entry points.

The control core is these three modules. GUI and package/CLI entry points remain
separate. config.py/device.py/discovery.py are removed without wrappers; import
public configuration/owner classes from thorlabs_shutter_control. Parameters
remain in TOML; unknown hub serial/firmware can be omitted (None). Known metadata
must not conflict across routes to the same host, and never substitutes for the
actual controller identity check. Configuration loading/construction remain passive.

The ordinary path is connect, get_status, release. Construction/imports are
passive. Connection verifies exact serial/model/firmware/channel count without
enable, output, mode or EEPROM commands. get_status requests identity, mode,
interlock requirement and status bits; all clients receive one flat ShutterStatus.
The private channel shares its metadata fields and adds only owner resources;
snapshots copy public fields and exclude handles/locks. Electrical readings are
never cached in host-only snapshots. External clients must migrate the old nested
schema as documented in the Python API.
An explicit raw solenoid-state diagnostic is separate from electrical feedback.

Optional update start/stop commands reuse the same session and bounded event
queue; get_events collects raw frames during an identity query. No background
receiver or motor-status decoder is added. Normal connect/status/release never
starts or stops updates or sends a hardware-disconnect command implicitly.

KEH3 docked bays use the same owner/session and qualified Manual output contract
as D2XX. The control-route check refuses VCP and KEH3 external USB OUT writes;
every other write still requires the reviewed load policy and exact controller
identity. The selected middle-bay SH05R now has actual Manual ON/OFF/readback evidence;
hub identity/recovery, other topology and independent optical acceptance remain open.
The former candidate probe/analyzer CLI and duplicate Ethernet notebook wrapper
were removed; existing captures remain records, not runtime configuration.

One per-controller lock serializes I/O. The WebUI's Stop-before-Release condition
is checked under this same lock with require_stopped=True, so another callback
cannot start output between its check and release. Ordinary close remains passive.
OS claims cover serial and endpoint across
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

Queries drain every arrived transport chunk before sending and reject queued
replies; sustained unsolicited traffic consumes the original operation deadline.
This does not solve APT's lack of transaction IDs for arbitrary delayed replies.
End-to-end deadlines use perf_counter, including lock time. No retries, fallback,
reconnect or ON replay occur. Framing/freshness failures quarantine the session;
partial/unknown writes also lose transmit alignment and block protective frames.
Recovery requires independent source protection, observed optical closure and
fresh OFF/Manual/interlock checks. Neither a command nor electrical feedback
establishes optical state, exposure timing or driver/native dispatch guarantees.
