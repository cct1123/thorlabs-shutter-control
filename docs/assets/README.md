# Documentation assets and privacy

| File | Provenance |
| --- | --- |
| [GUI startup](gui-startup.jpg) | Full-page capture of the production GUI with no serials selected; no SDK discovery or hardware connection |
| [Six slots](gui-six-slots.jpg) | E085 unconfigured production GUI with --slots 6; no hardware access |
| [Trigger settings](gui-trigger-settings.jpg) | Same unconfigured GUI, first card expanded; displayed settings are drafts, not device readback |
| [KSC101 and SH05R](ksc101-sh05r.webp) | Unchanged manufacturer product photo, copyright Thorlabs; model labels only, not the local bench |

Product photo [source page](https://www.thorlabs.com/optical-shutters) and
[original image](https://thin01mstroc282prod.dxcloud.episerver.net/contentassets/3ba9d5dbc70a436fb4f30134096125c7/927_beamshutter_vn.webp?v=1202083916).
Screenshots show the default three-panel layout, expanded trigger settings and
an explicitly configured six-panel layout. Each was captured from a separate
unconfigured application instance;
no image editing, synthetic hardware state or actuation was used.

Live launch settings belong in project `config.py`; keep real identities out of
shared commits. Historical observations use `CONTROLLER_A`/`HUB_A` aliases. Illustrative
`192.0.2.x` addresses are documentation examples, not the bench network. Test
fixtures use explicitly fictional identities to exercise validation.

Keep unredacted logs/configuration in ignored `inputs/private/`. The private
original evidence archive and image remain there; sanitized JSON is a derivative,
not the original byte stream. Derived evidence hashes are recomputed after
sanitization. No credentials belong in docs, screenshots or diagnostic exports.

The privacy review covers current files, including assets and the wheel contents.
Earlier Git history was not rewritten and can retain previously committed data.
