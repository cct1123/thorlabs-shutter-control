# Using the GUI

[README](../README.md) | [Setup](getting-started.md) | [API](python-api.md)

Run `uv run shutter-control`, then open [localhost:8050](http://127.0.0.1:8050/).
Startup is passive. Exclude competing owners and establish physical source
protection/interlock before operating a shutter.

![Unified USB/LAN discovery using software devices](assets/gui-unified-discovery.png)

The screenshot uses fictional identities and software feedback, not hardware.
Panels wrap to a single column on narrow displays. SLOTS controls panel count;
discovery does not resize the session or connect devices.

## Ethernet LAN configuration

One **Discover** action finds USB and Ethernet controllers. Choose a labelled
serial/route in a panel and **Connect**. LAN results include their endpoint;
Connect configures that detected route on the released panel. LAN_SCAN settings
in config.py supply the range/timeout; no transport or IP entry is needed on screen.
Optional startup SERIAL_NUMBERS/ETHERNET_ENDPOINTS remain supported.

Discovery checks configured routes and performs one shared LAN scan for all cards.
Broad scanning requires every process-owned handle released. A failed/skipped
transport warns without hiding successful results. Retained/faulted identities
and cleanup stay visible. An empty list does not establish hardware absence.
Native calls can block. Close competing owners before a full scan.

After any Discover attempt, Connect requires the target in the latest successful
subset. A stale browser serial cannot reconnect an omitted target on an old route.
Before the first Discover, startup preselection may connect. Retained handles
cannot be replaced, including after failed release. Duplicate ownership is refused.
See [KEH3 setup](ethernet-assessment.md).

## Main controls

| Control | Behavior |
| --- | --- |
| Device serial/transport | Selected detected route before Connect; retained route while owned; selector locks with a handle |
| Connect | Validate identity/route, initialize communication/polling, then read feedback; no output/mode write |
| Mode | Manual, Single, Auto, Trigger; requires fresh Inactive/Closed before changing mode |
| Open / Start | Manual requests Active as Open; other modes request Active as Start after fresh readiness reads |
| Close / Stop | Request Inactive while preserving mode; remains available with a retained faulted handle |
| Lamps | Key, application readiness, communication fault, Active and reported Open; unknown is grey |
| Readouts | Controller feedback, not independent blade/optical proof; interlock indication is informational |
| Close & disconnect | Send Close then release; errors remain visible even if release succeeds |
| Close & disconnect all | Attempt cleanup for every slot despite failures; server stays running |
| Shut down GUI & devices | Launcher only: cleanup then stop server after the response; failed cleanup keeps server available |

The GUI assumes an enabled channel. Open/Start never enables or selects a mode
implicitly. Use the [explicit setup sequence](python-api.md#connection-and-manual-control)
when needed, then release that owner before GUI connection. Single/Auto use stored
cycle settings; this GUI does not read/edit their durations or counts. Trigger
Start primes the current input behavior and may open immediately.

GUI actions read the selected panel's prerequisites and result. Other panels keep
their previous observation until refresh. Unknown mode/state/position prevents
activation. Refresh is requested every1s; serialized reads may delay clicks.
Close is not an independent emergency stop and native calls may block.

## Trigger settings

Expand **Trigger settings** to edit TRIG1/TRIG2 directions and polarity.
Expanding/collapsing and draft changes issue no hardware commands.

- Read replaces drafts with fresh settings. Routine refresh keeps drafts and the
  explicitly labelled last-read settings summary.
- Apply requires Closed/Inactive/Manual, writes settings and checks readback.
- Arm requires that baseline, key enabled and an actual configured input, then
  explicitly enables, selects Triggered and requests Active.
- Main Trigger Start instead preserves mode/enable state and rereads actual input
  settings. Drafts never authorize activation.
- Disarm requests Inactive then Manual. Close alone preserves the current mode.

Armed and reported Closed can coexist. Active-low may open with an unplugged input;
the recorded no-cable position expectation failed and remains unresolved. External
electrical response is unqualified; see [hardware evidence](hardware.md).

## Ownership and finish

All browser tabs share one hub; use one operator. Process ownership cannot exclude
another application. Closing a tab leaves hardware/server running. Use launcher
shutdown or terminal Ctrl+C for cleanup. Forced process/kernel termination may
skip cleanup. Verify closure independently.

Embedded hosts call create_app(hub, on_shutdown=callback) with a ShutterHub and an
optional nonblocking stop callback. Without that callback the GUI has no server-stop
button; the host owns its lifecycle. Restart server/kernel after source changes.
