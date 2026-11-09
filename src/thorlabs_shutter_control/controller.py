"""KSC101 configuration, commands and shared application owner.

Order: configuration, data models, APT driver, ownership and the shared owner.
ShutterHub groups each operation with its helpers: connection, status, modes,
settings, output, then protection and recovery.

The DiamondGUI public owner methods live here. There is no second hardware
manager, SDK adapter or compatibility implementation. Each configured connection
has one lock and receiver; protective requests signal cancellation before waiting.
"""

import hashlib
import math
import os
import re
import struct
import time
import tomllib
from contextlib import contextmanager
from dataclasses import dataclass, field, fields, replace
from datetime import datetime, timezone
from os import PathLike
from pathlib import Path
from threading import Event, Lock, RLock

from .protocol import Cancelled, Deadline, Frame, ProtocolError, Session, ShutterError, clock
from .transport import Route, UnsupportedRoute, open_transport

MODES = {1: "manual", 2: "single", 3: "auto", 4: "triggered"}
# Exact KSC101 GetStatusBits reference (SRC-008); these are reported flags,
# not independently measured key position, interlock continuity or readiness.
STATUS_MASKS = {"interlock_status_bit": 0x00001000, "channel_enabled_bit": 0x80000000}


# Validation and timestamps


def positive(value, label, *, zero=False):
    """Return a finite positive float, allowing zero when zero=True.

    Reject booleans, nonnumeric values and invalid ranges with ValueError.
    The label identifies the offending input in the error message.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    if value < 0 or (not zero and value == 0):
        raise ValueError(f"{label} must be {'nonnegative' if zero else 'positive'}")
    return float(value)


def text(value, label):
    """Validate nonblank string input; raise ValueError using label on failure."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")


def utc_now():
    """Return an ISO 8601 UTC timestamp for observation and diagnostic records."""
    return datetime.now(timezone.utc).isoformat()


# Configuration and load qualification


@dataclass(frozen=True)
class Policy:
    """Immutable load qualification, timing limits and write permissions.

    Evidence and shutter_model describe the operator-qualified load; this record
    cannot establish physical safety. min_off_s/max_on_s are seconds, duty is a
    fraction in (0, 1], and qualified_modes permits output activation. Settings
    writes and EEPROM persistence require separate permissions; mode selection does not.
    Only a qualified OFF-to-closed mapping is supported. Finite-load limits may
    be recorded, but output activation still requires continuous-duty permission.
    """

    evidence: str
    shutter_model: str
    off_optical_state: str
    min_off_s: float
    continuous_on_allowed: bool = False
    max_on_s: float | None = None
    max_duty_fraction: float = 1.0
    # Accepted legacy setting; mode selection ignores it.
    allow_persistent_mode_changes: bool = False
    qualified_modes: tuple[str, ...] = ("manual",)  # Output activation, not protected selection.
    allow_device_settings: bool = False
    allow_persistent_settings: bool = False
    allow_continuous_cycles: bool = False
    max_cycle_count: int = 1  # Conservative software default, not a manufacturer load rating.

    def __post_init__(self):
        """Reject contradictory permissions, unsupported modes and invalid load limits."""
        text(self.evidence, "qualification evidence")
        text(self.shutter_model, "attached shutter model")
        if self.off_optical_state != "closed":
            raise ValueError("Only independently established OFF -> closed mappings are supported")
        positive(self.min_off_s, "min_off_s", zero=True)
        for name in (
            "continuous_on_allowed",
            "allow_persistent_mode_changes",
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
                not isinstance(mode, str) or mode not in MODES.values()
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
    """Immutable expected identity and connection route for one named shutter.

    channel is an application index, independent of the fixed APT channel 1.
    firmware is an explicit version allowlist. An absent policy disables shutter
    output/settings writes; role records the physical purpose, not a safe state.
    """

    name: str
    channel: int
    role: str
    serial_number: str
    firmware: tuple[str, ...]
    route: Route
    policy: Policy | None = None

    def __post_init__(self):
        """Validate names, application index, expected serial/firmware and route/policy types."""
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


def _validate_configs(configs):
    """Return configs as a tuple after rejecting duplicate assignments and hub conflicts."""
    configs = tuple(configs)
    if not configs or any(not isinstance(config, ControllerConfig) for config in configs):
        raise ValueError("Configure at least one ControllerConfig")
    for values in (
        [config.name for config in configs],
        [config.channel for config in configs],
        [config.serial_number for config in configs],
        [
            (config.route.kind, config.route.endpoint)
            for config in configs
            if config.route.kind != "d2xx"
        ],
    ):
        if len(values) != len(set(values)):
            raise ValueError("Duplicate name, application channel, serial or route assignment")
    hubs = {}
    for config in configs:
        if config.route.kind == "keh3":
            known = hubs.setdefault(config.route.host, {})
            for name in ("hub_serial", "hub_firmware"):
                value = getattr(config.route, name)
                if value is not None and known.setdefault(name, value) != value:
                    raise ValueError("Conflicting hub identity on the same network address")
    return configs


def load_config(path):
    """Load a nonempty tuple of validated ControllerConfig objects from a TOML path.

    The document must contain only [[shutters]] entries with explicit identity
    and route data. Unknown keys and invalid values fail validation. This reads
    a local file; it neither connects to a device nor changes its settings.
    """
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
    return _validate_configs(result)


# Device data and application status


class IdentityMismatch(ShutterError):
    """The selected route does not identify the expected controller/model/firmware."""


@dataclass(frozen=True)
class Identity:
    """Immutable controller identity decoded from an APT hardware-info reply.

    Observed serial/model/firmware remain separate from the configured values.
    hardware_version and channels preserve the reported hardware metadata.
    """

    serial_number: str
    model: str
    firmware: str
    hardware_version: int
    channels: int

    @classmethod
    def decode(cls, payload):
        """Decode an 84-byte hardware-info payload; reject invalid length or model text."""
        if not isinstance(payload, bytes) or len(payload) != 84:
            raise ProtocolError("Hardware identity requires an 84-byte payload")
        try:
            return cls(
                str(struct.unpack_from("<I", payload)[0]),
                payload[4:12].decode("ascii").rstrip("\0 "),
                f"{payload[16]}.{payload[15]}.{payload[14]}",
                struct.unpack_from("<H", payload, 78)[0],
                struct.unpack_from("<H", payload, 82)[0],
            )
        except UnicodeDecodeError as exc:
            raise ProtocolError("Malformed hardware identity") from exc

    def verify(self, config):
        """Return this identity if it matches config; otherwise raise IdentityMismatch."""
        if (
            self.serial_number != config.serial_number
            or self.model != "KSC101"
            or self.channels != 1
            or self.firmware not in config.firmware
        ):
            raise IdentityMismatch(f"Identity/model/firmware mismatch on exact route: {self}")
        return self


@dataclass(frozen=True)
class CycleParameters:
    """Validated device cycle settings, using integer milliseconds and cycle count.

    on_ms/off_ms each range from 100 to 10000; cycles ranges from 0 to 1000000.
    Zero cycles requests continuous cycling and needs separate owner permission.
    These device bounds do not replace the attached load limits in Policy.
    """

    on_ms: int
    off_ms: int
    cycles: int

    def __post_init__(self):
        """Reject noninteger or out-of-range device timings and cycle counts."""
        for name in ("on_ms", "off_ms"):
            value = getattr(self, name)
            if type(value) is not int or not 100 <= value <= 10000:
                raise ValueError(f"{name} must be an integer in 100..10000 ms")
        if type(self.cycles) is not int or not 0 <= self.cycles <= 1000000:
            raise ValueError("cycles must be an integer in 0..1000000; 0 means continuous")

    def encode(self):
        """Encode the channel-1 APT cycle payload as little-endian <HIII bytes."""
        return struct.pack("<HIII", 1, self.on_ms, self.off_ms, self.cycles)

    @classmethod
    def decode(cls, payload):
        """Decode a cycle payload and validate its channel, timings and count."""
        channel, on_ms, off_ms, cycles = struct.unpack("<HIII", payload)
        if channel != 1:
            raise ValueError("Wrong cycle-parameter response channel")
        return cls(on_ms, off_ms, cycles)


@dataclass
class ShutterStatus:
    """Independent mutable snapshot returned by the application owner.

    has_device reports a retained handle; identity reports verified controller
    data. Electrical readings are unknown until explicitly queried and carry a
    UTC timestamp. optical_closed_at/evidence record a separate human observation,
    never a conclusion from an output bit. Editing a snapshot cannot change the
    owner; locks, transports and other private resources are excluded.
    interlock_status_bit/channel_enabled_bit decode SRC-008 status masks and
    share electrical_observed_at; neither establishes physical key/ready state.
    """

    name: str
    has_device: bool = False
    identity: Identity | None = None
    generation: int = 0
    operating_mode: str = "unknown"
    interlock_required: bool | None = None  # Configuration, not contact continuity.
    status_bits: int | None = None
    interlock_status_bit: bool | None = None
    channel_enabled_bit: bool | None = None
    electrical_state: str = "unknown"
    electrical_observed_at: str | None = None
    requested_state: str | None = None
    error: str | None = None
    cleanup: str | None = None
    optical_closed_at: str | None = None  # Human observation, cleared by output/ambiguity.
    optical_evidence: str | None = None
    cycle_parameters: CycleParameters | None = None
    settings_observed_at: str | None = None
    settings_persistence: str | None = None


# KSC101 APT driver


class KSC101:
    # Identity and identification

    """Low-level APT commands and replies for one configured controller.

    The caller supplies a Session and end-to-end Deadline for each operation.
    This driver does not own locks, enforce load policy or guarantee optical
    state; applications should use ShutterHub. Protective calls are reserved
    for the owner's cleanup path. No output command is automatically retried.
    """

    def __init__(self, session, config):
        """Bind the existing session and expected configuration without device I/O."""
        self.session = session
        self.config = config

    def identity(self, deadline, *, protective=False):
        """Query hardware identity within deadline and verify it against the expected config."""
        reply = self.session.query(Frame(0x0005), 0x0006, deadline, protective=protective)
        return Identity.decode(reply.payload).verify(self.config)

    def blink_identify(self, deadline):
        """Send the identify-LED request; APT provides no completion acknowledgement."""
        self.session.send(Frame(0x0223, 1), deadline)

    def hub_bay_reply(self, deadline):
        """Read the raw legacy hub-bay byte; never infer a KEH3 route from it."""
        reply = self.session.query(Frame(0x0065), 0x0066, deadline)
        if reply.param2 != 0:
            self.session.poisoned = True
            raise ProtocolError("Nonzero reserved byte in hub-bay reply")
        return reply.param1

    def start_updates(self, deadline):
        """Request automatic status messages; there is no acknowledgement."""
        self.session.send(Frame(0x0011), deadline)

    def stop_updates(self, deadline):
        """Request that automatic status messages stop; there is no acknowledgement."""
        self.session.send(Frame(0x0012), deadline)

    def disconnect_hardware(self, deadline):
        """Explicitly request bus disconnect; this is not ordinary transport release."""
        self.session.send(Frame(0x0002), deadline)

    def led_modes(self, deadline):
        """Read the documented LED indication-mode word, without interpreting motion."""
        reply = self.session.query(Frame(0x04B4, 1), 0x04B5, deadline)
        channel, modes = struct.unpack("<HH", reply.payload)
        if channel != 1:
            self.session.poisoned = True
            raise ProtocolError("Wrong LED-mode response channel")
        return modes

    @staticmethod
    def validate_led_modes(modes):
        """Accept only documented LED bits: Identify=1, limit switch=2, moving=8."""
        if type(modes) is not int or modes < 0 or modes & ~0x0B:
            raise ValueError("LED modes must contain only documented bits 0x01, 0x02 and 0x08")

    def set_led_modes(self, modes, deadline):
        """Write the LED indication-mode word to RAM; this does not set display brightness."""
        self.validate_led_modes(modes)
        self.session.send(Frame(0x04B3, payload=struct.pack("<HH", 1, modes)), deadline)

    # Operating mode and interlock

    def operating_mode(self, deadline, *, protective=False):
        """Read the supported mode name: manual, single, auto or triggered."""
        return MODES[self._scalar(0x04C1, 0x04C2, MODES, deadline, protective=protective)]

    def interlock_required(self, deadline, *, protective=False):
        """Read the interlock-requirement setting; this does not measure contact continuity."""
        return self._scalar(0x04C7, 0x04C8, (1, 2), deadline, protective=protective) == 1

    def require_interlock(self, deadline):
        """Enable the hardware-interlock requirement; disabling it is not exposed."""
        self.session.send(Frame(0x04C6, 1, 1), deadline)

    def channel_enabled(self, deadline):
        """Read channel-enable state using 0x0211/0212, without output writes."""
        return self._scalar(0x0211, 0x0212, (1, 2), deadline) == 1

    def _scalar(self, request, reply, allowed, deadline, *, protective=False):
        """Query a channel-1 scalar and poison the session if its value is unsupported."""
        frame = self.session.query(Frame(request, 1), reply, deadline, protective=protective)
        if frame.param2 not in allowed:
            self.session.poisoned = True
            error = ProtocolError(f"Unsupported scalar value {frame.param2} in 0x{reply:04x}")
            error.add_note(f"Raw controller reply: {frame.encode().hex()}")
            raise error
        return frame.param2

    def set_operating_mode(self, mode, deadline):
        """Send a validated persistent mode-selection request; readback is separate."""
        if mode not in MODES.values():
            raise ValueError("mode must be manual, single, auto or triggered")
        code = next(code for code, name in MODES.items() if name == mode)
        self.session.send(Frame(0x04C0, 1, code), deadline)

    # Electrical output and raw diagnostics

    def status_bits(self, deadline, *, protective=False):
        """Query the raw 32-bit status value; malformed replies poison the session."""
        frame = self.session.query(Frame(0x0429, 1), 0x042A, deadline, protective=protective)
        try:
            return self.decode_status_bits(frame)
        except ProtocolError:
            self.session.poisoned = True
            raise

    @staticmethod
    def decode_status_bits(frame):
        """Validate a channel-1 0x042A frame and decode its 32-bit status field."""
        if frame.message_id != 0x042A or frame.payload is None or len(frame.payload) != 6:
            raise ProtocolError("Status bits require a 0x042A frame with a 6-byte payload")
        channel, bits = struct.unpack("<HI", frame.payload)
        if channel != 1:
            raise ProtocolError("Wrong status-bits response channel")
        return bits

    def solenoid_state_reply(self, deadline):
        """Read raw 0x04CD param2 without interpreting its conflicting legacy enums."""
        return self.session.query(Frame(0x04CC, 1), 0x04CD, deadline).param2

    def set_output(self, on, deadline, *, protective=False):
        """Send one ON/OFF request, or native Start/Stop in the selected mode.

        on must be boolean. This sends the command only; the caller must validate
        qualification before dispatch and explicitly confirm the resulting state.
        """
        if type(on) is not bool:
            raise ValueError("on must be boolean")
        self.session.send(Frame(0x04CB, 1, 1 if on else 2), deadline, protective=protective)

    def set_channel_enabled(self, enabled, deadline):
        """Encode the documented output alias 0x0210; the owner uses canonical 0x04CB.

        This can actuate the shutter. It is never initialization and has no ACK.
        Low-level callers must provide the same qualification as set_output.
        """
        if type(enabled) is not bool:
            raise ValueError("enabled must be boolean")
        self.session.send(Frame(0x0210, 1, 1 if enabled else 2), deadline)

    def wait_output(self, on, deadline, *, protective=False):
        """Poll until output bit 0 matches on and return the observed raw status bits.

        Use the existing deadline, without resending output commands. Matching
        electrical readback establishes neither blade position nor native inactivity.
        """
        while True:
            bits = self.status_bits(deadline, protective=protective)
            if bool(bits & 1) == on:
                return bits
            time.sleep(min(0.01, deadline.remaining()))

    # Cycle settings

    def cycle_parameters(self, deadline):
        """Read validated CycleParameters; malformed data poisons the session."""
        reply = self.session.query(Frame(0x04C4, 1), 0x04C5, deadline)
        try:
            return CycleParameters.decode(reply.payload)
        except (struct.error, TypeError, ValueError) as exc:
            self.session.poisoned = True
            raise ProtocolError(f"Invalid cycle parameters: {exc}") from exc

    def set_cycle_parameters(self, parameters, deadline):
        """Send validated CycleParameters to device RAM; readback is separate."""
        if not isinstance(parameters, CycleParameters):
            raise ValueError("parameters must be validated CycleParameters")
        self.session.send(Frame(0x04C3, payload=parameters.encode()), deadline)

    def persist_cycle_parameters(self, deadline):
        """Request EEPROM storage of cycle settings only (APT p99).

        No persistence acknowledgement exists; restart verification is still required.
        """
        self.session.send(Frame(0x04B9, payload=struct.pack("<HH", 1, 0x04C3)), deadline)


# Internal ownership and channel state


class _Claim:
    """Per-controller OS locks and a crash-persistent uncertainty journal.

    Serial and endpoint claims coordinate package clients in the same account,
    not vendor software or other hosts/accounts. Keep lock files on disk so
    unlink/recreate cannot defeat a held OS lock.
    """

    def __init__(self, config, directory=None):
        """Prepare lock/journal paths and create the local state directory; acquire no locks yet."""
        state_root = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "state"))
        self.directory = Path(directory or state_root / "KSC101Control" / "ownership-v1")
        self.directory.mkdir(parents=True, exist_ok=True)
        keys = ["serial:" + config.serial_number]
        if config.route.endpoint:
            keys.append("endpoint:" + config.route.endpoint.casefold())
        self.paths = [self.directory / hashlib.sha256(k.encode()).hexdigest() for k in sorted(keys)]
        self.handles = []
        self.journal = self.directory / ("uncertain-" + config.serial_number)

    def acquire(self):
        """Acquire serial/endpoint OS locks, releasing partial claims if acquisition fails."""
        try:
            for path in self.paths:
                stream = path.open("a+b")
                self.handles.append(stream)
                stream.seek(0)
                if os.name == "nt":
                    import msvcrt

                    if path.stat().st_size == 0:
                        stream.write(b"0")
                        stream.flush()
                    stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.release()
            raise ShutterError("Controller serial/route already owned or lock unavailable") from exc

    def mark_uncertain(self, reason):
        """Write and fsync an uncertainty reason so lockout survives process failure."""
        with self.journal.open("w", encoding="utf8") as stream:
            stream.write(reason)
            stream.flush()
            os.fsync(stream.fileno())

    def clear_uncertain(self):
        """Remove the journal when the caller confirms its required operation/cleanup state."""
        self.journal.unlink(missing_ok=True)

    def release(self):
        """Close handles to release OS locks; retain lock files and any uncertainty journal."""
        for stream in self.handles:
            stream.close()
        self.handles.clear()


@dataclass
class _Channel(ShutterStatus):
    """Mutable owner metadata plus private resources for one controller.

    Inherits public status fields, but retains no fresh electrical sample between
    operations. Locks/events are created separately per channel. Public snapshots
    copy only ShutterStatus fields, excluding these handles and synchronization objects.
    """

    config: ControllerConfig = field(kw_only=True)
    lock: object = field(default_factory=RLock)
    cancel: Event = field(default_factory=Event)
    priority_lock: object = field(default_factory=Lock)
    protectors: int = 0
    transport: object = None
    claim: _Claim | None = None
    driver: KSC101 | None = None
    next_on: float | None = None
    output_attempts: int = 0


# Shared application controller


class ShutterHub:
    """Own configured shutters through one serialized connection per controller.

    A target is an exact configured name or integer application channel index.
    Construction is passive: connect explicitly before queries or commands.
    Public operations return independent ShutterStatus snapshots unless noted.
    Default budgets are 5 s for connection, 3 s for queries/commands and a
    separate 5 s for protective cleanup, including time spent waiting for locks.

    Use safe_state/shutdown_outputs explicitly when output cleanup is required.
    close/disconnect/context exit only release communication and cannot prove
    optical closure. Reads never clear a latched fault; recover requires external
    source protection and independently reported optical closure.
    """

    # Construction and shared guards

    def __init__(
        self,
        configs,
        *,
        connect_timeout=5.0,
        query_timeout=3.0,
        cleanup_timeout=5.0,
        transport_factory=None,
        lock_directory=None,
    ):
        """Validate configuration and create per-channel state without opening devices.

        Args:
            configs: TOML path or nonempty iterable of ControllerConfig objects.
            connect_timeout: Total connection/identity budget in seconds.
            query_timeout: Total ordinary query/command budget in seconds.
            cleanup_timeout: Independent protective cleanup budget in seconds.
            transport_factory: Optional bounded byte-transport factory for software tests.
            lock_directory: Optional local directory for ownership locks and journals.

        Invalid configuration or timeout values fail before device I/O.
        """
        self.configs = (
            load_config(configs)
            if isinstance(configs, (str, PathLike))
            else _validate_configs(configs)
        )
        for value in (connect_timeout, query_timeout, cleanup_timeout):
            Deadline(value)
        self.connect_timeout = connect_timeout
        self.query_timeout = query_timeout
        self.cleanup_timeout = cleanup_timeout
        self._factory = transport_factory or open_transport
        self._lock_directory = lock_directory
        self._channels = {
            config.name: _Channel(config.name, config=config) for config in self.configs
        }

    def __enter__(self):
        """Return this owner without connecting or actuating any shutter."""
        return self

    def __exit__(self, error_type, error, traceback):
        """Release communication and propagate the original error, noting release failure."""
        try:
            self.close()
        except BaseException as cleanup:
            if error is None:
                raise
            error.add_note(f"Communication release failed: {cleanup}; retain owner")
        return False

    def _channel(self, target):
        """Resolve an exact configured name or application index; reject aliases and booleans."""
        for channel in self._channels.values():
            if (isinstance(target, str) and target == channel.config.name) or (
                type(target) is int and target == channel.config.channel
            ):
                return channel
        raise ValueError("Select an exact configured name or application channel index")

    @contextmanager
    def _locked(self, channel, deadline):
        """Hold the channel lock within deadline and always release it on exit."""
        if not channel.lock.acquire(timeout=deadline.remaining()):
            raise ShutterError("Owner busy until deadline; no command dispatched")
        try:
            deadline.remaining()
            yield
        finally:
            channel.lock.release()

    def _ready(self, channel, *, allow_fault=False):
        """Require a verified handle and, unless allowed for cleanup/reads, no latched fault."""
        if channel.driver is None or channel.identity is None:
            raise ShutterError("No identity-verified handle; connect explicitly")
        if channel.error is not None and not allow_fault:
            raise ShutterError(
                f"Fault lockout: {channel.error}; use Stop / OFF to reset after verified readback"
            )

    @staticmethod
    def _policy(channel):
        """Return the configured write policy after route/qualification checks, without I/O."""
        route = channel.config.route
        if route.kind == "keh3" and route.bay == "external":
            raise UnsupportedRoute(
                "KEH3 external USB control unavailable; select a documented docked cube bay"
            )
        if route.kind == "vcp":
            raise UnsupportedRoute("VCP bridge reset/binding unqualified: read-only commissioning")
        if channel.config.policy is None:
            raise ShutterError("Writes disabled: attached shutter limits/mapping are unqualified")
        return channel.config.policy

    # Connection lifecycle

    def connect(self, target):
        """Open the exact target route, verify identity and return host-only status.

        Acquire serial/endpoint claims and use the connection deadline. No enable,
        mode or output command is sent. A previous uncertainty journal remains a
        fault lockout until verified Stop/OFF or recovery; connect never replays output.
        """
        channel, deadline = self._channel(target), Deadline(self.connect_timeout)
        with self._locked(channel, deadline):
            self._open(channel, deadline)
            return self._snapshot(channel)

    def _open(self, channel, deadline):
        """Claim/open the exact route and verify identity; retain connection errors."""
        if channel.transport is not None or channel.claim is not None:
            raise ShutterError("Retained handle/claim: release or recover explicitly")
        channel.claim = _Claim(channel.config, self._lock_directory)
        try:
            channel.claim.acquire()
        except BaseException:
            channel.claim = None
            raise
        try:
            deadline.remaining()
            channel.transport = self._factory(channel.config, deadline)
            channel.driver = KSC101(Session(channel.transport, channel.cancel), channel.config)
            channel.identity = channel.driver.identity(deadline)
            channel.generation += 1
            if channel.claim.journal.exists():
                channel.error = "Persistent uncertainty: " + channel.claim.journal.read_text(
                    encoding="utf8"
                )
        except BaseException as exc:
            channel.identity = None
            channel.error = str(exc) or type(exc).__name__
            try:
                self._release(channel)
            except BaseException as cleanup:
                exc.add_note(f"Connection release failed: {cleanup}")
            raise

    def disconnect(self, target=None, *, require_stopped=False):
        """Release communication for target, or every channel when target is None.

        Send no output commands. A failed close retains its handle/claims, and all
        selected channels are attempted before failures are reported together.
        require_stopped=True atomically refuses release of an ON/Start request;
        the WebUI uses this guard against concurrent output callbacks.
        Return None when all requested releases succeed.
        """
        if type(require_stopped) is not bool:
            raise ValueError("require_stopped must be boolean")
        channels = [self._channel(target)] if target is not None else self._channels.values()
        failures = []
        for channel in channels:
            try:
                with self._locked(channel, Deadline(self.cleanup_timeout)):
                    if require_stopped and channel.requested_state in ("on", "start"):
                        raise ShutterError(
                            "Stop / OFF before releasing an active output or native sequence"
                        )
                    self._release(channel)
            except BaseException as exc:
                failures.append((channel.config.name, exc))
        self._raise_all("Release incomplete", failures)

    def close(self):
        """Release all communication handles and return None; never send output commands."""
        self.disconnect()

    @staticmethod
    def _release(channel):
        """Close transport before claims; clear observations and preserve ambiguity."""
        if channel.transport is not None:
            channel.transport.close()  # If this fails, retain handle and claims.
        channel.transport = channel.driver = channel.identity = None
        channel.next_on = None
        channel.cycle_parameters = channel.settings_observed_at = channel.settings_persistence = (
            None
        )
        channel.optical_closed_at = channel.optical_evidence = None
        if (
            channel.claim
            and channel.error is None
            and channel.requested_state not in ("on", "start")
            and not channel.claim.journal.exists()
        ):
            # Confirmed-safe output history does not authorize a future read-only session.
            channel.output_attempts = 0
        if channel.claim:
            channel.claim.release()
            channel.claim = None

    # Status and diagnostics

    def connection_snapshot(self, target):
        """Return host metadata for target without querying or opening a device.

        Electrical state stays unknown even if an earlier query succeeded; this
        snapshot must not be treated as a fresh output or optical observation.
        """
        channel = self._channel(target)
        return self._snapshot(channel)

    def _snapshot(self, channel, **readings):
        """Copy public channel metadata plus current readings into an independent status object."""
        values = {f.name: getattr(channel, f.name) for f in fields(ShutterStatus)}
        values.update(readings)
        bits = values["status_bits"]
        values.update(
            {
                name: None if bits is None else bool(bits & mask)
                for name, mask in STATUS_MASKS.items()
            }
        )
        return ShutterStatus(**(values | {"has_device": channel.transport is not None}))

    def get_status(self, target):
        """Return fresh controller readings, or host-only status if disconnected.

        A connected call queries identity, mode, interlock configuration and status
        bits within the query budget. Existing faults remain visible; identity or
        communication failures are latched and raised, never silently recovered.
        """
        channel, deadline = self._channel(target), Deadline(self.query_timeout)
        with self._locked(channel, deadline):
            if channel.driver is None:
                return self._snapshot(channel)
            self._ready(channel, allow_fault=True)
            try:
                return self._read_status(channel, deadline)
            except BaseException as exc:
                self._fault(channel, exc)
                raise

    def _read_status(self, channel, deadline, *, protective=False):
        """Read identity/mode/interlock/bits, update OFF rest and return fresh status."""
        channel.identity = channel.driver.identity(deadline, protective=protective)
        mode = channel.driver.operating_mode(deadline, protective=protective)
        required = channel.driver.interlock_required(deadline, protective=protective)
        bits = channel.driver.status_bits(deadline, protective=protective)
        if bits & 1:
            # An observed active output invalidates the previous OFF interval.
            channel.next_on = None
        elif channel.next_on is None and channel.config.policy is not None:
            channel.next_on = clock() + channel.config.policy.min_off_s
        return self._snapshot(
            channel,
            operating_mode=mode,
            interlock_required=required,
            status_bits=bits,
            electrical_state="on" if bits & 1 else "off",
            electrical_observed_at=utc_now(),
        )

    @contextmanager
    def _read_operation(self, target, *, verify_identity=True):
        """Lock and latch read faults; omit identity only before a full status preflight."""
        channel, deadline = self._channel(target), Deadline(self.query_timeout)
        with self._locked(channel, deadline):
            self._ready(channel)
            try:
                if verify_identity:
                    channel.identity = channel.driver.identity(deadline)
                yield channel, deadline
            except BaseException as exc:
                self._fault(channel, exc)
                raise

    def identify_device(self, target):
        """Read and return verified Identity for a connected, nonfaulted target."""
        with self._read_operation(target) as (channel, _):
            return channel.identity

    def get_solenoid_state_reply(self, target):
        """Return the raw diagnostic byte without inferring electrical or optical state."""
        with self._read_operation(target) as (channel, deadline):
            return channel.driver.solenoid_state_reply(deadline)

    def get_channel_enabled(self, target):
        """Query the documented channel-enable boolean; do not infer blade position."""
        with self._read_operation(target) as (channel, deadline):
            return channel.driver.channel_enabled(deadline)

    def get_hub_bay_reply(self, target):
        """Return a raw legacy bay byte; refuse the unqualified KEH3 query before I/O."""
        if self._channel(target).config.route.kind == "keh3":
            raise UnsupportedRoute(
                "Legacy hub-bay query is unqualified on KEH3; use the configured route"
            )
        with self._read_operation(target) as (channel, deadline):
            return channel.driver.hub_bay_reply(deadline)

    def get_led_modes(self, target):
        """Read the LED indication bitmask; it is not display brightness or optical feedback."""
        with self._read_operation(target) as (channel, deadline):
            return channel.driver.led_modes(deadline)

    def start_updates(self, target):
        """Request automatic status messages without starting a thread or output.

        Stop explicitly before release. No ACK confirms that streaming started.
        Use get_events for raw frames; ordinary get_status still requests fresh data.
        """
        with self._read_operation(target) as (channel, deadline):
            channel.driver.start_updates(deadline)

    def stop_updates(self, target):
        """Request automatic updates stop; no ACK or hardware-state change is inferred."""
        with self._read_operation(target) as (channel, deadline):
            channel.driver.stop_updates(deadline)

    def get_events(self, target):
        """Collect arrived frames via an identity query and consume buffered raw events.

        Keep payloads unmodified; no KSC101 motor-position/status-update layout is
        assumed. Controller faults still raise rather than becoming ordinary events.
        """
        with self._read_operation(target) as (channel, _):
            events = tuple(channel.driver.session.events)
            channel.driver.session.events.clear()
            return events

    def disconnect_hardware(self, target, *, source_inhibited=False):
        """Explicitly disconnect the bus, then release communication.

        Require source protection, fresh Manual/OFF and no active request. This
        sends 0x0002 once with no ACK; ordinary disconnect()/close() remain passive.
        """
        if source_inhibited is not True:
            raise ShutterError("Hardware disconnect requires source_inhibited=True")
        with self._read_operation(target, verify_identity=False) as (channel, deadline):
            feedback = self._manual_feedback(self._read_status(channel, deadline))
            if feedback.electrical_state != "off" or channel.requested_state in ("on", "start"):
                raise ShutterError("Stop/OFF before hardware disconnect")
            channel.driver.disconnect_hardware(deadline)
            self._release(channel)
            return self._snapshot(channel)

    def blink_identify(self, target):
        """Request target identification LEDs and return fresh status.

        No shutter output command is sent. Status readback does not acknowledge that
        the requested LED flash completed.
        """
        with self._read_operation(target) as (channel, deadline):
            channel.driver.blink_identify(deadline)  # APT defines no identify acknowledgement.
            return self._read_status(channel, deadline)

    # Operating mode and Manual preflight

    def set_operating_mode(self, target, mode, *, source_inhibited=False):
        """Select manual, single, auto or triggered and verify fresh mode/OFF readback.

        Mode selection requires no separate persistent-mode permission.
        The controller must be OFF with its interlock requirement enabled.
        source_inhibited is accepted for compatibility but is not required for mode selection.
        An actual transition sends Stop/OFF first; an already selected permitted
        mode returns status without rewriting it. Selection does not qualify Start.
        """
        if mode not in MODES.values():
            raise ValueError("mode must be manual, single, auto or triggered")
        if type(source_inhibited) is not bool:
            raise ValueError("source_inhibited must be boolean")
        channel, deadline = self._channel(target), Deadline(self.query_timeout)
        policy = self._policy(channel)
        with self._locked(channel, deadline):
            self._ready(channel)
            try:
                before = self._read_status(channel, deadline)
            except BaseException as exc:
                self._fault(channel, exc)
                raise
            if before.electrical_state != "off" or not before.interlock_required:
                raise ShutterError("Mode change requires electrical OFF and interlock requirement")
            if before.operating_mode == mode:
                return before  # Do not rewrite an already selected mode.
            with self._output_operation(channel):
                channel.claim.mark_uncertain("Explicit mode transition pending")
                channel.output_attempts += 1  # Mode changes can also affect output.
                channel.requested_state = "off"  # This transition explicitly sends Stop/OFF first.
                channel.driver.set_output(
                    False, deadline
                )  # OFF/deactivate before changing operating mode.
                channel.driver.wait_output(False, deadline)
                channel.driver.set_operating_mode(mode, deadline)
                after = self._read_status(channel, deadline)
                if (
                    after.operating_mode != mode
                    or after.electrical_state != "off"
                    or not after.interlock_required
                ):
                    raise ShutterError("Mode transition unconfirmed or changed output/interlock")
                channel.next_on = clock() + policy.min_off_s
                channel.claim.clear_uncertain()
                return after

    @staticmethod
    def _manual_feedback(feedback):
        """Require Manual mode and enabled interlock requirement; return the supplied status."""
        if feedback.operating_mode != "manual":
            raise ShutterError("Manual mode required; no hidden mode change or trigger priming")
        if not feedback.interlock_required:
            raise ShutterError("Manufacturer interlock requirement disabled; refuse output")
        return feedback

    def _preflight(self, channel, deadline):
        """Validate fresh Manual/interlock status; the caller checks electrical OFF."""
        self._ready(channel)
        return self._manual_feedback(self._read_status(channel, deadline))

    # Cycle settings

    def get_cycle_parameters(self, target):
        """Read device cycle settings, timestamp them and return fresh target status."""
        with self._read_operation(target) as (channel, deadline):
            channel.cycle_parameters = channel.driver.cycle_parameters(deadline)
            channel.settings_observed_at = utc_now()
            return self._read_status(channel, deadline)

    def set_cycle_parameters(self, target, parameters, *, source_inhibited=False, persist=False):
        """Write validated CycleParameters and verify settings and Manual/OFF status.

        Require device-settings permission, Manual mode,
        electrical OFF and the interlock requirement. Load timing/count limits apply.
        persist=True additionally requires EEPROM permission and sends a storage
        request; the returned persistence note still requires restart verification.
        A possible write followed by failure latches uncertainty and attempts OFF.
        """
        if not isinstance(parameters, CycleParameters):
            raise ValueError("parameters must be validated CycleParameters")
        if type(persist) is not bool:
            raise ValueError("persist must be boolean")
        deadline = Deadline(self.query_timeout)
        channel, policy = self._settings_access(target, source_inhibited)
        if persist and not policy.allow_persistent_settings:
            raise ShutterError(
                "EEPROM storage requires separate allow_persistent_settings permission"
            )
        self._cycle_limits(policy, parameters)
        with self._locked(channel, deadline), self._output_operation(channel):
            before = self._preflight(channel, deadline)  # Settings edits require Manual/OFF.
            if before.electrical_state != "off":
                raise ShutterError("Device settings require electrical OFF")
            channel.claim.mark_uncertain("Cycle settings write pending; output must remain OFF")
            channel.output_attempts += 1
            channel.driver.set_cycle_parameters(parameters, deadline)
            observed = channel.driver.cycle_parameters(deadline)
            if observed != parameters:
                raise ShutterError("Cycle settings readback differs from the requested values")
            channel.cycle_parameters, channel.settings_observed_at = observed, utc_now()
            channel.settings_persistence = "Not requested"
            if persist:
                channel.driver.persist_cycle_parameters(deadline)
                channel.settings_persistence = "EEPROM request sent; restart verification required"
            return self._confirm_settings(channel, deadline)

    def require_interlock(self, target, *, source_inhibited=False):
        """Enable the hardware-interlock requirement and verify Manual/OFF readback.

        Requires device-settings permission. A currently
        disabled requirement can be repaired; disabling the interlock is not exposed.
        """
        deadline = Deadline(self.query_timeout)
        channel, _ = self._settings_access(target, source_inhibited)
        with self._locked(channel, deadline), self._output_operation(channel):
            self._ready(channel)
            before = self._read_status(channel, deadline)
            if before.operating_mode != "manual" or before.electrical_state != "off":
                raise ShutterError("Interlock configuration requires Manual/OFF")
            if before.interlock_required:
                return before
            channel.claim.mark_uncertain("Interlock requirement write pending")
            channel.output_attempts += 1
            channel.driver.require_interlock(deadline)
            return self._confirm_settings(channel, deadline)

    def set_led_modes(self, target, modes, *, source_inhibited=False):
        """Write documented LED indication bits to RAM and return the exact readback.

        Require settings permission and fresh Manual/OFF/interlock.
        LED-only writes do not create an output-cleanup obligation. No EEPROM
        request is sent and no motor status meaning is inferred from these flags.
        """
        KSC101.validate_led_modes(modes)
        self._settings_access(target, source_inhibited)
        with self._read_operation(target, verify_identity=False) as (channel, deadline):
            before = self._manual_feedback(self._read_status(channel, deadline))
            if before.electrical_state != "off":
                raise ShutterError("LED settings require electrical OFF")
            channel.driver.set_led_modes(modes, deadline)
            observed = channel.driver.led_modes(deadline)
            if observed != modes:
                raise ShutterError("LED settings readback differs from the requested value")
            return observed

    def _settings_access(self, target, source_inhibited):
        """Validate shared settings permission before any I/O; accept legacy protection flag."""
        if type(source_inhibited) is not bool:
            raise ValueError("source_inhibited must be boolean")
        channel = self._channel(target)
        policy = self._policy(channel)
        if not policy.allow_device_settings:
            raise ShutterError("Device settings require allow_device_settings qualification")
        return channel, policy

    def _confirm_settings(self, channel, deadline):
        """Verify a settings write retained Manual/OFF and the interlock requirement."""
        feedback = self._read_status(channel, deadline)
        if (
            feedback.electrical_state != "off"
            or feedback.operating_mode != "manual"
            or not feedback.interlock_required
        ):
            raise ShutterError("Settings changed output/mode/interlock unexpectedly")
        channel.claim.clear_uncertain()
        return feedback

    @staticmethod
    def _cycle_limits(policy, parameters, *, repeated=True):
        """Enforce load timing, and when repeated=True, duty fraction and cycle-count limits."""
        if parameters.off_ms / 1000 < policy.min_off_s:
            raise ValueError("Device OFF duration is shorter than the qualified minimum OFF rest")
        if policy.max_on_s is not None and parameters.on_ms / 1000 > policy.max_on_s:
            raise ValueError("Device ON duration exceeds the load policy")
        if repeated:
            duty = parameters.on_ms / (parameters.on_ms + parameters.off_ms)
            if duty > policy.max_duty_fraction:
                raise ValueError("Device cycle duty fraction exceeds the load policy")
            if parameters.cycles == 0 and not policy.allow_continuous_cycles:
                raise ShutterError("Continuous cycles require separate load-policy permission")
            if parameters.cycles > policy.max_cycle_count:
                raise ValueError("Cycle count exceeds the qualified max_cycle_count")

    # Output activation and timed pulses

    def set_solenoid(self, target, on):
        """Request Manual ON when on=True, or protective OFF when on=False.

        Require a boolean. ON needs a qualified continuous-duty load, verified
        Manual/interlock/OFF preflight and elapsed OFF rest. Return electrical
        readback; neither branch proves physical blade position.
        """
        if type(on) is not bool:
            raise ValueError("on must be boolean")
        if not on:
            return self.safe_state(target)
        channel, deadline = self._channel(target), Deadline(self.query_timeout)
        policy = self._policy(channel)
        with self._locked(channel, deadline), self._output_operation(channel):
            return self._on(channel, deadline, policy)

    def start(self, target, *, source_inhibited=False):
        """Request Manual ON or one native Start/prime in the selected qualified mode.

        Native operation additionally requires qualified cycle parameters and
        interlock/OFF/rest checks. Triggered priming requires
        continuous-cycle permission and cycles=0. Return fresh status without
        inferring cycle completion; explicit Stop/OFF remains required.
        """
        if type(source_inhibited) is not bool:
            raise ValueError("source_inhibited must be boolean")
        channel, deadline = self._channel(target), Deadline(self.query_timeout)
        policy = self._policy(channel)
        with self._locked(channel, deadline), self._output_operation(channel):
            self._ready(channel)
            feedback = self._read_status(channel, deadline)
            mode = feedback.operating_mode
            if mode == "manual":
                return self._on(channel, deadline, policy, feedback=feedback)
            if mode not in policy.qualified_modes:
                raise ShutterError(f"Mode {mode} is absent from the load policy's qualified_modes")
            if not policy.continuous_on_allowed or not feedback.interlock_required:
                raise ShutterError(
                    "Native operation requires qualified load and interlock requirement"
                )
            if feedback.electrical_state != "off" or channel.requested_state == "start":
                raise ShutterError("Stop/OFF before starting another native sequence")
            parameters = channel.driver.cycle_parameters(deadline)
            self._cycle_limits(policy, parameters, repeated=mode == "auto")
            if mode == "triggered" and (
                parameters.cycles != 0 or not policy.allow_continuous_cycles
            ):
                raise ShutterError(
                    "KSC101 level-triggered priming requires cycles=0 "
                    "and explicit continuous permission"
                )
            if clock() < channel.next_on:
                raise ShutterError("Minimum OFF interval has not elapsed; Start was not dispatched")
            channel.claim.mark_uncertain("Native Start/prime requested; Stop/OFF remains required")
            channel.requested_state, channel.cleanup = "start", None
            channel.optical_closed_at = channel.optical_evidence = None
            channel.output_attempts += 1
            channel.next_on = None
            channel.driver.set_output(True, deadline)
            # A short Single cycle can finish before this reply. Do not require
            # an ON bit or pretend an OFF sample confirms native inactivity.
            return self._read_status(channel, deadline)

    def _on(self, channel, deadline, policy, *, feedback=None):
        """With lock/policy, check Manual/OFF/rest, send ON once and confirm its bit."""
        if not policy.continuous_on_allowed:
            raise ShutterError("Finite exposure/duty loads need a qualified independent cutoff")
        feedback = (
            self._preflight(channel, deadline)
            if feedback is None
            else self._manual_feedback(feedback)
        )
        if feedback.electrical_state != "off":
            raise ShutterError("Output already active; timing/ownership is unknown")
        remaining = channel.next_on - clock()  # Fresh OFF preflight establishes this interval.
        if remaining > 0:
            raise ShutterError(
                f"Minimum OFF/duty recovery interval has not elapsed; wait {remaining:.2f} s. "
                "ON was not dispatched."
            )
        channel.claim.mark_uncertain("ON may have applied; safe state not yet confirmed")
        channel.requested_state = "on"
        channel.cleanup = None
        channel.optical_closed_at = channel.optical_evidence = None
        channel.output_attempts += 1
        channel.next_on = None  # An ON attempt invalidates every previously observed OFF interval.
        channel.driver.set_output(True, deadline)
        bits = channel.driver.wait_output(True, deadline)
        return self._snapshot(
            channel,
            operating_mode=feedback.operating_mode,
            interlock_required=feedback.interlock_required,
            electrical_state="on",
            status_bits=bits,
            electrical_observed_at=utc_now(),
        )

    def validate_pulse(self, target, duration):
        """Return a valid host-hold duration in seconds without device I/O.

        Require a positive finite duration within the 50 s implementation
        limit and a qualified continuous-duty load. This checks the request only;
        it neither connects nor authorizes physical actuation by itself.
        """
        duration = positive(duration, "duration")
        policy = self._policy(self._channel(target))
        if duration > 50:
            raise ValueError("Exposure exceeds implementation maximum 50 s")
        if not policy.continuous_on_allowed:
            raise ShutterError(
                "Finite exposure protection needs an independent cutoff; unqualified"
            )
        return duration

    def pulse(self, target, duration):
        """Request Manual ON, wait duration seconds on the host, then request protective OFF.

        Return the final electrical OFF status. Cancellation/failure retains its
        error and any separate cleanup outcome. The host hold is bounded by the
        operation deadline and does not represent calibrated optical exposure.
        """
        duration = self.validate_pulse(target, duration)
        channel = self._channel(target)
        deadline = Deadline(min(60, duration + self.query_timeout))
        with self._locked(channel, deadline):
            with self._output_operation(channel):
                # validate_pulse already checked this policy.
                self._on(channel, deadline, channel.config.policy)
                if channel.cancel.wait(min(duration, deadline.remaining())):
                    raise Cancelled("Pulse cancelled by protective request")
                deadline.remaining()
            return self.safe_state(target)

    # Protection, recovery and shutdown

    def safe_state(self, target):
        """Prioritize protective OFF and return its freshly confirmed electrical status.

        Signal cancellation before waiting for the owner lock, then use the separate
        cleanup budget. Require a qualified route/load. A successful explicit Stop/OFF
        clears a prior fault after fresh OFF/interlock verification. Failure latches
        uncertainty and is raised; communication alone does not establish optical closure.
        """
        return self._protect(target, reset_fault=True)

    def _protect(self, target, *, reset_fault):
        """Send priority OFF; only an explicit operator Stop resets a verified fault."""
        channel, deadline = self._channel(target), Deadline(self.cleanup_timeout)
        policy = self._policy(channel)
        with channel.priority_lock:
            channel.protectors += 1
            channel.cancel.set()  # Signal before taking the active owner's lock.
        try:
            with self._locked(channel, deadline):
                try:
                    feedback = self._safe(channel, deadline, policy)
                    if reset_fault and channel.error is not None:
                        if not feedback.interlock_required:
                            raise ShutterError("Fault reset requires preserved interlock")
                        channel.claim.clear_uncertain()
                        channel.error = None
                    return replace(feedback, error=channel.error)
                except BaseException as exc:
                    channel.cleanup = f"Safe state unconfirmed: {str(exc) or type(exc).__name__}"
                    self._fault(channel, exc)
                    raise
        finally:
            with channel.priority_lock:
                channel.protectors -= 1
                if channel.protectors == 0:
                    channel.cancel.clear()

    def _safe(self, channel, deadline, policy):
        """With lock/policy, send protective OFF and confirm it without clearing faults."""
        self._ready(channel, allow_fault=True)
        channel.requested_state = "off"
        channel.cleanup = None
        channel.optical_closed_at = channel.optical_evidence = None
        channel.claim.mark_uncertain(
            f"Protective OFF pending; original={channel.error}; optical state unknown"
        )
        # A receive-poisoned stream cannot confirm readback. OFF remains reachable
        # only with known transmit alignment on the retained verified handle.
        if not channel.driver.session.poisoned:
            channel.identity = channel.driver.identity(deadline, protective=True)
        dispatched = clock()
        channel.output_attempts += 1
        channel.driver.set_output(False, deadline, protective=True)
        if channel.driver.session.poisoned:
            raise ShutterError("OFF dispatched on ambiguous session; no confirmed safe state")
        channel.driver.wait_output(False, deadline, protective=True)
        channel.next_on = clock() + policy.min_off_s  # Rest begins with observed OFF, not dispatch.
        feedback = self._read_status(channel, deadline, protective=True)
        if feedback.electrical_state != "off":
            raise ShutterError("OFF unconfirmed")
        channel.cleanup = (
            f"Electrical OFF readback; dispatch monotonic={dispatched:.6f}; optical unknown"
        )
        # Automatic cleanup retains faults; explicit safe_state() can reset them.
        if channel.error is None:
            channel.claim.clear_uncertain()
        return replace(feedback, cleanup=channel.cleanup)

    def recover(self, target, *, source_inhibited=False, optical_closed=False, evidence=None):
        """Reopen the exact target and clear lockout after protected passive verification.

        Require source_inhibited=True, optical_closed=True and nonblank evidence
        of an independent human closure observation. Verify Manual/OFF/interlock
        before clearing fault/request history and recording that observation.
        No output command, previous ON or native cycle is replayed; any verification
        failure retains lockout. External protection must already be established.
        """
        if source_inhibited is not True or optical_closed is not True:
            raise ShutterError(
                "Recovery requires independently protected source and optical closure"
            )
        text(evidence, "recovery observation evidence")
        channel, deadline = self._channel(target), Deadline(self.connect_timeout)
        with self._locked(channel, deadline):
            if channel.cancel.is_set():
                raise Cancelled("Recovery deferred to a pending protective request")
            self._release(channel)
            self._open(channel, deadline)
            try:
                feedback = self._read_status(channel, deadline)
                if (
                    feedback.electrical_state != "off"
                    or feedback.operating_mode != "manual"
                    or not feedback.interlock_required
                ):
                    raise ShutterError("Recovery requires OFF/manual and preserved interlock")
                channel.claim.clear_uncertain()
                channel.error = None
                channel.requested_state = None
                channel.output_attempts = 0
                channel.cleanup = "Protected recovery verified Manual/OFF; no output command sent"
                channel.optical_closed_at, channel.optical_evidence = utc_now(), evidence
                channel.next_on = clock() + (
                    channel.config.policy.min_off_s if channel.config.policy else 0
                )
                return replace(
                    feedback,
                    error=None,
                    requested_state=None,
                    cleanup=channel.cleanup,
                    optical_closed_at=channel.optical_closed_at,
                    optical_evidence=evidence,
                )
            except BaseException as exc:
                self._fault(channel, exc)
                raise

    def shutdown_outputs(self):
        """Attempt protective OFF for every channel with output history requiring cleanup.

        Do not actuate read-only sessions or reconnect missing devices. Attempt all
        applicable channels, then raise aggregated unresolved faults/cleanup errors.
        Communication release remains a separate close/disconnect action.
        Return None if all applicable cleanup succeeds.
        """
        failures = []
        for channel in self._channels.values():
            if channel.output_attempts == 0 and channel.requested_state not in ("on", "start"):
                if channel.error:
                    failures.append(
                        (channel.config.name, ShutterError(f"Read-only fault: {channel.error}"))
                    )
                continue  # A policy permits commands; it does not create a cleanup obligation.
            if channel.transport is not None:
                try:
                    feedback = self._protect(channel.config.name, reset_fault=False)
                    if feedback.error is not None:
                        failures.append((channel.config.name, ShutterError(feedback.error)))
                except BaseException as exc:
                    failures.append((channel.config.name, exc))
            elif channel.requested_state in ("on", "start") or channel.error:
                failures.append(
                    (
                        channel.config.name,
                        ShutterError(
                            "Controller unavailable with unresolved output/fault; "
                            "no automatic reconnect"
                        ),
                    )
                )
        self._raise_all("Output cleanup unconfirmed; optical state unknown", failures)

    @contextmanager
    def _output_operation(self, channel):
        """Latch ambiguous output failures and attempt OFF while retaining the original error."""
        attempts = channel.output_attempts
        try:
            yield
        except BaseException as exc:
            if channel.output_attempts != attempts:
                self._fault(channel, exc)
                try:
                    self._protect(channel.config.name, reset_fault=False)
                except BaseException as cleanup:
                    exc.add_note(f"Separate cleanup outcome: {cleanup}; optical state unknown")
            elif isinstance(exc, IdentityMismatch) or (
                channel.driver and channel.driver.session.poisoned
            ):
                self._fault(channel, exc)
            raise

    def _fault(self, channel, exc):
        """Latch the first error, clear optical evidence and journal uncertainty if possible."""
        description = str(exc) or type(exc).__name__
        channel.error = channel.error or description
        if isinstance(exc, IdentityMismatch):
            channel.identity = None
        channel.optical_closed_at = channel.optical_evidence = None
        if channel.claim:
            try:
                channel.claim.mark_uncertain(
                    f"{utc_now()} original={channel.error}; latest={description}; "
                    f"cleanup={channel.cleanup}"
                )
            except OSError as journal_error:
                exc.add_note(f"Could not persist uncertainty: {journal_error}; retain lockout")

    @staticmethod
    def _raise_all(label, failures):
        """Raise one ShutterError with per-channel causes/notes, or return for no failures."""
        if failures:
            error = ShutterError(label + ": " + "; ".join(f"{n}: {e}" for n, e in failures))
            for name, exc in failures:
                error.add_note(f"{name}: {exc!r}; notes={getattr(exc, '__notes__', [])}")
            raise error from failures[0][1]
