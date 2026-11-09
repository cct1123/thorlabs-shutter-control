# Ethernet shutter notebooks

All six standalone notebooks load the same exact configuration through
[shutter_config.py](shutter_config.py):

```python
from shutter_config import SHUTTER

print(SHUTTER.name)  # shutter
print(SHUTTER.channel)  # 0
print(SHUTTER.serial_number)  # 68800777
print(SHUTTER.route.endpoint)  # 192.168.1.19:40305
```

Controller firmware is 1.0.7; port40305 is the KEH3 middle bay. Application CH0
is separate from APT channel1. The source is
[config/shutter.ethernet.toml](../../config/shutter.ethernet.toml);
management port 40303 is unused. Keep power/Ethernet connected and USB IN
disconnected. Release competing owners; do not redock a powered cube.

```powershell
uv sync --locked --group notebooks
uv run --locked --group notebooks jupyter lab docs/examples
```

Choose this environment's Python3 kernel and run one notebook top to bottom.
Each works from the root or examples directory without another notebook's state.
There is no simulator, transport injection, USB fallback, scan or automatic retry.
Restart kernels after source changes.

| Notebook | Actual operation |
| --- | --- |
| [1. Discovery](01_device_discovery.ipynb) | Identify one exact configured controller |
| [2. Connection](02_connection.ipynb) | Connect, verify identity, release |
| [3. Status](03_status_query.ipynb) | Read the canonical structured status |
| [4. Settings](04_settings.ipynb) | Inspect host configuration and actual feedback |
| [5. Modes](05_shutter_modes.ipynb) | Explicit persistent Manual selection; Trigger exit requires source-protection confirmation |
| [6. ON/OFF](06_on_off.ipynb) | Physical OFF preparation, 2 s OFF pause, one 1 s host ON hold, OFF/readback |

Every hardware cell uses the same ShutterHub as Python/CLI/GUI. Its context
releases communication on success or error, preserving a cleanup error alongside
an original exception. If release fails, retain hub and resolve that error before
retrying hub.close(). Release never sends OFF or proves optical closure.

Status uses a fresh 0x0429/0x042A reply and the exact KSC101 output mask0x1.
OFF does not establish operating Inactive, trigger priming, contact continuity or
optical closure. Those states remain separate/unknown. The raw 0x04CD query is
an explicit diagnostic and is not needed for normal status. See
[manual/API findings](../state-zero-investigation.md) and [the Python API](../python-api.md).

Notebooks 1-4 query only. Notebook 5 can change the remembered operating mode;
its False source-protection flag refuses Trigger exit. Notebook 6 actuates the
connected shutter and requires prior Manual selection and the exact approved
source-blocked setup. Run All on notebooks 5/6 is a device operation, separate
from static verification. Review their instructions and
[hardware validation](../HARDWARE_VALIDATION.md) before execution.

Static verification checks schema, syntax and links without executing hardware:

```powershell
uv run --locked --group dev pytest tests/test_tutorial_notebooks.py
```

Saved outputs are dated evidence, not continuing live state. The original user
runs and pre-review notebooks are preserved under ignored inputs/private/notebooks;
[backup hashes](../../records/source-review-notebook-backups.json) identify them.
Actual new runs are recorded separately from static/software checks.


The current [Ethernet configuration](../../config/shutter.ethernet.toml) contains
the user-confirmed SH05R load policy. The actual notebook6 run passed one cycle
and saved its output: [real evidence](../../records/ethernet-control-live.json).
Controller bits0x2000->0x2001->0x2000, final Manual/OFF, resources released.
The user did not observe blade motion; independent optics remain unverified.
Notebook5's protected mode API was exercised separately before that run; its
False flag remains an intentional operator condition for future Trigger exit.
