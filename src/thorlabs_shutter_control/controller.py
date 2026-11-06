"""Shared application owner: exact identities, serialized I/O, explicit recovery.

The DiamondGUI public owner methods live here. There is no second hardware
manager, SDK adapter or compatibility implementation. Each configured connection
has one lock and receiver; protective requests signal cancellation before waiting.
"""

from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from os import PathLike
from threading import Event, Lock, RLock

from .config import load_config, positive, text, validate_configs
from .device import KSC101, Identity
from .errors import Cancelled, IdentityMismatch, ShutterError
from .ownership import Claim
from .protocol import Deadline, Session, clock
from .transport import open_transport, require_control_route


def utc_now():
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ShutterFeedback:
    shutter_state: str = "unknown"  # Optical state: never inferred from electrical readback.
    operating_mode: str = "unknown"
    operating_state: str = "unknown"  # Never inferred from the output bit.
    key_enabled: bool | None = None
    interlock_enabled: bool | None = None  # Configuration, not physical continuity.
    channel_enabled: bool | None = None
    status_bits: int | None = None
    electrical_state: str = "unknown"
    electrical_observed_at: str | None = None


@dataclass(frozen=True)
class ShutterStatus:
    name: str
    channel: int
    serial_number: str
    endpoint: str | None
    connection: str = "disconnected"
    has_device: bool = False
    identity_verified: bool = False
    observed_serial_number: str | None = None
    description: str | None = None
    generation: int = 0
    observed_at: str | None = None
    feedback_freshness: str = "unknown"
    feedback: ShutterFeedback = ShutterFeedback()
    requested_state: str | None = None
    transition_confirmed: bool = False  # Independent physical transition is never inferred.
    error: str | None = None
    cleanup: str | None = None
    optical_observed_at: str | None = None
    optical_provenance: str | None = None
    optical_observed_state: str = "unknown"
    identity: Identity | None = None


@dataclass
class _Channel:
    config: object
    lock: object = field(default_factory=RLock)
    cancel: Event = field(default_factory=Event)
    priority_lock: object = field(default_factory=Lock)
    protectors: int = 0
    transport: object = None
    claim: object = None
    driver: object = None
    identity: object = None
    generation: int = 0
    requested: str | None = None
    fault: str | None = None
    cleanup: str | None = None
    next_on: float | None = None
    optical: str = "unknown"
    optical_at: str | None = None
    optical_evidence: str | None = None
    output_attempts: int = 0


class ShutterHub:
    """One canonical owner, named channels or application CH indices.

    Construction/config parsing are hardware-free. transport_factory is a bounded
    byte-transport injection point for offline tests, not a deployed route override.
    Default budgets: connection 5 s, complete query/command 3 s, cleanup 5 s.
    """

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
        configs = load_config(configs) if isinstance(configs, (str, PathLike)) else configs
        self.configs = validate_configs(configs)
        for value in (connect_timeout, query_timeout, cleanup_timeout):
            Deadline(value)
        self.connect_timeout = connect_timeout
        self.query_timeout = query_timeout
        self.cleanup_timeout = cleanup_timeout
        self._factory = transport_factory or open_transport
        self._lock_directory = lock_directory
        self._channels = {c.name: _Channel(c) for c in self.configs}

    def __enter__(self):
        return self

    def __exit__(self, error_type, error, traceback):
        try:
            self.close()
        except BaseException as cleanup:
            if error is None:
                raise
            error.add_note(f"Communication release failed: {cleanup}; retain owner")
        return False

    def _channel(self, target):
        for c in self._channels.values():
            if (isinstance(target, str) and target == c.config.name) or (
                type(target) is int and target == c.config.channel
            ):
                return c
        raise ValueError("Select an exact configured name or application channel index")

    @contextmanager
    def _locked(self, channel, deadline):
        if not channel.lock.acquire(timeout=deadline.remaining()):
            raise ShutterError("Owner busy until deadline; no command dispatched")
        try:
            deadline.remaining()
            yield
        finally:
            channel.lock.release()

    def _snapshot(self, c, feedback=None):
        return ShutterStatus(
            c.config.name,
            c.config.channel,
            c.config.serial_number,
            c.config.route.endpoint,
            identity=c.identity,
            connection="fault" if c.fault else "connected" if c.identity else "disconnected",
            has_device=c.transport is not None,
            identity_verified=c.identity is not None,
            observed_serial_number=c.identity.serial_number if c.identity else None,
            description=f"{c.identity.model} firmware {c.identity.firmware}"
            if c.identity
            else None,
            generation=c.generation,
            observed_at=utc_now() if feedback else None,
            feedback_freshness="response_after_request_no_transaction_id"
            if feedback
            else "unknown",
            feedback=feedback or ShutterFeedback(),
            requested_state=c.requested,
            error=c.fault,
            cleanup=c.cleanup,
            optical_observed_at=c.optical_at,
            optical_provenance=c.optical_evidence,
            optical_observed_state=c.optical,
        )

    def connection_snapshot(self, target):
        """Host metadata only, no polling or cached electrical/optical success."""
        c = self._channel(target)
        return self._snapshot(c)

    def _fault(self, c, exc):
        c.fault = c.fault or str(exc)
        if isinstance(exc, IdentityMismatch):
            c.identity = None
        c.optical = "unknown"
        c.optical_at = c.optical_evidence = None
        if c.claim:
            try:
                c.claim.mark_uncertain(
                    f"{utc_now()} original={c.fault}; latest={exc}; cleanup={c.cleanup}"
                )
            except OSError as journal_error:
                exc.add_note(f"Could not persist uncertainty: {journal_error}; retain lockout")

    def _open(self, c, deadline):
        if c.transport is not None or c.claim is not None:
            raise ShutterError("Retained handle/claim: release or recover explicitly")
        c.claim = Claim(c.config, self._lock_directory)
        try:
            c.claim.acquire()
        except BaseException:
            c.claim = None
            raise
        try:
            deadline.remaining()
            c.transport = self._factory(c.config, deadline)
            c.driver = KSC101(Session(c.transport, c.cancel), c.config)
            c.identity = c.driver.identity(deadline)
            c.generation += 1
            if c.claim.journal.exists():
                c.fault = "Persistent uncertainty: " + c.claim.journal.read_text(encoding="utf8")
        except BaseException as exc:
            c.identity = None
            c.fault = str(exc)
            try:
                self._release(c)
            except BaseException as cleanup:
                exc.add_note(f"Connection release failed: {cleanup}")
            raise

    def connect(self, target):
        """Exact route and identity only; no enable, output, mode or persistent write."""
        c, d = self._channel(target), Deadline(self.connect_timeout)
        with self._locked(c, d):
            self._open(c, d)
            return self._snapshot(c)

    def _ready(self, c, *, allow_fault=False):
        if c.driver is None or c.identity is None:
            raise ShutterError("No identity-verified handle; connect explicitly")
        if c.fault and not allow_fault:
            raise ShutterError(f"Fault lockout: {c.fault}; explicit protected recovery required")

    def _feedback(self, c, d, *, protective=False):
        c.identity = c.driver.identity(d, protective=protective)
        mode = c.driver.operating_mode(d, protective=protective)
        required = c.driver.interlock_required(d, protective=protective)
        bits = c.driver.status_bits(d, protective=protective)
        if bits & 1:
            c.next_on = None  # An observed active output invalidates the previous OFF interval.
        elif c.next_on is None and c.config.policy is not None:
            c.next_on = clock() + c.config.policy.min_off_s
        return ShutterFeedback(
            shutter_state="unknown",
            operating_mode=mode,
            interlock_enabled=required,
            status_bits=bits,
            electrical_state="on" if bits & 1 else "off",
            electrical_observed_at=utc_now(),
        )

    def get_status(self, target):
        c, d = self._channel(target), Deadline(self.query_timeout)
        with self._locked(c, d):
            if c.driver is None:
                return self._snapshot(c)
            self._ready(c, allow_fault=True)
            try:
                return self._snapshot(c, self._feedback(c, d))
            except BaseException as exc:
                self._fault(c, exc)
                raise

    def identify_device(self, target):
        c, d = self._channel(target), Deadline(self.query_timeout)
        with self._locked(c, d):
            self._ready(c)
            try:
                c.identity = c.driver.identity(d)
                return c.identity
            except BaseException as exc:
                self._fault(c, exc)
                raise

    def get_solenoid_state_reply(self, target):
        """Explicit raw diagnostic, separate from normalized electrical feedback."""
        c, d = self._channel(target), Deadline(self.query_timeout)
        with self._locked(c, d):
            self._ready(c)
            try:
                c.identity = c.driver.identity(d)
                return c.driver.solenoid_state_reply(d)
            except BaseException as exc:
                self._fault(c, exc)
                raise

    @staticmethod
    def _policy(c):
        require_control_route(c.config)
        if c.config.policy is None:
            raise ShutterError("Writes disabled: attached shutter limits/mapping are unqualified")
        return c.config.policy

    def _preflight(self, c, d):
        self._ready(c)
        self._policy(c)
        feedback = self._feedback(c, d)
        if feedback.operating_mode != "manual":
            raise ShutterError("Manual mode required; no hidden mode change or trigger priming")
        if not feedback.interlock_enabled:
            raise ShutterError("Manufacturer interlock requirement disabled; refuse output")
        return feedback

    def set_operating_mode(self, target, mode, *, source_inhibited=False):
        """Select Manual explicitly; SRC-002 p20 says changed modes persist at power-up."""
        if mode != "manual":
            raise ValueError("Cycle/TTL modes unavailable until their limits and contracts qualify")
        if type(source_inhibited) is not bool:
            raise ValueError("source_inhibited must be boolean")
        c, d = self._channel(target), Deadline(self.query_timeout)
        policy = self._policy(c)
        with self._locked(c, d):
            self._ready(c)
            try:
                before = self._feedback(c, d)
            except BaseException as exc:
                self._fault(c, exc)
                raise
            if before.operating_mode == "triggered" and not source_inhibited:
                raise ShutterError(
                    "Trigger->Manual requires independently inhibited source and isolated "
                    "trigger control; pass source_inhibited=True after establishing them"
                )
            if before.electrical_state != "off" or not before.interlock_enabled:
                raise ShutterError("Mode change requires electrical OFF and interlock requirement")
            if before.operating_mode == mode:
                return self._snapshot(c, before)  # Do not rewrite an already selected mode.
            if not policy.allow_persistent_mode_changes:
                raise ShutterError(
                    "Mode changes are persistent across power cycles (SRC-002 p20); "
                    "explicit allow_persistent_mode_changes policy permission is required"
                )
            with self._output_operation(c):
                c.claim.mark_uncertain("Explicit mode transition pending")
                c.output_attempts += 1  # Mode changes can also affect output.
                c.driver.set_output(False, d)  # OFF/deactivate before changing operating mode.
                c.driver.wait_output(False, d)
                c.driver.set_operating_mode("manual", d)
                after = self._feedback(c, d)
                if after.operating_mode != "manual" or after.electrical_state != "off":
                    raise ShutterError("Manual mode transition unconfirmed or changed output")
                c.next_on = clock() + policy.min_off_s
                c.claim.clear_uncertain()
                return self._snapshot(c, after)

    def set_manual_mode(self, target, *, source_inhibited=False):
        return self.set_operating_mode(target, "manual", source_inhibited=source_inhibited)

    def enable_device(self, target):
        self._channel(target)
        raise ShutterError("Channel enable aliases solenoid output (SRC-001); use explicit ON")

    @contextmanager
    def _output_operation(self, c):
        """One ambiguity/cleanup guard for mode, ON and pulse writes."""
        attempts = c.output_attempts
        try:
            yield
        except BaseException as exc:
            if c.output_attempts != attempts:
                self._fault(c, exc)
                self._cleanup_after_error(c, exc)
            elif isinstance(exc, IdentityMismatch) or (c.driver and c.driver.session.poisoned):
                self._fault(c, exc)
            raise

    def _on(self, c, d):
        policy = self._policy(c)
        if not policy.continuous_on_allowed:
            raise ShutterError("Finite exposure/duty loads need a qualified independent cutoff")
        feedback = self._preflight(c, d)
        if feedback.electrical_state != "off":
            raise ShutterError("Output already active; timing/ownership is unknown")
        remaining = c.next_on - clock()  # Fresh OFF preflight establishes this interval.
        if remaining > 0:
            raise ShutterError(
                f"Minimum OFF/duty recovery interval has not elapsed; wait {remaining:.2f} s. "
                "ON was not dispatched."
            )
        c.claim.mark_uncertain("ON may have applied; safe state not yet confirmed")
        c.requested = "on"
        c.cleanup = None
        c.optical = "unknown"
        c.optical_at = c.optical_evidence = None
        c.output_attempts += 1
        c.driver.set_output(True, d)
        bits = c.driver.wait_output(True, d)
        return self._snapshot(
            c,
            replace(
                feedback,
                shutter_state="unknown",
                electrical_state="on",
                status_bits=bits,
                electrical_observed_at=utc_now(),
            ),
        )

    def set_solenoid(self, target, on):
        if type(on) is not bool:
            raise ValueError("on must be boolean")
        if not on:
            return self.safe_state(target)
        c, d = self._channel(target), Deadline(self.query_timeout)
        self._policy(c)
        with self._locked(c, d), self._output_operation(c):
            return self._on(c, d)

    def open_shutter(self, target):
        """Optical request allowed only with the qualified OFF/closed load mapping."""
        return self.set_solenoid(target, True)

    def close_shutter(self, target):
        return self.safe_state(target)

    def _safe(self, c, d):
        policy = self._policy(c)
        self._ready(c, allow_fault=True)
        c.requested = "off"
        c.cleanup = None
        c.optical = "unknown"
        c.optical_at = c.optical_evidence = None
        c.claim.mark_uncertain(f"Protective OFF pending; original={c.fault}; optical state unknown")
        # A receive-poisoned stream cannot confirm readback. OFF remains reachable
        # only with known transmit alignment on the retained verified handle.
        if not c.driver.session.poisoned:
            c.identity = c.driver.identity(d, protective=True)
        dispatched = clock()
        c.output_attempts += 1
        c.driver.set_output(False, d, protective=True)
        if c.driver.session.poisoned:
            raise ShutterError("OFF dispatched on ambiguous session; no confirmed safe state")
        c.driver.wait_output(False, d, protective=True)
        c.next_on = clock() + policy.min_off_s  # Rest begins with observed OFF, not dispatch.
        feedback = self._feedback(c, d, protective=True)
        if feedback.electrical_state != "off" or feedback.operating_mode != "manual":
            raise ShutterError("OFF unconfirmed or external/cycle authority remains active")
        c.cleanup = f"Electrical OFF readback; dispatch monotonic={dispatched:.6f}; optical unknown"
        # Do not clear an existing fault. Only protected recover() can clear lockout.
        if c.fault is None:
            c.claim.clear_uncertain()
        return self._snapshot(c, feedback)

    def safe_state(self, target):
        c, d = self._channel(target), Deadline(self.cleanup_timeout)
        self._policy(c)
        with c.priority_lock:
            c.protectors += 1
            c.cancel.set()  # Signal before taking the active owner's lock.
        try:
            with self._locked(c, d):
                try:
                    return self._safe(c, d)
                except BaseException as exc:
                    c.cleanup = f"Safe state unconfirmed: {exc}"
                    self._fault(c, exc)
                    raise
        finally:
            with c.priority_lock:
                c.protectors -= 1
                if c.protectors == 0:
                    c.cancel.clear()

    def cancel(self, target):
        """Priority cancellation includes the qualified OFF action, not just a flag."""
        return self.safe_state(target)

    def _cleanup_after_error(self, c, original):
        try:
            self.safe_state(c.config.name)
        except BaseException as cleanup:
            original.add_note(f"Separate cleanup outcome: {cleanup}; optical state unknown")

    def validate_pulse(self, target, duration):
        """Validate a requested host hold without connecting or accessing hardware."""
        duration = positive(duration, "duration")
        policy = self._policy(self._channel(target))
        if duration > 50 or (policy.max_on_s is not None and duration > policy.max_on_s):
            raise ValueError("Exposure exceeds configured limit (or implementation maximum 50 s)")
        if not policy.continuous_on_allowed:
            raise ShutterError(
                "Finite exposure protection needs an independent cutoff; unqualified"
            )
        return duration

    def pulse(self, target, duration):
        duration = self.validate_pulse(target, duration)
        c = self._channel(target)
        d = Deadline(min(60, duration + self.query_timeout))
        with self._locked(c, d):
            with self._output_operation(c):
                self._on(c, d)
                if c.cancel.wait(min(duration, d.remaining())):
                    raise Cancelled("Pulse cancelled by protective request")
                d.remaining()
            return self.safe_state(target)

    def recover(self, target, *, source_inhibited=False, optical_closed=False, evidence=None):
        """Explicit protected recovery; re-open exact route, verify OFF/manual/interlock.

        A read alone never clears ambiguity. External source protection and an
        independent closed observation are required and recorded as human evidence.
        No output command or previous ON/cycle is replayed.
        """
        if source_inhibited is not True or optical_closed is not True:
            raise ShutterError(
                "Recovery requires independently protected source and optical closure"
            )
        text(evidence, "recovery observation evidence")
        c, d = self._channel(target), Deadline(self.connect_timeout)
        with self._locked(c, d):
            if c.cancel.is_set():
                raise Cancelled("Recovery deferred to a pending protective request")
            self._release(c)
            self._open(c, d)
            try:
                feedback = self._feedback(c, d)
                if (
                    feedback.electrical_state != "off"
                    or feedback.operating_mode != "manual"
                    or not feedback.interlock_enabled
                ):
                    raise ShutterError("Recovery requires OFF/manual and preserved interlock")
                c.claim.clear_uncertain()
                c.fault = None
                c.optical, c.optical_at, c.optical_evidence = "closed", utc_now(), evidence
                c.next_on = clock() + (c.config.policy.min_off_s if c.config.policy else 0)
                return self._snapshot(c, feedback)
            except BaseException as exc:
                self._fault(c, exc)
                raise

    @staticmethod
    def _release(c):
        if c.transport is not None:
            c.transport.close()  # If this fails, retain handle and claims.
        c.transport = c.driver = c.identity = None
        c.next_on = None
        c.optical = "unknown"
        c.optical_at = c.optical_evidence = None
        if c.claim:
            c.claim.release()
            c.claim = None

    def disconnect(self, target=None):
        """Communication release only. Independent output cleanup remains explicit."""
        channels = [self._channel(target)] if target is not None else self._channels.values()
        failures = []
        for c in channels:
            try:
                with self._locked(c, Deadline(self.cleanup_timeout)):
                    self._release(c)
            except BaseException as exc:
                failures.append((c.config.name, exc))
        self._raise_all("Release incomplete", failures)

    @staticmethod
    def _raise_all(label, failures):
        if failures:
            error = ShutterError(label + ": " + "; ".join(f"{n}: {e}" for n, e in failures))
            for name, exc in failures:
                error.add_note(f"{name}: {exc!r}; notes={getattr(exc, '__notes__', [])}")
            raise error from failures[0][1]

    def close(self):
        """HardwareManager passive release hook."""
        self.disconnect()

    def shutdown_outputs(self):
        failures = []
        for c in self._channels.values():
            if c.output_attempts == 0 and c.requested is None:
                if c.fault:
                    failures.append((c.config.name, ShutterError(f"Read-only fault: {c.fault}")))
                continue  # A policy permits commands; it does not create a cleanup obligation.
            if c.transport is not None:
                try:
                    self.safe_state(c.config.name)
                except BaseException as exc:
                    failures.append((c.config.name, exc))
            elif c.requested == "on" or c.fault:
                failures.append(
                    (
                        c.config.name,
                        ShutterError(
                            "Controller unavailable with unresolved output/fault; "
                            "no automatic reconnect"
                        ),
                    )
                )
        self._raise_all("Output cleanup unconfirmed; optical state unknown", failures)
