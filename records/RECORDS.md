# Engineering records

Durable evidence and decisions. Software doubles, SDK enumeration, and physical
observations have distinct scopes. Records below were finalized 2026-09-09,
23:20 UTC. No physical shutter operation has been observed or claimed.

## E001

Kind / scope: official documentation and SDK inspection; TEST-002, REQ-002/005.
Sources: [interface notes](../docs/INTERFACE.md) link the official KSC101 Python/C#
examples, manufacturer manual and Kinesis download page. Python example source
revision: `d85b2014d12018028c3eba1f724f42e94d3c47bf`.

Method: inspect examples without executing their device-control code; extract/read
the manual and visually inspect its specification/interlock pages. Download the
official x64 Kinesis 1.14.60 package; verify its published SHA-256 and Authenticode
signature; extract an MSI administrative image into the workspace. Load its
DeviceManagerCLI/GenericMotorCLI/KCube.SolenoidCLI assemblies via Python.NET;
reflect the actual properties, method names and enum values. Compare state meanings
with the vendor KSC101 C header included in the SDK.

Expected: authentic vendor package and real KSC101 API members supporting the
required class boundary. Observed: SHA-256
`298c4cc03a6c3b4d5c174964ae9193d13baca63dab10c1595b4e9ad5d914ff05` matched;
signature valid, signer Thorlabs, Inc. SolenoidCLI file/product version
`1.14.60.27990`. .NET Framework and all selected assemblies loaded.
GetSolenoidState is distinct from GetOperatingState; enum values and health/
key properties match [test_sdk.py](../tests/test_sdk.py). Native header documents
the interlock bit 0x1000. PASS for source/API selection and reflection scope.

Local, ignored sources: `tmp/references/`, `tmp/pdfs/`, `tmp/kinesis-sdk/`.
The initial extraction-only switch produced no usable image; documented MSI
administrative extraction succeeded (log ACTION=ADMIN, return 0). No system Kinesis
driver installation or firmware modification performed. CHM extraction produced no
usable HTML; API conclusions are based on actual assembly reflection, vendor
header and official examples, not inferred CHM contents.

Limitations: loading/reflection does not validate hardware commands, exact polling
freshness, or physical feedback. The manual contains legacy APT software material;
current Kinesis APIs were taken from the SDK/examples.

## E002

Kind / scope: environment/USB inventory and real SDK discovery; TEST-003, REQ-003.
Method: inspect usual Kinesis folders; inspect connected PnP device descriptions;
execute `DeviceManagerCLI.BuildDeviceList()` and `GetDeviceList(68)`, also through
`uv run --locked shutter-control --list --kinesis-dir "tmp/kinesis-sdk/Program Files 64/Thorlabs/Kinesis"`.
Use `--cache-dir .uv-cache` on this sandbox.

Observed: only Thorlabs OPM in the usual program folders; no standard Kinesis
installation found. Connected PnP inventory had no device identified as KSC101/
Thorlabs. WMI OS query was denied, so it was not used as hardware evidence.
The real SDK returned `[]`; CLI displayed `No KSC101 devices discovered.`
with exit code 0 (enumeration completed, not a hardware PASS).

Result: BLOCKED for required physical discovery/connection. No controller serial,
shutter model or power arrangement was discovered. USB-driver readiness is
unverified; empty enumeration alone does not distinguish unavailable hardware
from connection/power/driver problems. No Connect or output command reached hardware.
Bearing: B001 in STATE.md; REQ-003..008 require operator/hardware access.

## E003

Kind / scope: software tests and packaging; TEST-001..008 (software scope only).
Configuration: Windows x64, uv 0.11.2, CPython 3.12.14, Dash 4.4.1, Plotly 7.0.0,
Python.NET 3.1.0, pytest 9.1.1; official Kinesis x64 1.14.60.27990 for the opt-in
SDK check. [validation-manifest.json](validation-manifest.json) fingerprints the
tested source/configuration and final build outputs.

Method / expected:
- `uv lock --check`, `uv sync --locked --offline`: lock consistent; environment reproducible.
- `uv run --locked ruff check src tests`, `ruff format --check src tests`: no findings.
- Set KINESIS_TEST_DIR to the extracted SDK and run
  `uv run --locked pytest -q -p no:cacheprovider`: all tests pass without physical actuation.
- `uv build --offline`: build sdist/wheel; inspect wheel for controller, GUI, CLI,
  CSS and absence of vendor DLLs/test files.

Observed: locked/offline sync passed with 39 resolved packages; lint clean, formatter
left files unchanged. Final test run: **43 passed in 0.57 s**, exit 0. Final
sdist/wheel built successfully; package contents verified. An earlier pytest cache
warning was an environment permission issue; use of the cache provider was disabled
for final validation and its failed generated cache directory was removed.

Tests demonstrate input/selection validation; no output writes during connect;
partial-connect cleanup; 20 repeated open/close cycles in a software double;
manual-mode ordering; safeguard refusal; missing-feedback timeout and recovery-close
attempt; fault latching and unknown state, including connection loss during sampling;
release even after close/polling errors or interrupted close; retained handle on
disconnect failure; context-manager error preservation; CLI shutdown on server
failure; Dash lifecycle callbacks and no command replay on refresh. The optional
test loads actual DLLs/checks SDK members and enumerates, without connecting.

Result: PASS for REQ-001 and software architecture portion REQ-002. Physical
REQ-003..008 remain BLOCKED. Software-double transitions are not observations of
the real shutter. Kinesis's own USB/cache timeout behavior remains to be measured.

## E004

Kind / scope: real-browser GUI inspection with real SDK, no device; TEST-008.
Method: run the local Dash server with the extracted SDK on 127.0.0.1:8050,
inspect rendered page, click Discover, click Connect, and inspect feedback.
Review the final compact CSS layout after reload.

Expected: passive initial state, no unintended output commands, actionable
no-device error and disabled Open/Close. Observed: Disconnected, unknown identity/
state/key/interlock; Discover showed `Found 0 device(s).`; Connect showed
`Expected one KSC101; found 0. Connect a device or explicitly select its serial number.`
Open and Close stayed disabled. Page/callback/asset requests returned HTTP 200;
layout reviewed visually. PASS for this no-device browser scope.

Server stopped after verification; no controller handle had been opened. Stopping
this no-device server is not evidence of physical shutdown behavior. Successful
connected GUI lifecycle was exercised through HTTP callbacks with a software double
in E003; its physical counterpart remains blocked.

## D001

Decision: accept the user's 2026-09-09 autonomous launch as superseding the original
initialization-only pause. Updated PROJECT.md's current scope accordingly.
Basis: explicit user instruction to begin and continue the engineering loop.
Consequence: research, reversible local implementation and software checks proceed;
physical actions remain bounded by the actual setup and AGENTS.md. Requirements
and firmware/interlock restrictions unchanged.

## D002

Decision: use a single public Python controller around official Kinesis .NET via
Python.NET; Dash only orchestrates that public interface.
Basis: E001 and the user's supported-interface/minimal-structure constraints.
Consequence: Windows/Kinesis runtime required for hardware; vendor binaries are
external prerequisites. One SDK version per process, one owner per device.
Reconsider if official KSC101 interface support or the host platform changes.

## D003

Decision: connect without explicit output/mode commands; explicit Open/Close use
Manual mode; default disconnect attempts close before release and reports failures.
Never represent a successful setter as independent physical verification.
Basis: user requirements, manufacturer mode/state semantics (E001), failure-path
software checks (E003). Recovery must preserve an unknown state after a fault.
Consequence: close on context exit/Ctrl+C is best-effort; default disconnect changes
output. A deliberate communication-only disconnect is available. Browser closure,
forced termination and USB loss do not guarantee closure. Physical acceptance
must verify the documented policy before the project can be COMPLETE.
