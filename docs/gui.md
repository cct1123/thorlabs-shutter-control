# Local GUI

```powershell
uv sync --locked --extra gui --extra d2xx
uv run --locked shutter-control --config shutters.local.toml gui
```

Open localhost:8050. Startup is passive and local-only. Select an exact configured
name, then explicitly Connect. Read state obtains controller replies; no background
polling is started. Manual selection, ON, priority OFF and passive Release are
separate controls. An omitted qualification policy blocks every write.
The Manual control states that mode changes are remembered at power-up. A real
transition requires separate `allow_persistent_mode_changes` policy permission;
an already Manual/OFF state is queried without a mode write.

The page displays the full structured result, including requested electrical
state, dated controller feedback, fault/cleanup details and human optical evidence.
Unknown optical state stays unknown. Buttons are explicit commands; no toggle is
computed from a cached state. OFF can interrupt an active query/hold through the
same shared owner. Native driver blocking still requires independent protection.
After a partial/unknown-count write, the owner refuses further frames, including
OFF, because transmit alignment is unknown. The GUI reports the failed cleanup;
use independent source protection and the explicit protected recovery procedure.

Terminal Ctrl+C attempts each connected target's qualified OFF separately, then
releases communication even if cleanup fails. A read-only/unqualified target
cannot be actuated for cleanup and reports that limitation. Browser-tab closure
does not terminate the server or establish closure. Process failure cannot run
cleanup reliably; the persistent uncertainty marker prevents a new process from
silently restoring ON.
