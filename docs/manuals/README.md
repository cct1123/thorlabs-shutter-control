# Device manuals and APT command protocol

These unchanged manufacturer PDFs are included in the repository for offline
reference. Verified 6 November 2026 against the SHA-256 values already recorded
in the [source register](../sources.md); original downloads remain in ignored
`inputs/reference/`. They are eligible for version control here.

| Source | Local document | Revision | Pages |
| --- | --- | --- | --- |
| SRC-002 | [KSC101 controller manual](KSC101_Manual_HA0368T_Rev_D.pdf) | HA0368T Rev D, June 2023 | 45 |
| SRC-010 | [KSC101 Kinesis UI reference manual](KSC101_Kinesis_UI_Manual_HA0368T_Rev_F.pdf) | HA0368T Rev F, September 2026 | 41 |
| SRC-003 | [KEH3/KEH6 hub manual](KEH3_KEH6_Manual_DOC-103012_Rev_E.pdf) | DOC-103012 Rev E, 22 January 2026 | 33 |
| SRC-007 | [APT host-controller command protocol](APT_Communications_Protocol_Issue_42.1.pdf) | Issue 42.1, 9 September 2025 | 443 |
| SRC-001 | [Earlier APT protocol in Git history](https://github.com/cct1123/thorlabs-shutter-control/blob/5d2adc1edeb93a3b827974c12ee957a2b6c9255f/docs/manuals/APT_Communications_Protocol_Issue_36.pdf) | Issue 36, 17 April 2023 | 421 |

Issue 36 is available in Git history for older source/page references; it is no
longer in the working tree. Issue 42.1 is the retained local protocol reference.
Neither revision alone establishes compatibility with the actual firmware or
KEH3 control route.

The Rev D KSC101 PDF is the legacy APT user guide. Its cover states that APT software
was discontinued on 1 July 2024 and directs readers to current item-specific
documentation. This copy preserves the exact manual used by the implementation;
it is not a claim that this is the latest operating guide. The user-supplied
ETN017648-D03 URL returned Rev F, now included unchanged as SRC-010. Its GUI is
a reference only; no Kinesis/SDK control is used. New-copy integrity is recorded
in records/webui-apt-validation.json, separately from the historical four-manual manifest.

The [source register](../sources.md) records manufacturer URLs, protocol mirror
URLs, relevant sections and known contract gaps. The
[verification manifest](../../records/manuals-verification.json) records local
paths, byte counts, hashes, page counts and origin URLs. Copyright and notices
remain with Thorlabs; no ownership or open-source license is asserted for these
documents.

PROJECT.md now records the user's SH05R load selection. Its manufacturer-authored
manual was reviewed online as SRC-009 in the source register, but a local
unchanged load PDF is still missing: the mirror timed out and the legacy
manufacturer download returned HTML. Four PDFs remain in this working tree;
the earlier Issue 36 PDF remains in Git history. The dated verification manifests
retain their original five-document scope. Manuals do not establish present
wiring or optical behavior.
