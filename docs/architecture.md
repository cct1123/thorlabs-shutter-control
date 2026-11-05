# Architecture

`transport.py` owns optional native/serial byte access. `protocol.py` owns framing,
stream validation and a single-flight request/reply session. `device.py` implements
manufacturer KSC101 messages. `controller.py` owns identity, synchronization,
qualification policy, fault lockout and cleanup. CLI, optional Dash GUI and
DiamondGUI share that same owner. There is no network control service.

The normal command path validates public arguments, takes a per-controller lock,
checks identity/model/firmware on the exact handle, obtains mode/interlock/state,
checks limits, records possible output application durably, sends once and reads
back the electrical state. No cache getter can establish operation success.

Imports and constructors never enumerate/open hardware, start workers or poll.
Connections perform only documented USB bridge setup and identity requests.
They do not prime, enable, select a mode, write EEPROM or restore previous output.
The explicit `discover` command lists D2XX or VCP host metadata without opening
controllers. Connection then checks the selected configured identity; there is
no subnet scan or first-device selection. KEH3 capture analysis and the separately
authorized candidate probe cannot enable an operational route.

Each connection has one receive path and one lock. Cross-process serial/route
claims use OS file locks in the current user's persistent application-data directory. An uncertainty
file survives failed commands and process exit. Claims cannot exclude unrelated
vendor software, another user account or another host; those must be excluded by
deployment controls. Failed close retains the handle and claim.

Protective requests set the active owner's cancellation event before acquiring
its lock. Reads check cancellation in 20 ms slices; active holds wait on that
event. Multiple protective callers retain priority until the last completes.
Ordinary queued queries see cancellation before receive access or any write.
Recovery defers to a pending protective request. The initial dispatch
target is 250 ms on a healthy transport; tests measure simulated dispatch only.
USB native open/close calls are not forcibly interruptible, so bench qualification
and independent physical protection remain necessary.

Deadlines use the high-resolution monotonic `perf_counter` clock and span lock
acquisition, preflight, writes and replies. This also supplies the dispatch clock;
Python 3.12's coarser Windows `monotonic()` is not used for these measurements.
Cleanup has a new, separate budget. Late success is rejected. APT framing has no
checksum/sync marker; malformed lengths and unexpected reply families quarantine
the stream instead of guessing a new alignment. Known message forms, payload
lengths, expected reply addresses and the 255-byte protocol bound are checked
from the header before waiting for a payload. A framing error is terminal; complete
decoded frames and the malformed tail remain attached to the exception for diagnosis.
Unrelated complete asynchronous
frames are retained in a bounded diagnostic queue; fault frames retain raw bytes.

Timeout/cancellation leaves receive evidence ambiguous. A qualified OFF can still
be dispatched through the retained identity-verified USB handle when transmit
alignment is intact; that cannot establish successful readback on a poisoned stream.
A short/unknown-count write also loses transmit alignment, so no further frame is
sent on that connection, even for OFF. Independent source protection and explicit
recovery are then required. A complete but late write retains known alignment.
No
automatic output replay, transport fallback or reconnect exists. Identity mismatch
revokes even that retained output authority. All-target cleanup continues after
another target fails and reports original failures and cleanup outcomes separately.

KSC101 mode transitions have an automatically persistent effect (SRC-002 p20).
The reviewed policy must explicitly permit them. Selection of an already Manual
mode is a read-only no-op; no background path changes the mode or enables the flag.

ON and pulse share one ambiguity/cleanup guard. Pulse validation is also shared
by the CLI before connection. A new output attempt invalidates earlier cleanup
messages, and all OFF paths report the current failure or readback consistently.
Operational replies and candidate captures share one identity decoder and matcher.
