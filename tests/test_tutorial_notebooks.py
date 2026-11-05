"""Execute beginner examples offline and exercise opt-in paths on byte-level fakes."""

import json
from dataclasses import replace
from pathlib import Path

import pytest
from conftest import FakeTransport

import thorlabs_shutter_control as api

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((ROOT / "docs/examples").glob("0*.ipynb"))


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.stem)
@pytest.mark.parametrize("directory", [ROOT, ROOT / "docs/examples"])
def test_saved_defaults_never_access_hardware(path, directory, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Default notebook attempted device access")

    monkeypatch.chdir(directory)
    monkeypatch.setattr(api.ShutterHub, "connect", forbidden)
    monkeypatch.setattr(api.ShutterHub, "set_solenoid", forbidden)
    monkeypatch.setattr(api.ShutterHub, "set_manual_mode", forbidden)
    notebook = json.loads(path.read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    namespace = {}
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            assert cell["execution_count"] is None and cell["outputs"] == []
            exec(compile(cell["source"], str(path), "exec"), namespace)
    assert namespace["RUN_HARDWARE"] is False


@pytest.mark.parametrize(
    ("path", "partial"), [(p, False) for p in NOTEBOOKS[1:]] + [(NOTEBOOKS[-1], True)]
)
def test_live_examples_with_simulated_transport(path, partial, config, tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    config = replace(
        config, name="example", policy=replace(config.policy, allow_persistent_mode_changes=True)
    )
    devices = []
    real_owner = api.ShutterHub

    def transport_factory(c, deadline):
        fake = FakeTransport(c)
        fake.partial = partial
        if path.name.startswith("05"):
            fake.mode = 2
        devices.append(fake)
        return fake

    def owner(configs, **kwargs):
        return real_owner(
            configs, transport_factory=transport_factory, lock_directory=tmp_path, **kwargs
        )

    monkeypatch.setattr(api, "ShutterHub", owner)
    namespace = {}
    for cell in json.loads(path.read_text(encoding="utf-8"))["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = cell["source"].replace("RUN_MODE_CHANGE = False", "RUN_MODE_CHANGE = True")
        source = source.replace("RUN_OUTPUT = False", "RUN_OUTPUT = True")
        if partial and "on_result = hub.set_solenoid" in source:
            with pytest.raises(api.ShutterError) as error:
                exec(compile(source, str(path), "exec"), namespace)
            assert any("Notebook OFF cleanup failed" in note for note in error.value.__notes__)
        else:
            exec(compile(source, str(path), "exec"), namespace)
        if "configs = load_config(CONFIG)" in source:
            namespace.update(configs=(config,), selected=config, RUN_HARDWARE=True)
    assert all(device.closed for device in devices)
    frames = [frame for device in devices for frame in device.output_frames]
    if path.name.startswith("06"):
        expected = [(0x04CB, 1)] if partial else [(0x04CB, 1), (0x04CB, 2)]
        assert [(frame.message_id, frame.param2) for frame in frames] == expected
    elif path.name.startswith("05"):
        assert [(frame.message_id, frame.param2) for frame in frames] == [(0x04C0, 1)]
    else:
        assert frames == []
