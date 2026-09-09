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
