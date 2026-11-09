# Texas RRC Wellbore Integration

**Legacy data engineering | Python | COBOL copybooks | Fixed-width ASCII | Record linkage | CSV / relational data preparation**

This repository documents a historical data engineering workflow developed to extract and organize the Railroad Commission of Texas (RRC) **Full Wellbore / DBF900** dataset. The work focused on parsing heterogeneous record types and using **Root Key 02 (WBCOMPL)** as the primary source of completion identifiers for association with other technical root-key records.

## Source data and documentation

- [Texas RRC — Data Sets Available for Download](https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/) — select **Oil & Gas Well Data → Full Wellbore → ASCII Format**.
- RRC, *Oil and Gas Well Bore System: Magnetic Tape User's Guide* (publication WBA091, updated May 20, 2019). This official guide describes the 247-character records, record keys, field positions and hierarchical record layout.
- Copybooks were derived from the RRC record layouts to support field-by-field parsing.

The raw statewide data are **not included** in this repository. Obtain current data from the RRC and review their documentation before use.

## Historical workflow

1. **Ingest:** Read DBF900 fixed-width records, using the first two characters to identify each record type.
2. **Parse:** Load per-record-type COBOL copybooks; interpret field positions, data types and zoned-decimal numeric values.
3. **Normalize identifiers:** Extract district, lease / RRC gas ID and well number from RK02. Retain source-field provenance through `DISTRICT_NO_SOURCE`, `LEASE_NO_SOURCE` and `WELL_NO_SOURCE`.
4. **Associate records:** Locate the nearest preceding RK02 completion interval using `bisect_right` and propagate normalized identifiers to RK02–RK13 outputs.
5. **Export:** Produce separate CSV tables for subsequent relational integration; perform selected transformations such as negative Texas WGS84 longitudes.

**RK01 (WBROOT)** was also investigated for wellbore characteristics and API-related fields, but RK01-based linkage was **not required for the specific RK02-centered extraction workflow** documented here.

## Implementation history

- `RK_Lookup.py`: earlier RK02 composite-key lookup experiment.
- `Root_Key_Final_Fixed_Errors (1).py` (August 2, 2025): RK02 position-based interval association with binary search, CSV exports and field provenance.
- `Integrated_RK01.py`: separate exploratory attempt to connect RK01 API characteristics.

See [Methodology and known limitations](docs/methodology.md). The archived implementation is preserved for historical review; it is **not presented as a production-ready, validated pipeline**.

## Important caveats

- The historical RK02 interval boundaries do not explicitly stop at a new RK01 wellbore boundary; associations require validation against source record order.
- The oil/gas field selection logic needs explicit classification-aware handling, including COBOL `REDEFINES`.
- A logger is configured, but the August 2 parsing loop suppresses exceptions without populating the structured error list.
- Performance improvements are algorithmic (binary search); no measured benchmark or verified join accuracy is claimed.

## Repository roadmap

- [x] Document official source and historical approach
- [x] Archive the August 2 historical script with local machine paths redacted
- [ ] Add reviewed copybooks and synthetic test fixtures
- [ ] Refactor into configurable modules
- [ ] Validate oil/gas field normalization and record boundaries
- [ ] Add unit and integration tests
- [ ] Document downstream SQL schema and joins after confirming original implementation

## Attribution

Historical implementation and project documentation: Jay Oliver. Source dataset and record layout documentation: Railroad Commission of Texas. This is an independent project repository, not an official RRC product.
