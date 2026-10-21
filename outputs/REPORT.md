# Shutter controller report

The reviewed software uses a USB-only KCubeShutter and hub-owned Ethernet routes.
Serials accept strings or integers. Open/Close send Active/Inactive only,
preserving mode and enable state. Explicit enable_device() enables the channel;
Disarm selects Inactive/Manual. Arm retains Enable/Triggered/Active.
Setters send commands and return None;
getters explicitly request feedback. Connect verifies identity without depending
on operating state0, which is reported as unknown. Writes invalidate cached state.
Shutdown attempts Close and releases every slot despite errors, without claiming
physical closure. Native SDK calls may still block.

Users manage the physical interlock externally. No driver, GUI, tutorial, notebook
or diagnostic operation gates on software interlock feedback/confirmation. The
readout and optional Python metadata remain available. Independent identity,
ownership, connection, key, operating-state and TTL prerequisites remain.

The GUI uses the current hub API, separates command messages from controller
feedback, preserves unknown states and supports connection retry. Launcher settings
are in [config.py](../src/thorlabs_shutter_control/config.py); published defaults
contain no device identity and startup is passive. No launcher interlock flag or
hardware environment/CLI configuration is required.

The [Open/Close notebook](../docs/examples/shutter_open_close_tutorial.ipynb)
has sequential cells, identity-gated error cleanup, explicit feedback reads and
separate API timings. Published outputs are cleared and repeat is disabled.
Successful Open leaves the shutter commanded Open until the Close cell runs.

## Validation and pruning

E114 / TEST-122: **186 passed, 1 skipped** against source and the extracted wheel.
Ruff check and format PASS; three-device software simulation PASS. Notebook cells,
documentation Python snippets, links and shareable-file checks are validated in
[review-publication-validation.json](../records/review-publication-validation.json).
The real-SDK test is opt-in and was skipped; this review issued no hardware
commands and did not launch a GUI.

Tests were consolidated from16 to8 modules and about half the Python lines;
representative contracts replace duplicate and exhaustive historical matrices.
[Pruning evidence](../records/test-pruning-validation.json) records the retained
coverage and generated-file inventory. Environment, Git, private records and lab
data are preserved. Old validation counts and hashes are historical checkpoints.

## Hardware scope and operation

Historical single-pair USB/browser evidence and user-observed motion are retained.
Changed command/GUI paths need bench revalidation. Cube Ethernet, actual KEH6/
multiple pairs, electrical TTL, physical recovery and calibrated timing remain
unqualified. The active-low no-cable expectation failure is unresolved; see the
[TTL summary](../records/ttl-summary.json). Software simulation cannot resolve it.

Start with [setup](../docs/getting-started.md), [GUI](../docs/gui.md),
[API](../docs/python-api.md) and the [hardware procedure](../docs/HARDWARE_VALIDATION.md).
The [illustrated supervisor notebook](supervisor-notebook.html) summarizes historical
bench results with current configuration examples. Its original preview and old
Notion attachment validation remain historical; this review updates local files only.
Rebuild its self-contained HTML with `python -B outputs/render_supervisor_notebook.py`.

Publication: implementation **f2934c8** pushed to origin/main; exact remote hash
verified (E115 / TEST-123 / REQ-082).
Physical qualification remains open; no overall hardware completion is claimed.
