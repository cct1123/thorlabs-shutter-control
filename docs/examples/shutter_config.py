"""Exact real Ethernet configuration shared by all independent notebooks."""

from pathlib import Path

from thorlabs_shutter_control import load_config

HUB_MANAGEMENT_PORT = 40303
(SHUTTER,) = load_config(Path(__file__).resolve().parents[2] / "config/shutter.ethernet.toml")
