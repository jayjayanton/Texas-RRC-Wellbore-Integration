# Data dictionary

The authoritative field positions, widths and PIC types are in the RRC *Oil and Gas Well Bore System: Magnetic Tape User's Guide* (WBA091, updated May 2019), and the corresponding copybooks. This document covers the **derived** columns introduced by the Python workflow.

| Column | Meaning | Source |
| --- | --- | --- |
| `LineNumber` | 1-based position in DBF900 ASCII file | Parser |
| `RECORD_TYPE` | O (oil) or G (gas) | RK02 oil/gas code |
| `DISTRICT_NO` | RRC district | RK02 oil or gas district |
| `DISTRICT_NO_SOURCE` | Original field name used | RK02 |
| `LEASE_NO` | Oil lease number **or** gas RRC ID; different semantics | RK02 |
| `LEASE_NO_SOURCE` | Original oil lease / gas ID field | RK02 |
| `WELL_NO` | Well number | RK02 |
| `WELL_NO_SOURCE` | Original well number field | RK02 |

**Important:** `LEASE_NO` is a historical normalized column name, not proof that gas IDs are lease numbers. Preserve `RECORD_TYPE` and provenance fields when joining.

## Record keys addressed in the historical August 2 script

| Key | Segment |
| --- | --- |
| 01 | WBROOT — wellbore characteristics, separate from RK02 linkage |
| 02 | WBCOMPL — completion identifiers |
| 03 | WBDATE — dates |
| 04 | WBRMKS — remarks |
| 05 | WBTUBE — tubing |
| 06 | WBCASE — casing |
| 07 | WBPERF — perforations |
| 08 | WBLINE — liner |
| 09 | WBFORM — formation |
| 10 | WBSQEZE — squeeze |
| 11 | WBFRESH — usable-quality water protection |
| 12 | WBOLDLOC — old location |
| 13 | WBNEWLOC — new location |

See the official RRC manual for original fields and the full 01–28 segment catalog.
