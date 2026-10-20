# thorlabs-shutter-control

Human-authored project definition.

## Engineering objective

Develop a reliable Python control program for a Thorlabs KSC101 K-Cube Solenoid
Controller and connected optical shutter. Provide a simple reusable controller
class, reliable open/close control, connection and status handling, and a
lightweight Plotly Dash GUI for manual control. Keep the structure clean for
later integration into larger laboratory-control software.

## Requirements / acceptance criteria

### Controller

- Support connect, disconnect, device identification, shutter open/close,
  state/status queries where available, safe shutdown, and clear communication
  error handling.
- Refine the exact internal API after studying the KSC101 interface.

### GUI

- Show connection status, device identity / serial number, shutter state where
  available, Open and Close buttons, and status/error messages.
- Keep the GUI simple and functional; all hardware control goes through the
  controller class, with no Thorlabs-specific control logic in the GUI.

### Validation

- Ultimately validate on physical hardware: discovery/connection, open, close,
  repeated open/close operation, disconnect/reconnect, error handling, defined
  shutdown behavior, and GUI operation through the controller class.
- Successful software calls alone do not prove physical shutter operation.

## Constraints

- Use Python, `uv` for environment and dependency management, `pyproject.toml`,
  and `uv.lock`.
- Use Plotly Dash for the GUI and keep the hardware interface behind a simple
  controller class.
- Prefer official Thorlabs-supported APIs/libraries where practical. Keep the
  implementation minimal and avoid unnecessary abstractions.
- When implementation begins, research official Thorlabs documentation and
  supported software interfaces autonomously; make routine reversible
  engineering decisions autonomously.
- Do not invent missing hardware details or bypass hardware interlocks or safety
  mechanisms.
- Do not modify firmware without explicit approval.

## Available system

- Known, as supplied: Thorlabs KSC101, compatible Thorlabs optical shutter, and
  USB-connected control computer.
- Unknown until discovered or supplied: device serial number, exact shutter
  model, power configuration, installed Kinesis version, and current device /
  shutter state. Hardware has not been inspected or validated.

## Current scope

Autonomous implementation was followed by a user-requested hardware-readiness
audit on 2026-09-09. Finish software review and preparation, then stop at
AWAITING_HUMAN_REVIEW. Do not communicate with or actuate the physical KSC101
until the user approves the staged hardware-validation launch. Requirements and
the engineering constraints above remain unchanged.

### Documentation follow-up

The user's subsequent documentation-only request in [prompt log.txt](prompt%20log.txt)
authorizes a polished README, supporting user guides, actual simulated GUI
screenshots, editable architecture/workflow diagrams, verified examples and
troubleshooting. Base every claim on implementation and recorded evidence. Keep
simulation prominent and physical validation pending. No hardware development,
device access, physical validation, architectural redesign or unrelated features
are in scope. Documentation examples and a source-checkout screenshot/demo harness
may reuse the existing test fixture; production behavior remains unchanged.
The earlier hardware-review hold remains in force after this documentation pass.

On 2026-09-15, the user requested a simple first-time-user README, then asked for
more focus on real-hardware use. For the README, prioritize installation, bench
setup, discovery, connection, operation and shutdown; keep simulation as an
optional workflow and label its evidence clearly. This changes documentation
emphasis only; the hardware-review hold and physical criteria remain unchanged.

### Code simplification follow-up

The user's subsequent cleanup request authorizes incremental code and documentation
simplification: remove redundant structure and configuration while preserving
required behavior, used public APIs, hardware boundaries, safety/error handling,
meaningful tests, packaging and reproducibility. Validate reductions with affected
tests, then the full software suite, lint/format and package checks. Report the
resulting architecture, removals, size changes and intentionally retained complexity.
This supersedes the documentation-only restriction on local implementation changes;
the hardware-review hold and physical acceptance criteria remain in force.

### Three-shutter KEH3 USB follow-up (2026-10-20)

The user requests: "Implement support for three KSC101 shutters through KEH3 USB
in one GUI, with independent controls and safe shutdown for all connected shutters.
Keep hardware access on hold."

- Provide three independent serial selections, connection/status/error displays,
  Open, Close, and Close & disconnect controls in one local GUI.
- Use one controller object per shutter, prevent competing ownership of the same
  serial within this process, and preserve per-device safeguards and fault handling.
- Provide Close & disconnect all and server-exit cleanup that attempt every slot
  even if another slot fails, with identified errors. Cleanup is sequential and
  best effort; it does not guarantee physical closure or bound hung vendor calls.
- Keep startup passive and preserve single-controller Python usage. Allow up to
  three distinct CLI serial preselection arguments without automatic connection.
- Validate using three distinct software devices, independent state/faults,
  duplicate protection and failure/interrupt cleanup. Document reproducible use.
- Intended hardware transport is KEH3 USB to individual KSC101 serial identities;
  Ethernet and synchronized actuation are outside this change. Physical hub/SDK
  enumeration, channel mapping, feedback and closure still require bench acceptance.

This authorizes local implementation and software-only validation. It does not
authorize SDK/device discovery, connection, actuation or firmware writes. The
hardware-review hold remains in force.

### Controller rename and simplification follow-up (2026-10-20)

The user requests: "rename KSC101Controller to KCubeShutter. combine the bank.py
into the controller.py. prune and simplify".

Rename the public class and current imports/examples to `KCubeShutter`, without
a legacy alias. Place `ShutterBank` alongside the driver in `controller.py` and
remove `bank.py`. Prune redundant code while retaining the three independent
GUI slots, atomic serial ownership, per-device safeguards/faults, complete
best-effort cleanup and passive startup. Validate affected behavior with
software-only regressions, packaging and current documentation. The intentional
public class rename supersedes earlier preservation of that class name;
hardware access remains on hold.

### ShutterHub construction and controller review (2026-10-20)

The user requests: "CHANGE ShutterBank to ShutterHub. simplify the construction.
review controller.py. remove any unnecessary scaffolding".

Rename the hub class and current exports/callers/documentation to `ShutterHub`
without an old-name alias. Construct the three slots directly from an optional
serial list, centralizing preselection/padding and validation. Keep explicit
controller injection for integrations and software tests. Remove unused support
code and redundant validation while preserving passive startup, independent
controls, atomic ownership, safeguards, latched faults and all-shutter cleanup.
Validate source, packaging, examples and GUI behavior using software only.
The hardware hold remains unchanged.

### GUI construction cleanup (2026-10-20)

The user requests: "review gui.py and simplify the GUI construction. remove
unnecessary scaffolding while preserving the three independent shutter controls.
keep hardware access on hold."

Simplify panel construction, component binding and callback setup while retaining
three independent serial selections/controls/status/errors, shared discovery and
all-shutter shutdown. Preserve passive startup, supported injected views, fault
and safeguard gating, retained identity, message persistence and serialized
controller access. Use software-only regression, layout and packaging checks;
the hardware hold remains in force.


### Ethernet SDK assessment request (2026-10-20)

User: "Check whether the official Kinesis or XA SDK supports controlling three
KSC101s through KEH3 Ethernet, and what code changes would be needed. Keep hardware
access on hold." Scope is research and a source-based change assessment; this
does not authorize implementation, SDK/device discovery or hardware operations.
The delivered production transport remains USB.

### TRIG1/TRIG2 TTL support (2026-10-20)

User: "Add TRIG1/TRIG2 TTL configuration, readback, and arm/disarm support to
KCubeShutter and the GUI. Keep it simple, preserve safe shutdown for all three
shutters, and keep hardware access on hold."

- Expose each port's Disabled/Input/Output mode and High/Low active polarity,
  validated against the KSC101-specific official Kinesis API.
- Separate settings drafts, explicit Apply, actual vendor readback and explicit
  Arm/Disarm. Connect and refresh must not configure or arm. Report priming
  separately from shutter position; no pin-voltage measurement is implied.
- Apply only when reported Closed/Inactive/Manual. Arm requires healthy feedback,
  enabled key/interlock and an input port; use device settings, not GUI drafts.
  Active input or active-low with a disconnected LOW input may open immediately.
- Close/Disarm/default disconnect/server exit must request Inactive, confirm
  Closed/Inactive before selecting Manual, and preserve cleanup of every slot
  after errors or interruptions. Do not restore
  Triggered mode. Do not issue persistent-settings or firmware commands.
- Validate independent settings/control, refusals, readback/failure/interrupt
  paths, GUI and packaging using software only. Prepare physical TTL acceptance
  separately. No SDK loading, device access, electrical testing or actuation is
  authorized; the hardware hold remains in force.

### Consistency review and publication (2026-10-20)

User: "review check consistency. prune and fix. commit and push".
Review and simplify the accumulated three-shutter/TTL changes, fix supported
defects, align documentation and validation evidence, then commit and push to the
configured remote. Use software-only validation and preserve the hardware hold.
