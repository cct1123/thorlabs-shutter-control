# Documentation assets and privacy

| File | Provenance |
| --- | --- |
| [Current modern panels](gui-modern-simulation.png) | Software-only browser capture with fictional Manual/Single/Trigger devices and simulation banner; no hardware |
| [Current Trigger settings](gui-modern-trigger-settings.png) | Same modern preview with TTL settings expanded |
| [Current passive startup](gui-modern-startup.png) | Three empty panels before discovery/connection in an isolated software preview |
| [Current Auto mode](gui-modern-auto.png) | One fictional connected device in Auto; other panels unconnected |
| [Current six-panel layout](gui-modern-six-slots.png) | Six empty panels; no discovery/connection |
| [Current narrow layout](gui-modern-narrow.png) | 375px software preview with expanded TTL settings; no horizontal overflow |
| [Historical GUI startup](gui-startup.jpg) | Full-page capture of the production GUI with no serials selected; no SDK discovery or hardware connection |
| [Historical six slots](gui-six-slots.jpg) | E085 unconfigured production GUI with --slots 6; no hardware access |
| [Historical Trigger settings](gui-trigger-settings.jpg) | Same unconfigured GUI, first card expanded; displayed settings are drafts, not device readback |
| [KSC101 and SH05R](ksc101-sh05r.webp) | Unchanged manufacturer product photo, copyright Thorlabs; model labels only, not the local bench |

Product photo [source page](https://www.thorlabs.com/optical-shutters) and
[original image](https://thin01mstroc282prod.dxcloud.episerver.net/contentassets/3ba9d5dbc70a436fb4f30134096125c7/927_beamshutter_vn.webp?v=1202083916).
Current PNGs were refreshed for E122 / TEST-130. Startup and six-panel captures
are unconnected; connected mode/TTL captures use fictional software devices and
simulated state. Superseded red Kinesis-style PNGs were pruned under REQ-089; their software
validation is retained in E119. Historical JPGs show separate unconfigured application instances,
including six panels; no hardware discovery or actuation was used. All captures
are direct browser screenshots.

Live launch settings belong in project `config.py`; keep real identities out of
shared commits. Historical observations use `CONTROLLER_A`/`HUB_A` aliases. Illustrative
`192.0.2.x` addresses are documentation examples, not the bench network. Test
fixtures use explicitly fictional identities to exercise validation.

Keep unredacted logs/configuration in ignored `inputs/private/`. The private
original evidence archive and image remain there; sanitized JSON is a derivative,
not the original byte stream. Derived evidence hashes are recomputed after
sanitization. No credentials belong in docs, screenshots or diagnostic exports.

Current captures contain fictional serials only. Earlier package privacy checks
are recorded in the evidence index; no new wheel was built for this doc revision.
Earlier Git history was not rewritten and can retain previously committed data.

The original startup/TTL/six-slot JPG captures show the earlier GUI styling and
remain historical layout evidence. Current modern PNGs preserve the four
user-supplied mode layouts
with neutral panels and flat controls; no vendor logos or actual serials are copied.
