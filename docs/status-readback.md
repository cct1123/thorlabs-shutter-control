# KSC101 status-readback implementation and remaining mapping gap

## Implemented readback

The existing status query0x0429/channel1 and response0x042A contain a channel-word
and32-bit status value. The exact KSC1011.14.60 C header and .NET GetStatusBits
reference (SRC-008) document output0x1, interlock0x1000 and channel-enabled
0x80000000. The shared owner decodes the latter two into optional bool fields
interlock_status_bit/channel_enabled_bit and dates them with electrical_observed_at.
No new query, stream, SDK runtime, receiver or hardware write is added.
Unknown upper bits are retained in status_bits without interpretation. In
particular0x2000 is not a readiness/key flag.

The GUI shows Interlock flag/Channel flag as Set/Clear, Software fault as the
owner's fault record, Output ON as electrical feedback and Native request as
host Start requested/No pending request. Dated flags may display alongside a
fault; undated/disconnected/missing flags are Unknown. Healthy refusal handling
can retain previous same-session readings with their original date and a clear
historical-reading notice. These flags never authorize commands or change any
interlock policy. No pending request does not mean an external sequence is idle.

## Why Key/Ready/actual Activity are still unavailable

The verified vendor SolenoidStatus API exposes KeyEnabled, OperatingState,
SolenoidState and ToggleCount. The RevF manual p29 describes the key switch and
ready-for-use lamps but supplies no raw message/mask for them. Neither source
establishes KeyEnabled=interlock bit or Ready=channel-enabled bit.
Recorded firmware1.0.7 returned raw0 from0x04CD, whereas the C/APT Active/Inactive
values are1/2 and the .NET physical SolenoidState enum is Open1/Closed0. This
prevents treating that raw scalar as confirmed native OperatingState. Repeating
a known unsupported0x0480 query is not part of ordinary status.

An additional static inspection extracted only Solenoid DLL files from the
already-downloaded, previously signature-verified installer into a disposable
reference directory. Reflection-only metadata inspection of the managed wrapper
shows getters delegating to native CSolenoidStatus/struct accessors; it does not
provide a verified raw protocol mapping. No vendor function/constructor,
installer, driver or SDK control code was executed. The files are not dependencies.

## Exact resumption condition

Obtain a manufacturer-confirmed KSC101 firmware1.0.7 request/reply byte layout
and bit/value definitions for KeyEnabled, Is Ready and actual OperatingState /
ToggleCount, or an existing passive vendor communication capture paired with
those displayed states and their timestamps. Include model/firmware/mode, query
and reply hex, which states changed, and capture provenance. Provide existing
captures or documentation; no new hardware action is requested by this document.
The next action is to encode independent literal fixtures and implement the
verified mappings through the same driver/owner before a separately authorized
read-only comparison. Do not toggle key/interlock, prime triggers, actuate output
or launch a competing owner as an incidental diagnostic.

## Validation scope

Software-only fixture and callback tests establish decoding/wiring of the named
flags and preservation of unknown/session/fault boundaries. Saved raw replies
are historical replays, not new physical validation. The overall request to
reproduce vendor Key/Ready/actual native Activity remains PARTIAL/BLOCKED on the
mapping above; it is not claimed complete by substituting differently named flags.
