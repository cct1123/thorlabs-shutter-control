# Historical evidence and privacy

The original 136-file evidence archive and connected-bench screenshot contain
real device identities and local configuration. They have been removed from the
shareable working tree. Unmodified originals and checksums are retained locally
under ignored `inputs/private/documentation-originals/`; they are not distributed
with a fresh clone. This change preserves local evidence without publishing it.

Current [hardware results](../hardware-validation.json), [TTL results](../ttl-summary.json)
and [evidence index](../RECORDS.md) are sanitized derivatives. `CONTROLLER_A`,
`HUB_A` and `MISMATCHED_ID` are aliases, not usable device serials. They preserve
identity comparisons and test outcomes without identifying the bench.

Historical stages, decisions and firmware/command investigations remain available
in the private original archive for local review. Old files are reference data,
not current operating authority. Public summaries preserve PASS/FAIL/UNTESTED
scope, including unresolved active-low TTL and Ethernet observations.

Privacy removal here covers current shareable files. Earlier Git commits may
still contain prior identities or assets; Git history has not been rewritten.
