# Engineering evidence and decisions

The complete original E001-E078/D history and raw artifacts are preserved in
[the verified archive](archive/README.md). This index supersedes repeated progress
logs; original bytes/checksums remain available. Requirements live in STATE.md.

| Evidence | Durable conclusion |
| --- | --- |
| E050 / TEST-060 | Official KSC101 update1.0.6->1.0.7 completed; USB identity68800777 repaired without a software alias |
| E068 / TEST-077; E070 / TEST-079 | Four-state matrix did not establish jack continuity; clear SDK bit remains unknown, key report is separate |
| E072 / TEST-081 | User removed dedicated Stage7/count criterion; removal is not a physical PASS |
| E075 / TEST-084 | Five SDK Open2s/Close2s cycles passed readback; user confirmed physical sequence |
| D018 / E076; E077 / TEST-085/086 | Explicit object/serial session interlock evidence; production Stage5 shutdown and Stage6 GUI/Ctrl+C cleanup readback passed |
| E078 / TEST-087 | Redesigned GUI actual browser/USB Open with2.015s visible hold, Close, passive trigger read, keyboard section, reconnect and global cleanup;440 then-current software tests passed |

Physical calibration/timing, three-pair, electrical TTL and physical fault tests
remain unexecuted. Historical Ethernet hub-only discovery predates cube firmware
update; no post-update cube qualification is claimed. See
[consolidated observations](hardware-validation.json).

## D019 / E079 / TEST-088 - Holistic cleanup and consistency review

User explicitly authorizes pruning logs/development junk, holistic fixes, commit
and push. Preserved136 original evidence/checkpoint/source/acquisition files in
hardware-2026-10-20.zip, verified every member SHA256 and ZIP integrity, and wrote
an external whole-archive checksum. Retained current bench summary, formal
incomplete bench record and actual GUI screenshot separately. Old prompt history,
unused generated screenshots and temporary SDK extraction/installer/build/cache
copies are cleanup candidates; installed Kinesis/.venv/live GUI remain untouched.

Review found stale untested/hold claims, pre-/post-firmware Ethernet conflation,
obsolete UI examples, mixed text encoding and incompatible tutorial readiness.
Current docs were reconciled. Tutorials03-05 now accept explicit confirmation for
selected serials and reject another target before SDK access. A supported cleanup
bug was fixed: identity mismatch plus failed release could previously cause output
cleanup on an unverified retained target. ExitStack now registers passive release
before Connect and Close only after successful identity/feedback verification;
callbacks continue through errors with normal Python exception chaining. New
regressions cover these cases.449 source software tests PASS; no driver/GUI/CLI
change or actual hardware operation in this cleanup. Previous bench evidence is
not promoted to three-pair/electrical/calibration acceptance.

Final validation:449 source tests and449 tests against the freshly built,
extracted wheel PASS. Wheel contains9 entries including CSS, with no records,
tests, docs or vendor binaries.100 verified files/directories pruned; .venv and
installed vendor runtime preserved.17 active Markdown files/67 local targets PASS;
Ruff/format/diff checks PASS. All136 archive member hashes and whole ZIP checksum
verified; secret-pattern scan has no matches. Active reviewed text normalized LF.
Build/test outputs were removed after qualification; no verified scratch/cache
folder remains. records/cleanup-validation.json records commands, hashes, removal
allowlist and limits. origin/main fetched equal to pre-review HEAD0833e84.
Implementation commit/push verification follows; no hardware operation performed.
