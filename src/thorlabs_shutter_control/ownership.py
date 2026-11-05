"""Machine-local advisory claims and persistent uncertainty across process exit.

All library/CLI/GUI owners use these locks. They cannot exclude unrelated vendor
software or another machine: deployment must prevent those competing owners.
Files remain in place so unlink/recreate cannot defeat a held OS lock.
"""

import hashlib
import os
from pathlib import Path

from .errors import ShutterError


class Claim:
    def __init__(self, config, directory=None):
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
        except (OSError, BlockingIOError) as exc:
            self.release()
            raise ShutterError("Controller serial/route already owned or lock unavailable") from exc

    def mark_uncertain(self, reason):
        with self.journal.open("w", encoding="utf8") as stream:
            stream.write(reason)
            stream.flush()
            os.fsync(stream.fileno())

    def clear_uncertain(self):
        self.journal.unlink(missing_ok=True)

    def release(self):
        for stream in self.handles:
            stream.close()
        self.handles.clear()
