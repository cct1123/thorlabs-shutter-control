# Three-shutter TTL consistency review

The reviewed system controls up to three independent KSC101 shutters through the
intended KEH3 USB path, with manual controls, TRIG1/TRIG2 settings/readback and
explicit Arm/Disarm in each GUI panel. Current software review: [E024](../records/RECORDS.md#e024) / TEST-035.
Hardware remains **AWAITING_HUMAN_REVIEW** and physical acceptance **BLOCKED**.

## Fixes and pruning

- Release now attempts Disconnect even when StopPolling is interrupted, preserves
  the interrupt/fault and retains serial ownership after failed release. Failed
  connection cleanup and interrupted Open recovery cannot report healthy state.
- Close/Disarm uses operating feedback independently of trigger settings. A TTL
  settings-read failure no longer blocks return to Manual after verified Inactive.
  Command snapshots may omit settings; get_status() requests full readback.
- Operating feedback is sampled after the TTL-request delay; connection verifies
  the returned identity matches the selected serial. Non-string serials are rejected
  before SDK access.
- Removed repeated per-port enum-map construction, duplicate recovery fault
  formatting and separate release-step handlers. The GUI retains one plain panel
  function and one serialized callback; no new backend or framework was introduced.
- Aligned API/status docs, wait-stage counts, shutdown guidance and screenshot
  provenance. Ignored pytest-generated temporary cache names without deleting files.

## Validation and limits

211 source and 211 rebuilt-wheel tests pass, including 24 review regressions. Fourteen focused cases fail
against the prior E023 wheel, demonstrating the defects reproduced by the new tests.
Ruff lint/format, uv build, dependency check and three-device simulated API pass.
Packaged Python matches source; assets are present and local caches/SDK artifacts
are excluded. Current hashes: [review manifest](../records/review-validation.json).
Earlier manifests remain historical. [E025](../records/RECORDS.md#e025) / TEST-036
verifies implementation commit [2bce513](https://github.com/cct1123/thorlabs-shutter-control/commit/2bce513baeef36a38f365c1e78c3702e30bf821e)
was pushed to origin/main and the remote reference matched.
No real SDK import, USB/network device scan, connection, actuation, electrical test,
calibration or firmware write occurred. All behavior tests use distinct fake devices.
The rendered GUI and its earlier simulated screenshot remain visually unchanged.

Close verifies Closed/Inactive before Manual; it never forces Manual while a cube
may still be primed Active. Cleanup remains sequential/best effort, with no bound
on hung SDK calls and no guarantee after power/USB loss or process termination.
TTL readback is vendor-maintained data, not pin voltage or certified freshness;
active-low may open immediately with a disconnected LOW input. Physical TEST-034
remains unexecuted. See [STATE.md](../STATE.md), [API](../docs/python-api.md),
[GUI](../docs/gui.md) and [bench procedure](../docs/HARDWARE_VALIDATION.md).

The [Ethernet assessment](../docs/ethernet-assessment.md), E022, remains research
only; production transport remains USB. Review and publication are complete;
no hardware authority is added.
