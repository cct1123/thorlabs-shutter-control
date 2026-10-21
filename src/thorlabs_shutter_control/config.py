"""Project settings. Edit here, then run: uv run shutter-control.

Serials only preselect panels; startup never discovers or connects hardware.
Keep actual local serials out of shared commits.
"""

KINESIS_DIR = r"C:\Program Files\Thorlabs\Kinesis"
SERIAL_NUMBERS: tuple[str | int, ...] = ()
SLOTS: int | None = None  # Default: at least three, growing to fit serials.
PORT = 8050
