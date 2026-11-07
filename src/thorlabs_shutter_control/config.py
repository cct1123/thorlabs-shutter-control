"""Strict, passive configuration. Roles and optical mappings are operator evidence."""

import math
import re
import tomllib
from dataclasses import dataclass
from ipaddress import IPv4Address
from pathlib import Path


def positive(value, label, *, zero=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    if value < 0 or (not zero and value == 0):
        raise ValueError(f"{label} must be {'nonnegative' if zero else 'positive'}")
    return float(value)


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value


@dataclass(frozen=True)
class Route:
    kind: str
    port: str | None = None
    hub_serial: str | None = None
    host: str | None = None
    bay: str | None = None
    hub_firmware: str | None = None

    def __post_init__(self):
        if self.kind not in ("vcp", "d2xx", "keh3"):
            raise ValueError("route kind must be vcp, d2xx or keh3")
        if self.kind == "vcp":
            text(self.port, "exact virtual COM port")
            if not re.fullmatch(r"COM[1-9][0-9]*", self.port):
                raise ValueError("VCP route must be a canonical Windows COM number, e.g. COM9")
        elif self.port is not None:
            raise ValueError("port is only valid for vcp")
        if self.kind == "keh3":
            for field in ("hub_serial", "host", "bay", "hub_firmware"):
                text(getattr(self, field), field)
            if str(IPv4Address(self.host)) != self.host:
                raise ValueError("hub host must be a canonical IPv4 address")
            if self.bay not in ("left", "middle", "right", "external"):
                raise ValueError("unknown KEH3 route")
        elif any(v is not None for v in (self.hub_serial, self.host, self.bay, self.hub_firmware)):
            raise ValueError("hub fields apply only to keh3 routes")

    @property
    def endpoint(self):
        if self.kind == "keh3":
            port = dict(left=40304, middle=40305, right=40306, external=40307)[self.bay]
            return f"{self.host}:{port}"
        return self.port


@dataclass(frozen=True)
class Policy:
    """Deployment qualification, not a substitute for a physical safety interlock.

    Manual output is allowed only with a documented continuous-duty load.
    Finite exposure/duty policies can be recorded, but remain unavailable until
    an independent cutoff and the operating limits are qualified.
    """

    evidence: str
    shutter_model: str
    off_optical_state: str
    min_off_s: float
    continuous_on_allowed: bool = False
    max_on_s: float | None = None
    max_duty_fraction: float = 1.0
    allow_persistent_mode_changes: bool = False
    qualified_modes: tuple[str, ...] = ("manual",)
    allow_device_settings: bool = False
    allow_persistent_settings: bool = False
    allow_continuous_cycles: bool = False
    max_cycle_count: int = 1  # Conservative software default, not a manufacturer load rating.

    def __post_init__(self):
        text(self.evidence, "qualification evidence")
        text(self.shutter_model, "attached shutter model")
        if self.off_optical_state != "closed":
            raise ValueError("Only independently established OFF -> closed mappings are supported")
        positive(self.min_off_s, "min_off_s", zero=True)
        if type(self.continuous_on_allowed) is not bool:
            raise ValueError("continuous_on_allowed must be boolean")
        if type(self.allow_persistent_mode_changes) is not bool:
            raise ValueError("allow_persistent_mode_changes must be boolean")
        for name in (
            "allow_device_settings",
            "allow_persistent_settings",
            "allow_continuous_cycles",
        ):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"{name} must be boolean")
        if (
            not isinstance(self.qualified_modes, tuple)
            or "manual" not in self.qualified_modes
            or any(
                not isinstance(mode, str) or mode not in ("manual", "single", "auto", "triggered")
                for mode in self.qualified_modes
            )
            or len(set(self.qualified_modes)) != len(self.qualified_modes)
        ):
            raise ValueError(
                "qualified_modes must be a unique tuple of supported modes including manual"
            )
        if type(self.max_cycle_count) is not int or not 1 <= self.max_cycle_count <= 1000000:
            raise ValueError("max_cycle_count must be an integer in 1..1000000")
        if self.allow_persistent_settings and not self.allow_device_settings:
            raise ValueError("Persistent settings require device-settings permission")
        positive(self.max_duty_fraction, "max_duty_fraction")
        if self.max_duty_fraction > 1:
            raise ValueError("max_duty_fraction must be <= 1")
        if self.max_on_s is not None:
            positive(self.max_on_s, "max_on_s")
            if self.max_on_s > 50:
                raise ValueError("This implementation supports exposures up to 50 seconds")
        if self.continuous_on_allowed and (
            self.max_on_s is not None or self.max_duty_fraction != 1
        ):
            raise ValueError("Continuous ON conflicts with finite exposure/duty limits")
        if not self.continuous_on_allowed and self.max_on_s is None:
            raise ValueError("Finite exposure loads require max_on_s")


@dataclass(frozen=True)
class ControllerConfig:
    name: str
    channel: int
    role: str
    serial_number: str
    firmware: tuple[str, ...]
    route: Route
    policy: Policy | None = None

    def __post_init__(self):
        text(self.name, "logical name")
        text(self.role, "physical role")
        if type(self.channel) is not int or self.channel < 0:
            raise ValueError("channel must be a nonnegative application index")
        if not isinstance(self.serial_number, str) or not re.fullmatch(
            r"68[0-9]{6}", self.serial_number
        ):
            raise ValueError("KSC101 serial must be eight digits beginning 68")
        if (
            not isinstance(self.firmware, tuple)
            or not self.firmware
            or any(
                not isinstance(f, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", f)
                for f in self.firmware
            )
        ):
            raise ValueError("An explicit firmware allowlist is required")
        if not isinstance(self.route, Route) or (
            self.policy is not None and not isinstance(self.policy, Policy)
        ):
            raise ValueError("route/policy must be validated configuration objects")


def validate_configs(configs):
    configs = tuple(configs)
    if not configs or any(not isinstance(c, ControllerConfig) for c in configs):
        raise ValueError("Configure at least one ControllerConfig")
    for values in (
        [c.name for c in configs],
        [c.channel for c in configs],
        [c.serial_number for c in configs],
        [(c.route.kind, c.route.endpoint) for c in configs if c.route.kind != "d2xx"],
    ):
        if len(values) != len(set(values)):
            raise ValueError("Duplicate name, application channel, serial or route assignment")
    hubs = {}
    for c in configs:
        if c.route.kind == "keh3":
            identity = (c.route.hub_serial, c.route.hub_firmware)
            if c.route.host in hubs and hubs[c.route.host] != identity:
                raise ValueError("Conflicting hub identity on the same network address")
            hubs[c.route.host] = identity
    return configs


def load_config(path):
    """Parse TOML only. Unknown keys fail through dataclass constructors."""
    with Path(path).open("rb") as stream:
        document = tomllib.load(stream)
    if set(document) != {"shutters"} or not isinstance(document["shutters"], list):
        raise ValueError("Configuration must contain only [[shutters]] entries")
    result = []
    for entry in document["shutters"]:
        item = dict(entry)
        item["route"] = Route(**item["route"])
        item["firmware"] = tuple(item["firmware"])
        if "policy" in item:
            policy = dict(item["policy"])
            if "qualified_modes" in policy:
                policy["qualified_modes"] = tuple(policy["qualified_modes"])
            item["policy"] = Policy(**policy)
        result.append(ControllerConfig(**item))
    return validate_configs(result)
