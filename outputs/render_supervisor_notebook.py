"""Build the offline supervisor notebook from the published evidence, without SDK access."""

# HTML/SVG prose is kept in readable template lines.
# ruff: noqa: E501

import base64
import html
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs/supervisor-notebook.html"
REVISION = "ca0d15098e47e552518e985e71de3d2f6302eb7a"
SOURCES = {
    "S1": "records/hardware-validation.json",
    "S2": "records/ttl-summary.json",
    "S3": "records/current-hardware-tests.json",
    "S4": "records/review-validation.json",
    "S5": "docs/HARDWARE_VALIDATION.md",
    "S6": "records/RECORDS.md",
    "S7": "docs/architecture.md",
    "S8": "docs/ethernet-assessment.md",
    "S9": "docs/assets/README.md",
}


def snapshot_bytes(name):
    return subprocess.check_output(["git", "show", f"{REVISION}:{name}"], cwd=ROOT)


def read_json(name):
    return json.loads(snapshot_bytes(name))


def cite(*keys):
    return '<sup class="cite">' + " ".join(f'<a href="#{k}">{k}</a>' for k in keys) + "</sup>"


def svg(body, title, height=240, width=1000):
    marker = "arrow-" + "-".join(title.lower().split())
    return (
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="{html.escape(title)}" viewBox="0 0 {width} {height}">'
            f'<title>{html.escape(title)}</title><defs><marker id="arrow" markerWidth="8" '
            'markerHeight="8" refX="7" refY="4" orient="auto">'
            '<path d="M0 0 L8 4 L0 8 Z" fill="#64748b"/></marker></defs>' + body + "</svg>"
        )
        .replace('id="arrow"', f'id="{marker}"')
        .replace("url(#arrow)", f"url(#{marker})")
    )


def box(x, y, w, title, subtitle, color="#ecf4f2"):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="72" rx="12" fill="{color}" '
        'stroke="#c8d7d5"/>'
        f'<text x="{x + w / 2}" y="{y + 29}" text-anchor="middle" class="node">{title}</text>'
        f'<text x="{x + w / 2}" y="{y + 51}" text-anchor="middle" class="sub">{subtitle}</text>'
    )


def arrow(x1, y1, x2, y2, dashed=False):
    return (
        f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="#64748b" '
        'stroke-width="2" marker-end="url(#arrow)"'
        + (' stroke-dasharray="5 5"' if dashed else "")
        + "/>"
    )


def build():
    bench = read_json(SOURCES["S1"])
    ttl = read_json(SOURCES["S2"])
    durations = bench["results"]["production_shutdown"]["shutdown_call_s"]
    topology = ""
    for i, (a, b) in enumerate(
        [
            ("Windows PC", "Kinesis / FTDI USB"),
            ("KEH3", "Left bay"),
            ("KSC101", "Firmware 1.0.7"),
            ("SH05R", "Optical shutter"),
        ]
    ):
        x = 25 + i * 248
        topology += box(x, 32, 205, a, b)
        if i < 3:
            topology += arrow(x + 208, 68, x + 241, 68)
    topology += '<text x="500" y="140" text-anchor="middle" class="sub">Qualified bench branch: one USB controller/shutter pair; identities omitted</text>'
    topology = svg(topology, "Physical USB bench block diagram", 170)

    architecture = ""
    for i, (a, b) in enumerate(
        [
            ("Dash GUI / CLI", "Explicit operator actions"),
            ("ShutterHub", "Selection / cleanup"),
            ("KCubeShutter", "Identity / state / readiness"),
            ("Kinesis .NET", "Vendor device access"),
        ]
    ):
        x = 25 + i * 248
        architecture += box(x, 25, 205, a, b)
        if i < 3:
            architecture += arrow(x + 208, 61, x + 241, 61)
    architecture += box(510, 145, 220, "Fake devices", "Software tests only", "#f3effb")
    architecture += arrow(620, 100, 620, 140, True)
    architecture += '<text x="250" y="181" text-anchor="middle" class="sub">Lazy SDK loading; passive startup</text>'
    architecture = svg(architecture, "Software boundaries and software test substitution", 235)

    ttl_graph = '<text x="65" y="27" class="sub">Port / polarity</text><text x="465" y="27" class="sub">Expected feedback</text><text x="700" y="27" class="sub">Observed feedback</text>'
    ttl_rows = ""
    for i, r in enumerate(ttl["input_results"]):
        y = 43 + i * 52
        ok = r["result"] == "READBACK_PASS"
        color, label = ("#e0f2e9", "PASS") if ok else ("#fde8e5", "FAIL")
        ttl_graph += f'<rect x="28" y="{y}" width="944" height="43" rx="8" fill="{color}"/>'
        for x, text in [
            (65, f"IO{r['port']} / {r['polarity'].upper()}"),
            (465, r["expected"].title()),
            (700, r["reported"].title()),
            (890, label),
        ]:
            ttl_graph += f'<text x="{x}" y="{y + 27}" class="node">{text}</text>'
        ttl_rows += f"<tr><td>IO{r['port']} / {r['polarity']}</td><td>{r['expected']}</td><td>{r['reported']}</td><td>{label}</td></tr>"
    ttl_graph = svg(
        ttl_graph, "Disconnected TTL inputs: expected and observed shutter feedback", 260
    )

    shutdown = ""
    for tick in (0, 0.5, 1.0, 1.5):
        x = 180 + tick * 440
        shutdown += f'<line x1="{x}" y1="25" x2="{x}" y2="180" stroke="#e2e8f0"/><text x="{x}" y="207" text-anchor="middle" class="sub">{tick:g} s</text>'
    for i, value in enumerate(durations):
        y = 33 + i * 50
        shutdown += f'<text x="30" y="{y + 23}" class="node">Call {i + 1}</text><rect x="180" y="{y}" width="{value * 440:.2f}" height="32" rx="5" fill="#17675c"/><text x="{192 + value * 440:.2f}" y="{y + 23}" class="sub">{value:.3f} s</text>'
    shutdown = svg(
        shutdown, "Historical host shutdown call duration in seconds; not optical timing", 230
    )

    sequence = ""
    for cycle in range(5):
        x = 70 + cycle * 175
        sequence += f'<rect x="{x}" y="55" width="87.5" height="48" fill="#c7e8dc"/><rect x="{x + 87.5}" y="55" width="87.5" height="48" fill="#e6eaf0"/><text x="{x + 87.5}" y="35" text-anchor="middle" class="sub">Cycle {cycle + 1}</text>'
    sequence += '<text x="20" y="83" class="sub">State</text><text x="500" y="135" text-anchor="middle" class="sub">Each cycle: Open + 2 s added hold → Close + 2 s added hold</text><text x="500" y="159" text-anchor="middle" class="sub">Sequence schematic; command/feedback latency omitted; not a measured optical trace</text>'
    sequence = svg(sequence, "Five-cycle sequence schematic with added two-second holds", 185)

    workflow = ""
    for i, (a, b) in enumerate(
        [
            ("1 · Connect / read", "Matching identity + valid responses"),
            ("2 · Functional cycle", "Close → Open / hold → Close"),
            ("3 · GUI / cleanup", "No replay; release and normal exit"),
        ]
    ):
        x = 20 + i * 335
        workflow += box(x, 25, 290, a, b)
        if i < 2:
            workflow += arrow(x + 294, 61, x + 326, 61)
    workflow += '<text x="500" y="135" text-anchor="middle" class="sub">Reuse the functional cycle if performed in the GUI; no redundant fixed-count stage</text>'
    workflow = svg(workflow, "Simplified three-step commissioning workflow", 160)

    image = base64.b64encode(snapshot_bytes("docs/assets/gui-startup.jpg")).decode()
    source_rows = ""
    for key, name in SOURCES.items():
        source_rows += f'<tr id="{key}"><td>{key}</td><td><code>{name}</code></td></tr>'

    content = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>KSC101 shutter control — practical tutorial</title>
<style>
:root{{--ink:#1c2b32;--muted:#55656d;--teal:#17675c;--line:#dbe3e5;--paper:#fff;--bg:#f3f5f4}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}}main{{max-width:1100px;margin:auto;background:var(--paper);padding:60px 68px 70px}}header{{border-top:6px solid var(--teal);padding-top:22px}}.eyebrow{{font-size:12px;font-weight:700;letter-spacing:.16em;color:var(--teal);text-transform:uppercase}}h1{{font-size:clamp(30px,4vw,47px);line-height:1.12;letter-spacing:-.035em;max-width:850px;margin:14px 0 20px}}h2{{font-size:25px;line-height:1.25;margin:46px 0 16px;border-top:1px solid var(--line);padding-top:26px}}h3{{font-size:18px;margin:24px 0 8px}}p{{margin:12px 0}}a{{color:#0d665d;text-underline-offset:3px}}code{{font-size:.86em;background:#eef2f3;padding:2px 5px;border-radius:4px;overflow-wrap:anywhere}}.meta,.small,figcaption{{font-size:13px;color:var(--muted)}}.lead{{font-size:20px;line-height:1.5}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:24px 0}}.card{{border:1px solid var(--line);border-radius:12px;padding:18px}}.card b{{display:block;font-size:30px;line-height:1.1;color:var(--teal);margin-bottom:8px}}.card span{{font-size:13px;color:var(--muted)}}.callout{{background:#edf6f3;border-left:4px solid var(--teal);padding:16px 20px;margin:20px 0}}.warn{{background:#fff3e8;border-color:#bc6b22}}nav{{border:1px solid var(--line);padding:16px 22px;border-radius:12px;margin:25px 0}}nav a{{display:inline-block;margin:4px 17px 4px 0;font-size:14px}}figure{{margin:24px 0;padding:18px;border:1px solid var(--line);border-radius:12px;background:#fcfdfd;break-inside:avoid}}figure svg{{width:100%;height:auto;display:block}}figcaption{{margin-top:10px;line-height:1.5}}.node{{font:600 17px system-ui,sans-serif;fill:#223740}}.sub{{font:14px system-ui,sans-serif;fill:#52636d}}.cite{{font-size:11px;margin-left:5px;white-space:nowrap}}table{{border-collapse:collapse;width:100%;font-size:14px;margin:18px 0}}th,td{{text-align:left;border-bottom:1px solid var(--line);padding:11px 12px;vertical-align:top}}th{{background:#eef4f3;font-weight:650}}.table-wrap{{overflow:auto}}.tag{{font-size:11px;letter-spacing:.05em;font-weight:700;display:inline-block;border-radius:20px;padding:3px 9px;background:#e1f2e8;color:#185b42;white-space:nowrap}}.fail{{background:#fde5e2;color:#912b21}}.unknown{{background:#fff1d8;color:#855a16}}ol,ul{{padding-left:24px}}li{{margin:8px 0}}details{{border:1px solid var(--line);padding:14px 18px;border-radius:10px;margin:18px 0}}summary{{cursor:pointer;font-weight:650}}.screen{{display:block;width:100%;height:auto;border-radius:8px}}footer{{border-top:1px solid var(--line);margin-top:35px;padding-top:20px;color:var(--muted);font-size:13px}}button{{border:1px solid #a3b7b2;border-radius:7px;background:white;color:var(--teal);padding:8px 13px;cursor:pointer;font:inherit}}@media(max-width:700px){{main{{padding:26px 20px}}.cards{{grid-template-columns:1fr}}h2{{margin-top:32px}}figure{{padding:8px}}th,td{{padding:8px}}}}@media print{{body{{background:white;font-size:11px}}main{{max-width:none;padding:0}}nav,button{{display:none}}h2{{break-after:avoid}}a{{text-decoration:none;color:inherit}}details{{break-inside:avoid}}.cards{{grid-template-columns:repeat(3,1fr)}}.screen{{max-height:650px;object-fit:contain}}}}
</style></head><body><main>
<header><div class="eyebrow">Practical tutorial / USB shutter control / bench reference</div>
<h1>Control a shutter with confidence:<br>connect, operate, finish cleanly</h1>
<p class="lead">Learn the working USB path, use the GUI, interpret controller feedback and troubleshoot the limits discovered on the bench.</p>
<p class="meta">Based on the October 2026 bench session. Bench results describe an earlier implementation; current direct setters require separate feedback reads and do not verify closure. Copyable launch examples follow the current project configuration. Creating or opening this document does not access hardware.</p>
<div class="cards"><div class="card"><b>USB</b><span>One KSC101 / SH05R pair through KEH3: the demonstrated hardware path.</span></div><div class="card"><b>5 cycles</b><span>Open / 2 s hold / Close / 2 s hold: feedback passed and the user confirmed physical following.</span></div><div class="card"><b>3 steps</b><span>Commissioning now combines connect/read, one functional cycle and GUI/cleanup.</span></div></div>
<div class="callout warn"><strong>Know the scope:</strong> the single-pair USB path worked. TTL active-low behavior is unresolved; cube Ethernet, actual KEH6/multiple pairs and calibrated physical timing still need their own tests.{cite("S1", "S2", "S4", "S5")}</div>
<button onclick="window.print()">Print / save as PDF</button></header>
<nav aria-label="Notebook contents"><a href="#bench">01 Bench and architecture</a><a href="#journey">02 Diagnostic experience</a><a href="#status">03 Command interpretation</a><a href="#ttl">04 TTL results</a><a href="#gui">05 GUI and scale</a><a href="#procedure">06 Future procedure</a><a href="#delivery">07 Copyable starting points</a><a href="#review">08 Choosing your next test</a><a href="#sources">09 Further reading</a></nav>

<section id="bench"><h2>01 · System and evidence boundaries</h2>
<p>The tested configuration was Windows → USB → KEH3 left bay → KSC101 → SH05R. The cube reported firmware <strong>1.0.7</strong>, hardware revision 3; the environment was Kinesis <strong>1.14.60.27990</strong>, Python <strong>3.12.7 x64</strong> and pythonnet <strong>3.1</strong>. The FTDI/Kinesis USB interface had <strong>no assigned COM port</strong>. Discover the cube identity through the vendor SDK rather than selecting a serial COM port.{cite("S1", "S5")}</p>
<figure>{topology}<figcaption>Figure 1. Physical bench topology. Actual serials, network addresses and credentials are omitted; CONTROLLER_A/HUB_A in evidence are documentation aliases, never replacement live identities.</figcaption></figure>
<figure>{architecture}<figcaption>Figure 2. Control boundaries. The GUI delegates to the hub/driver; official Kinesis owns device communication. In-memory devices substitute for the SDK only in software tests. They cannot prove wiring, blade motion or electrical behavior.{cite("S7")}</figcaption></figure>
<div class="table-wrap"><table><thead><tr><th>Evidence class</th><th>What it establishes</th><th>What it does not establish</th></tr></thead><tbody><tr><td>Software tests</td><td>Selection, ownership, command contracts, failures, GUI callbacks, cleanup and packaging under controlled doubles.</td><td>Correct physical wiring, real blade response, voltage or timing.</td></tr><tr><td>Controller readback</td><td>Identity, communication and reported state/configuration from the actual controller.</td><td>Independent blade sensing or optical exposure measurement.</td></tr><tr><td>Human observation</td><td>The user confirmed that the five-cycle sequence physically followed the commands.</td><td>A calibrated edge-time record or a new observation for later GUI/shutdown tests.</td></tr></tbody></table></div>
<p class="small">The last recorded handoff had Closed/Inactive/Manual, restored trigger settings, released handles and a GUI with disconnected slots. It is historical state, not a present device-state claim.{cite("S3")}</p></section>

<section id="journey"><h2>02 · Diagnostic experience and turning points</h2>
<div class="table-wrap"><table><thead><tr><th>Observed bottleneck</th><th>Supported resolution / conclusion</th><th>Future lesson</th></tr></thead><tbody>
<tr><td>Looking for a shutter COM port.</td><td>Kinesis/FTDI USB discovery uses controller identities; no COM assignment was present.</td><td>Start at the actual transport and vendor discovery contract.</td></tr>
<tr><td>KSC101 firmware 1.0.6 reported a mismatched hardware identity.</td><td>The separately authorized official update to 1.0.7 repaired USB identity; identity guards stayed intact.</td><td>Do not conceal a native identity mismatch with a software alias.</td></tr>
<tr><td>USB health label remained “Connecting” despite working reads.</td><td>Assess IsConnected, communication status, identity and successful responses together.</td><td>One SDK label is insufficient evidence of health or failure.</td></tr>
<tr><td>Repeated jack/key changes did not settle interlock interpretation.</td><td>The matrix did not establish a jack-related continuity signal; key indication is separate.</td><td>Preserve unknowns and use properly scoped physical confirmation.</td></tr>
<tr><td>Both our program and Kinesis discovered only the Ethernet hub.</td><td>Those tests used cube firmware 1.0.6. No post-update cube Ethernet PASS exists.</td><td>Hub reachability and open TCP ports do not qualify the bay/controller path.</td></tr>
<tr><td>Long stage chains delayed useful functional testing.</td><td>One end-to-end USB/GUI path supplied more useful evidence; redundant gates were removed.</td><td>Repeat a read or test only when it distinguishes a concrete uncertainty.</td></tr>
</tbody></table></div>
<figure>{sequence}<figcaption>Figure 3. Tested five-cycle sequence. Five SDK cycles passed readback; the user confirmed physical following. The illustrated 20 seconds is only the sum of added holds; actual sequence duration also included commands and feedback waits.{cite("S1")}</figcaption></figure></section>

<section id="status"><h2>03 · Correct interpretation of status and commands</h2>
<p><strong>Auto is a valid mode.</strong> Undefined operating-state value 0 is not evidence of Inactive. A clear SDK interlock bit means unknown in the observed contract, not “physical interlock disabled.” The key-related <code>0x2000</code> indication is separate. The four-state jack/key experiment did not establish a software-readable jack continuity signal.{cite("S1", "S5", "S6")}</p>
<p>Explicit operator confirmation records normal physical interlock/protection for a particular object and selected serial. It is evidence, <strong>not an SDK interlock write or bypass</strong>. This optional metadata does not gate commands. Users manage the physical interlock externally; identity, key and communication checks remain. Retargeting clears the confirmation; it does not transfer to a new object/process.{cite("S7")}</p>
<ul><li><strong>Connect:</strong> discover/select, initialize communication/polling and verify identity/feedback without explicit output or mode writes.</li><li><strong>Open:</strong> current API sends Active only. Set up channel enable and Manual mode explicitly, then read feedback separately. Active follows the selected mode.</li><li><strong>Close:</strong> current API sends Inactive only and preserves mode. Use explicit Disarm for Inactive/Manual, then read feedback separately.</li><li><strong>Cleanup:</strong> after a verified connection, attempt Close and release. A failed/unverified connection gets passive release; do not write output to an unverified identity.</li><li><strong>Ownership:</strong> one process/operator owns a cube. Failed release retains the handle/claim; do not create a competing owner.</li></ul>
<p>The hub attempts cleanup for every slot and aggregates failures. Calls are sequential: a native SDK hang can prevent later attempts, so a per-feedback timeout is not a total shutdown deadline.{cite("S6", "S7")}</p>
<figure>{shutdown}<figcaption>Figure 4. Three historical production shutdown call durations: {", ".join(f"{v:.3f}" for v in durations)} seconds. These are host-call observations with controller feedback, not measured blade-closure latency or a worst-case guarantee.{cite("S1")}</figcaption></figure></section>

<section id="ttl"><h2>04 · TTL: useful partial results and a preserved failure</h2>
<p>The user reported both IO1/TRIG1 and IO2/TRIG2 connected to nothing. The autonomous single-pair test covered disabled/output settings, input polarity, priming, Disarm, settings restoration and release. Original settings were TRIG1 input/high and TRIG2 output/high; these were restored afterward.{cite("S2")}</p>
<figure>{ttl_graph}<figcaption>Figure 5. Actual disconnected-input results. High-polarity Closed expectations passed. Both low-polarity Open expectations failed: Triggered/Active was reported, but position stayed Closed, including the bounded settling check. This categorical graph is not an electrical waveform.{cite("S2")}</figcaption></figure>
<details><summary>Exact expectation matrix and diagnostic control</summary><table><thead><tr><th>Input</th><th>Expected</th><th>Reported</th><th>Outcome</th></tr></thead><tbody>{ttl_rows}</tbody></table><p>Both low cases reported status bits <code>8192</code>. A separate Manual Open → 1-second added hold → Close positive control passed electronic feedback: <code>8193 → 8192</code>. Every run ended Closed/Inactive/Manual with restoration/release. The initial IO1 mismatch was checked with a bounded 1-second read window; IO2 was tested independently. Arm was not repeatedly replayed to force an outcome.</p></details>
<div class="callout warn"><strong>Cause remains unknown.</strong> The observations do not establish a hardware defect, firmware defect, polarity defect or feedback defect. No driver workaround was added. External pulses, output voltage, independent blade observation and calibrated TTL timing remain untested. Preserve the documented precaution that active-low Arm may open immediately, even with an unplugged input.{cite("S2", "S5")}</div></section>

<section id="gui"><h2>05 · Actual user experience, scale and focused fixes</h2>
<p>The production GUI was exercised through real browser actions and actual USB feedback: manual Open/Close, refresh without replay, reconnect, passive TTL Read, global cleanup and normal Ctrl+C exit. A later GUI run recorded a 2.015-second visible added hold; that is host/browser behavior, not calibrated exposure. The controller readback and user-confirmed earlier sequence are distinct evidence.{cite("S1", "S6")}</p>
<figure><img class="screen" src="data:image/jpeg;base64,{image}" width="1264" height="957" alt="Production shutter GUI showing three unconfigured panels, disconnected state and collapsed trigger settings"><figcaption>Figure 6. Actual production GUI startup capture. No serial was selected and no SDK discovery/connection or actuation was used for this screenshot. It illustrates interface design, not a connected bench result.{cite("S9")}</figcaption></figure>
<p>Manual controls, readiness hints and faults derive from the same status snapshots. Trigger settings are collapsible; edits stay as drafts until Apply, Read replaces drafts, Arm uses device settings, and refresh does not replay action clicks. Browser closure alone does not shut down the hardware owner.{cite("S7")}</p>
<h3>Beyond three shutters</h3><p><code>SLOTS = N</code> in config.py / <code>ShutterHub(slots=N)</code> accepts a positive panel count. The default remains at least three and expands to fit supplied serials. Six/nine-device software lifecycles and empty three/six-panel browser layouts were tested. There is no application-defined count cap, but power, USB, host resources and sequential SDK latency still limit practical size.{cite("S4", "S7")}</p>
<p><strong>KEH6 USB compatibility is expected, not physically qualified.</strong> Per-cube addressing motivates that expectation; no KEH6 or multiple-pair bench PASS is claimed. KEH6 Ethernet mappings are not inferred. Full status reads include a polling wait: at default 250 ms per connected panel, six panels contribute at least 1.5 seconds of waits plus SDK time. Control is not simultaneous or synchronized.{cite("S4", "S7", "S8")}</p>
<h3>Always choose the intended controller</h3><p>Every hub GUI panel, including a single-panel session, requires a selected serial for Connect. Discover may visibly select a sole discovered device; verify it is the intended target before connecting. The direct <code>create_app(KCubeShutter(...))</code> convenience API retains the driver’s optional-serial behavior.{cite("S4", "S6")}</p></section>

<section id="procedure"><h2>06 · A simpler procedure for the next session</h2>
<figure>{workflow}<figcaption>Figure 7. Three commissioning checks replace the old stage chain. Historical “Stage 3/4/5/6” labels in records are not this new numbering. Dedicated Stage 7 was removed by the user; removal is not a PASS.{cite("S5")}</figcaption></figure>
<ol><li><strong>Connect/read:</strong> discover once, select the intended serial, connect and verify identity/communication. Stop on mismatch or failed reads. Status-only work ends with passive release and requires no motion.</li><li><strong>One functional cycle:</strong> with applicable authority/protection and current readiness, read status, explicitly enable as needed and Disarm to establish Closed/Inactive/Manual; Open and verify; hold for the approved interval; Close and verify. Record whether the blade was independently observed.</li><li><strong>GUI/finish:</strong> check refresh without action replay, release/reconnect and expected readiness. Reuse the functional cycle if it ran in the GUI. Finish with Close &amp; disconnect all and normal Ctrl+C; verify release/server exit.</li></ol>
<div class="callout"><strong>Unchanged qualified USB bench:</strong> connect/read → Closed baseline → intended operation → Close/release. No repeated full commissioning, arbitrary cycle count, complete old bench form or approval between ordinary commands. Reuse established authorization within its scope; recheck transient/changed conditions.{cite("S5")}</div>
<p>Record only reproducibility-critical facts: date/purpose, code revision, actual selected mapping in secure local configuration, transport/changed settings, action/added hold, expected versus observed feedback, independent observation, errors and release outcome. Installation/firmware, Ethernet, electrical TTL, fault injection and physical timing are separate change-driven investigations.</p>
<p>For passive Ethernet qualification, first release competing owners and use the documented LAN-only arrangement. KEH3 uses one IP: hub 40303, left/middle/right bays 40304/40305/40306 and USB OUT 40307; USB IN must be disconnected for Ethernet operation. A matching cube identity/readback and passive release are the acceptance check. Historical hub-only discovery does not prove firmware incompatibility or current cube connectivity.{cite("S8")}</p></section>

<section id="delivery"><h2>07 · Copyable starting points</h2>
<h3>Start a one-panel GUI</h3>
<pre><code>uv sync --locked
uv run --locked shutter-control</code></pre>
<p>Close Kinesis and any competing controller program first. Open <code>http://127.0.0.1:8050/</code>, click Discover, check the serial, then Connect. Startup is passive; it does not open the shutter. This project uses Windows and the installed Kinesis runtime for hardware communication.</p>
<h3>Prepare manual operation</h3>
<p>Set <code>SLOTS = 1</code> and optionally <code>SERIAL_NUMBERS</code> in <code>src/thorlabs_shutter_control/config.py</code> before launch. Users manage the physical interlock and source protection externally. There is no software interlock gate or confirmation flag. Verify the target, read status, establish Close, then perform the intended Open/approved hold/Close cycle. Keep Close and the independent bench shutdown action available.</p>
<h3>Read status from Python without moving the shutter</h3>
<pre><code>from thorlabs_shutter_control import KCubeShutter, config

cube = KCubeShutter(config.SERIAL_NUMBERS[0])  # Set the actual selected identity locally.
try:
    print(cube.connect())
    print(cube.identify_device())
    print(cube.get_status())
finally:
    cube.disconnect(close_shutter=False)</code></pre>
<p>This example releases communication only; it leaves output and mode unchanged. For an authorized operating session, use Close and normal shutdown after a verified connection. If connection identity fails, keep cleanup passive.</p>
<h3>Add panels when needed</h3>
<pre><code># In config.py: SLOTS = 6
uv run --locked shutter-control</code></pre>
<p>This configures six GUI panels; it is not a six-device hardware qualification. Select each distinct target explicitly. Allow for sequential status/cleanup time and manufacturer power/USB limits.</p></section>

<section id="review"><h2>08 · Choose the next test by the capability you need</h2>
<table><thead><tr><th>Capability</th><th>Current evidence</th><th>Next acceptance question</th></tr></thead><tbody>
<tr><td>Single-pair USB functional scope</td><td><span class="tag">DEMONSTRATED</span><br>Actual reads/control/GUI; user-confirmed five-cycle motion.</td><td>Reuse for intended operation within established bench conditions; revalidate relevant changes.</td></tr>
<tr><td>TTL active-low behavior</td><td><span class="tag fail">UNRESOLVED FAIL</span><br>Both disconnected-input low cases stayed reported Closed.</td><td>When TTL is needed, use a controlled source and independent electrical/optical observation to distinguish input level, logic and feedback.</td></tr>
<tr><td>Cube Ethernet</td><td><span class="tag unknown">UNQUALIFIED</span><br>Hub-only discovery predates the cube update.</td><td>With USB IN disconnected and one owner, does firmware 1.0.7 identify/read/release through its actual bay endpoint?</td></tr>
<tr><td>KEH6 / multiple real pairs</td><td><span class="tag unknown">SOFTWARE ONLY</span><br>Configurable count and fake-device lifecycle tested.</td><td>Do actual mappings, power/load, independence and all-slot cleanup pass on the selected hardware?</td></tr>
<tr><td>Physical shutdown / exposure timing</td><td><span class="tag unknown">UNMEASURED</span><br>Host feedback and call durations only.</td><td>Use independent blade/optical sensing if the application requires timing, then define uncertainty and validity conditions.</td></tr>
<tr><td>Physical communication loss/recovery</td><td><span class="tag unknown">UNTESTED</span></td><td>Under a specifically authorized Closed-state test, does a real loss fault and recover without stale state or duplicate ownership?</td></tr>
</tbody></table>
<p><strong>Practical priority:</strong> use the demonstrated USB path for ordinary single-shutter work; choose additional tests only when their capability is needed. If TTL integration is next, resolve its preserved failure first. If LAN control is next, do the passive post-update bay test first. Physical timing and multi-pair work need their own evidence; no broad completion claim is justified.{cite("S1", "S2", "S5", "S8")}</p>
<details><summary>Quick self-check before a new task</summary><ul><li>Do I need only the demonstrated single-pair USB operation?</li><li>Does this task actually need TTL, LAN or multiple shutters?</li><li>Is functional blade observation sufficient, or does the experiment require independently measured timing?</li><li>What changed since the last successful run, and which check would reveal a problem?</li></ul></details></section>

<section id="sources"><h2>09 · Further reading</h2>
<p>Use these repository references when you need implementation detail, fuller test results or a specific troubleshooting procedure. The tutorial keeps its explanations grounded in the recorded bench experience.</p>
<div class="table-wrap"><table><thead><tr><th>Ref</th><th>Repository reference</th></tr></thead><tbody>{source_rows}</tbody></table></div>
<p>The hardware procedure is the primary operating reference. The TTL summary preserves the unresolved low-polarity result; the Ethernet note distinguishes hub reachability from cube communication. Official manuals are linked in those guides.</p>
</section>
<footer>Practical reference based on recorded single-pair bench work. Inline figures and the original GUI screenshot are included for offline reading. The print button opens the browser print dialog. Rebuild the local copy with <code>python outputs/render_supervisor_notebook.py</code>. No hardware is accessed by the renderer or this notebook.</footer>
</main></body></html>"""
    OUTPUT.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT.name}: {len(content.encode('utf-8'))} bytes")


if __name__ == "__main__":
    build()
