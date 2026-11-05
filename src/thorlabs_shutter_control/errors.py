"""Errors retain uncertainty; an exception never implies optical closure."""


class ShutterError(RuntimeError):
    """Rejected or failed shutter operation."""


class ProtocolError(ShutterError):
    """Invalid or ambiguous stream; further queries require a new session."""


class DeadlineExceeded(ShutterError):
    """The end-to-end monotonic deadline expired."""


class Cancelled(ShutterError):
    """An active request yielded to cancellation or a protective request."""


class UnsupportedRoute(ShutterError):
    """A documented and qualified route contract is missing."""


class IdentityMismatch(ShutterError):
    """The retained route no longer identifies the configured controller."""


class ControllerFault(ShutterError):
    """Complete manufacturer fault frame, without guessing private return codes."""

    def __init__(self, frame):
        self.frame = frame
        self.raw = frame.encode().hex()
        super().__init__(f"Controller fault 0x{frame.message_id:04x}: {self.raw}")
