# Using the GUI

[README](../README.md) | [Setup](getting-started.md) | [API](python-api.md)

Set `SHUTTER_SERIAL` locally as described in the [README](../README.md#launch-and-operate).

```powershell
uv run --locked shutter-control --serial $env:SHUTTER_SERIAL --verified-interlock $env:SHUTTER_SERIAL
```

The confirmation records verified normal physical interlock/protection for this
selected serial/session only. It changes no hardware interlock setting. Startup
is passive. Visit [localhost:8050](http://127.0.0.1:8050/), then Discover/select
and Connect. Close Kinesis and other controller owners first.

![Production GUI at startup with no device selected](assets/gui-startup.jpg)

Privacy-safe capture of the real application: no controller selected, no hardware
connection. Unknown states are startup feedback, not a bench observation.

Panel count is configured at startup: `--slots N` accepts a positive integer.
The default is three or enough to fit all preselected serials. Larger layouts
wrap across rows; Discover does not resize the session or auto-connect devices.
Every CLI panel, including `--slots 1`, requires a selected serial for Connect.
For one panel, Discover selects a sole discovered device in the visible dropdown.

## Main controls

| Control/readout | Behavior |
| --- | --- |
| Connection badge/count | Healthy connected panels; a fault can retain a handle even when excluded from the count |
| Device serial | Explicit target; locked while a handle is retained |
| Discover | USB enumeration without connection/output; preserves retained identities |
| Connect | Verify serial, initialize communication/polling and read feedback; no explicit output/mode write |
| Reported state | Open, Closed or Unknown; text/color reflect controller feedback, not optical proof |
| Key/interlock | Raw SDK indication; unknown(operator verified) identifies separate session evidence |
| Open | Healthy identity/communication, enabled key and interlock readiness required; manual Open refuses Triggered mode |
| Close | Attempt Inactive, verify Closed/Inactive, select Manual, then verify; available while a handle exists, including fault |
| Readiness hint | Explains a disabled Open or indicates manual readiness |
| Action feedback | Last action/error in this browser view; ordinary refresh preserves it, reload starts a new view |
| Close & disconnect | Close then release; errors remain visible even when release succeeds |
| Close & disconnect all | Attempt every slot despite failures/interrupts; no total latency guarantee |

The active card puts state, manual controls and feedback together. Trigger
settings are collapsed initially and keyboard operable. The delayed busy cue and
aria-busy mark pending requests without disabling Close during polling. A blocking
SDK call can still delay later controls; Close is not an independent emergency stop.

## Trigger settings

![Expanded TRIG1/TRIG2 settings in the unconfigured GUI](assets/gui-trigger-settings.jpg)

The screenshot shows draft controls; its disconnected state has no device readback.

Expand **Trigger settings** to read/edit TRIG1/TRIG2. Opening/collapsing the section
issues no hardware command. Directions: disabled/input/output; polarity: high/low.

- Draft edits do not apply or arm. Ordinary refresh keeps drafts.
- Read TTL settings replaces drafts with device readback.
- Apply requires Closed/Inactive/Manual and checks returned settings.
- Arm uses device settings, requires an input and readiness, and primes Triggered/Active.
- Armed and Closed can coexist with an inactive input. Close/Disarm returns Manual/Inactive.

Arm may open immediately. A disconnected input is documented LOW, so active-low
can open without a cable. Separate actual no-cable API tests applied/armed both
ports: configuration and Disarm passed, but active-low remained reported Closed.
[TTL results](../records/ttl-summary.json) retain that FAIL. External electrical
response remains unqualified; the earlier connected-browser test used Read only.

## Ownership and finish

All browser tabs share the same hub. Use one operator; process-local duplicate
protection cannot exclude vendor software or another Python process. Refresh is
requested every1s but serialized SDK operations can take longer. Layout/readiness
checks and actual single-pair browser tests are recorded in the
[hardware summary](../records/hardware-validation.json).

Finish with Close & disconnect all, verify the reported result and physical
closure as required by the bench procedure, then normal terminal Ctrl+C. Closing
a tab or force-killing the process does not perform orderly shutdown.

## Six-panel example

![Unconfigured six-slot GUI](assets/gui-six-slots.jpg)

Started with `--slots 6`; all panels remain unconnected. This is layout evidence,
not a six-controller hardware test.
