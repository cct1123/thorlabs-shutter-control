"""Explicit candidate-stream diagnostics. Never enables a KEH3 control route.

SRC-003 establishes ports only. Raw APT and the chosen address are hypotheses.
The operator must authorize even an identity query on the actual setup. Offline
capture analysis needs no authorization, socket, SDK or native library.
"""

from dataclasses import asdict, dataclass, field

from .config import ControllerConfig
from .device import Identity
from .errors import IdentityMismatch, ShutterError
from .ethernet import TCPTransport
from .ownership import Claim
from .protocol import Deadline, Decoder, Frame, clock

CAPTURE_LIMIT = 4096
CANDIDATE_ADDRESSES = frozenset((0x50, 0x11, *range(0x21, 0x2B)))


def validate(config, destination):
    if not isinstance(config, ControllerConfig) or config.route.kind != "keh3":
        raise ValueError("Select an explicit configured KEH3 controller route")
    if type(destination) is not int or destination not in CANDIDATE_ADDRESSES:
        raise ValueError("Supply one explicit candidate APT address; no address scan is performed")


@dataclass
class ProbeReport:
    endpoint: str
    expected_controller: str
    expected_hub: str
    candidate_address: int
    verdict: str = "no-identity"
    raw_hex: str = ""
    request_hex: str = ""
    frames: list = field(default_factory=list)
    identity: dict | None = None
    error: str | None = None
    cleanup_error: str | None = None
    first_byte_after_s: float | None = None
    hub_identity_verified: bool = False
    operational_route_available: bool = False
    route: dict = field(default_factory=dict)
    expected_firmware: tuple = ()


def analyze_capture(config, raw, *, destination):
    """Interpret a candidate capture without I/O; a match never qualifies a route."""
    validate(config, destination)
    if not isinstance(raw, bytes) or len(raw) > CAPTURE_LIMIT:
        raise ValueError("Capture must be bytes, at most 4096 bytes")
    report = ProbeReport(
        config.route.endpoint,
        config.serial_number,
        config.route.hub_serial,
        destination,
        raw_hex=raw.hex(),
        route=asdict(config.route),
        expected_firmware=config.firmware,
    )
    decoder = Decoder(destination=1, source=destination)
    try:
        frames = decoder.feed(raw)
        report.frames = [f.encode().hex() for f in frames]
        if any(f.message_id in (0x80, 0x81, 0x0002) for f in frames):
            report.verdict = "controller-fault-or-disconnect"
        elif decoder.buffer:
            report.verdict = "incomplete-frame"
        else:
            identities = [f for f in frames if f.message_id == 6]
            if len(identities) > 1:
                report.verdict = "ambiguous-identities"
            elif identities:
                identity = Identity.decode(identities[0].payload)
                report.identity = asdict(identity)
                try:
                    identity.verify(config)
                    report.verdict = "candidate-controller-match-hub-unverified"
                except IdentityMismatch:
                    report.verdict = "identity-mismatch"
    except ShutterError as exc:
        report.verdict, report.error = "invalid-candidate-stream", str(exc)
        report.frames = [f.encode().hex() for f in getattr(exc, "decoded_frames", ())]
    return report


class KEH3Probe:
    """One owner, one explicit query, no retries/reconnect or operational adoption.

    Keep this object if close fails: it retains the transport and claim, so close
    can be retried explicitly. Never changes modes, outputs, hub config or firmware.
    """

    def __init__(
        self,
        config,
        *,
        destination,
        timeout=5.0,
        authorized=False,
        transport_factory=None,
        lock_directory=None,
    ):
        validate(config, destination)
        Deadline(timeout)
        if type(authorized) is not bool:
            raise ValueError("authorized must be boolean")
        self.config, self.destination, self.timeout = config, destination, timeout
        self.authorized = authorized
        self.factory = transport_factory or TCPTransport
        self.lock_directory = lock_directory
        self.transport = self.claim = None

    def close(self):
        if self.transport is not None:
            self.transport.close()  # Retain both handle and claim on failure.
            self.transport = None
        if self.claim is not None:
            self.claim.release()
            self.claim = None

    def run(self):
        if not self.authorized:
            raise ShutterError("Identity probe needs authorization for a query-only bench window")
        if self.claim is not None:
            raise ShutterError("Release the retained probe handle before another run")
        d = Deadline(self.timeout)
        raw = bytearray()
        report = analyze_capture(self.config, b"", destination=self.destination)
        claim = Claim(self.config, self.lock_directory)
        claim.acquire()
        self.claim = claim
        request = Frame(5, destination=self.destination).encode()
        sent_at, first_byte = None, None
        try:
            host, port = self.config.route.endpoint.split(":")
            self.transport = self.factory(host, int(port), d)
            d.remaining()
            sent_at = clock()
            count = self.transport.write(request, d)
            if count != len(request):
                raise ShutterError(f"Partial diagnostic query: {count}/{len(request)}; no retry")
            d.remaining()
            while True:
                chunk = self.transport.read(min(0.02, d.remaining()))
                if chunk:
                    if first_byte is None:
                        first_byte = clock() - sent_at
                    if len(raw) + len(chunk) > CAPTURE_LIMIT:
                        raw.extend(chunk[: CAPTURE_LIMIT - len(raw)])
                        raise ShutterError("Capture limit reached; stream contract unresolved")
                    raw.extend(chunk)
                    d.remaining()  # Retain late bytes, but never promote them to a match.
                    report = analyze_capture(self.config, bytes(raw), destination=self.destination)
                    if report.verdict not in ("no-identity", "incomplete-frame"):
                        break
                d.remaining()
        except Exception as exc:
            report = analyze_capture(self.config, bytes(raw), destination=self.destination)
            report.verdict, report.error = "probe-unconfirmed", str(exc)
        finally:
            report.request_hex = request.hex() if sent_at is not None else ""
            report.first_byte_after_s = first_byte
            try:
                self.close()
            except Exception as exc:
                report.cleanup_error = str(exc)
                report.verdict = "cleanup-unconfirmed"
        return report
