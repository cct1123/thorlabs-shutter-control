"""Validate tracked profile with simulated transport, never device/network I/O."""
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "tests"))
from conftest import FakeTransport
from thorlabs_shutter_control import ShutterError, ShutterHub, controller, load_config
from thorlabs_shutter_control.gui import execute_action

config, = load_config(root / "config/shutter.ethernet.toml")
assert config.policy.min_off_s == 0
controller.clock = lambda: 100.0  # No elapsed time can conceal a remaining pause.
results = {"min_off_s": config.policy.min_off_s, "scope": "software-only FakeTransport"}
with TemporaryDirectory(prefix="zero-off-pause-", dir=root / "tmp") as folder:
    device = FakeTransport(config)
    with ShutterHub([config], transport_factory=lambda c,d: device, lock_directory=folder) as hub:
        target = config.name
        execute_action(hub,"connect",target)
        results["immediate_on_after_connect"] = execute_action(hub,"on",target)[0].electrical_state
        execute_action(hub,"off",target)
        execute_action(hub,"off",target)
        results["immediate_on_after_repeated_off"] = execute_action(hub,"on",target)[0].electrical_state
        execute_action(hub,"off",target)
        execute_action(hub,"single",target)
        execute_action(hub,"manual",target)
        results["immediate_on_after_manual_transition"] = execute_action(hub,"on",target)[0].electrical_state
        execute_action(hub,"off",target)
        device.interlock = 2
        count = len(device.output_frames)
        try:
            execute_action(hub,"on",target)
        except ShutterError as exc:
            results["disabled_interlock_refusal"] = str(exc)
        else:
            raise AssertionError("Disabled interlock was accepted")
        assert len(device.output_frames) == count
        device.interlock = 1
        results["final_electrical_state"] = hub.get_status(target).electrical_state
        assert results["final_electrical_state"] == "off"
assert all(results[k] == "on" for k in ("immediate_on_after_connect", "immediate_on_after_repeated_off", "immediate_on_after_manual_transition"))
(root / "records/zero-off-pause-validation.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
print(json.dumps(results,indent=2))
