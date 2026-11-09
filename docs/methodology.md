# Methodology and implementation notes

## Source structure
The RRC WBA091 guide describes a fixed-width DBF900 file with a two-character segment identifier. The original workflow used individual COBOL-style copybooks to parse each root key.

## Why RK02?
RK02 (WBCOMPL) provides completion-level oil and gas identifiers that can be propagated into separate technical record exports, many of which do not independently carry those identifiers. RK01 was used primarily to investigate wellbore characteristics and API information, rather than as the required join basis for this workflow.

## Identifier standardization
The historical implementation produced `DISTRICT_NO`, `LEASE_NO`, `WELL_NO`, `COMP_NO` and associated `*_SOURCE` fields. The source fields distinguish original RRC oil/gas columns, although the code does **not** fully implement a classification-aware resolution rule. In particular, `LEASE_NO` may represent an oil lease number or gas RRC ID; these are different identifier types and should not be assumed interchangeable.

## Association method
The August 2, 2025 script first records RK02 line positions and builds completion metadata. It then sorts those positions, constructs intervals ending at the next RK02, and uses `bisect_right` to locate the nearest preceding interval for each parsed RK02–RK13 record. The intended benefit is efficient lookup and propagation of completion identifiers into separate CSV outputs.

## Validation limitations
1. Intervals are bounded by the next RK02, not explicitly by the next RK01. This could misassociate records near wellbore boundaries.
2. The `WB-OIL-KEY` and `WB-GAS-KEY` share bytes via COBOL `REDEFINES`; a robust implementation must branch on the record classification.
3. The lookup key in the August 2 version is constructed from gas-specific fields, so collisions and incorrect matching require investigation.
4. Exceptions in the main parser are silently converted to null values; the configured error log does not demonstrate successful error auditing.
5. Output filenames and column schemas should be checked against actual generated CSVs before reporting validated outcomes.
6. No benchmark, SQL ingestion code, or independently confirmed production results are included here.

## Next steps
Preserve the historical implementation, add synthetic fixtures based on the published layout, verify each record association, then implement a configurable and tested version. Any future refactor should be explicitly distinguished from the historical code.

## References
- [RRC datasets](https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/)
- RRC, *Oil and Gas Well Bore System: Magnetic Tape User's Guide*, WBA091 (May 20, 2019), especially the system description, record-key table, RK02 completion layout, and RK13 location layout.
