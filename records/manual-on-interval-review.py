"""Software-only Manual ON timing diagnostic; no hardware/network transport."""
import json
import sys
from dataclasses import asdict, replace
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from conftest import FakeTransport, config as config_fixture
from thorlabs_shutter_control import ShutterError, ShutterHub, controller
from thorlabs_shutter_control.gui import create_app, execute_action
from ui_helpers import post_callback

config = config_fixture.__wrapped__()
config = replace(config, policy=replace(config.policy, min_off_s=2, allow_persistent_mode_changes=True))
tick = [100.0]
controller.clock = lambda: tick[0]
results = {}
with TemporaryDirectory(prefix="manual-on-review-", dir=ROOT / "tmp") as folder:
    device = FakeTransport(config)
    with ShutterHub([config], transport_factory=lambda c,d: device, lock_directory=folder) as hub:
        sample, _, _ = execute_action(hub, "connect", "beam")
        app = create_app(hub)
        key = next(k for k in app.callback_map if "serial-label.children" in k)
        rendered = post_callback(app,key,{"sample":asdict(sample),"target":"beam"},"sample.data")
        results["gui_on_enabled_during_recovery"] = not rendered["on"]["disabled"]
        tick[0] = 101.06
        action_key = next(k for k in app.callback_map if "notice.children" in k)
        refused = post_callback(app,action_key,{"target":"beam","on":1},"on.n_clicks")
        results["refusal"] = refused["notice"]["children"]
        results["refusal_snapshot_electrical_state"] = refused["sample"]["data"]["electrical_state"]
        results["refusal_fault"] = refused["sample"]["data"]["error"]
        results["output_frames_after_refusal"] = len(device.output_frames)
        assert "wait 0.94 s" in results["refusal"]
        assert results["output_frames_after_refusal"] == 0
        hub.get_status("beam")
        results["deadline_after_poll"] = hub._channel("beam").next_on
        assert results["deadline_after_poll"] == 102
        tick[0] = 102.01
        results["on_after_interval"] = hub.start("beam").electrical_state
        assert results["on_after_interval"] == "on"
        hub.safe_state("beam")
        tick[0] = 110
        hub.safe_state("beam")
        results["deadline_after_redundant_off"] = hub._channel("beam").next_on
        assert results["deadline_after_redundant_off"] == 112
        tick[0] = 120
        hub.set_operating_mode("beam","single")
        tick[0] = 130
        hub.set_operating_mode("beam","manual")
        results["deadline_after_return_to_manual"] = hub._channel("beam").next_on
        assert results["deadline_after_return_to_manual"] == 132
        hub.safe_state("beam")
Path(ROOT / "records/manual-on-interval-review.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
print(json.dumps(results,indent=2))
