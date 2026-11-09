"""A readable electrical sample must not hide a persistent owner fault."""

import pytest
from ui_helpers import post_callback

from thorlabs_shutter_control.gui import create_app


@pytest.mark.parametrize("action", ["connect", "read", "poll", "release"])
def test_persistent_fault_remains_in_both_notices_without_actuation(bench, action):
    hub, devices, _, path = bench
    journal = path / "uncertain-68000001"
    journal.write_text("Previous owner cleanup unconfirmed (software fixture)", encoding="utf-8")
    hub.connect("beam")
    app = create_app(hub)
    key = next(key for key in app.callback_map if "notice.children" in key)
    prop = "n_intervals" if action == "poll" else "n_clicks"
    response = post_callback(app, key, {"target": "beam", action: 1}, f"{action}.{prop}")
    assert response["sample"]["data"]["error"].startswith("Persistent uncertainty:")
    assert "notice" in response  # Faults must also surface during background polling.
    message = response["notice"]["children"]
    assert "fault" in message.lower() and "recovery" in message.lower()
    assert "Previous owner cleanup unconfirmed" in message
    assert response["settings-notice"]["children"] == message
    assert journal.exists() and not devices[0].output_frames
