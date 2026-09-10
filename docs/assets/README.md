# Documentation visual assets

These are browser screenshots of the actual Dash layout, callbacks and packaged
CSS, captured on 2026-09-09 using Microsoft Edge 152.0.4191.66 through Playwright.
Each PNG is **820 × 850 pixels**, browser viewport only, at scale 1. No app labels,
statuses or pixels were edited. No unrelated desktop content is included.

All captures use [simulated_demo.py](../examples/simulated_demo.py), the actual
`KSC101Controller`, and the existing fixture in `tests/conftest.py`. Kinesis is
replaced before any controller operation. `68000001` is a fictional fixture
identity, not a real serial. Source behavior and styling were unchanged.

| Asset | Reproduce after launching the demo |
| --- | --- |
| [gui-disconnected.png](gui-disconnected.png) | Fresh normal demo, before clicking Discover |
| [gui-connected-simulated.png](gui-connected-simulated.png) | Discover → Connect → Close; wait for the completed message |
| [gui-shutter-open.png](gui-shutter-open.png) | From connected state, Open; wait for Open state/message |
| [gui-error-state.png](gui-error-state.png) | Fresh `--empty` demo, Discover → Connect; wait for the found-0 error |

Run from the repository root with `uv run --locked python docs/examples/simulated_demo.py`.
For the empty case add `--empty`, using `--port 8051` if a normal demo is already
running. Use the same viewport/scale, wait for each callback to finish, and move
the pointer clear of controls before capturing. Finish with Close & disconnect
where connected, then Ctrl+C in the terminal.

Editable diagrams are Mermaid blocks in [architecture](../architecture.md),
[GUI workflow](../gui.md#normal-workflow), [hardware](../hardware.md), and the
[README](../../README.md). The hardware guide also lists useful future photos.
