"""RK02-centered identifier normalization and interval association.

This is a NEW, testable refactor, not the original August 2025 script.
"""
from bisect import bisect_right

FIELDS = ("DISTRICT_NO", "DISTRICT_NO_SOURCE", "LEASE_NO", "LEASE_NO_SOURCE",
          "WELL_NO", "WELL_NO_SOURCE", "RECORD_TYPE")

def completion_identifiers(row):
    code = str(row.get("WB-OIL-CODE") or row.get("WB-GAS-CODE") or "").strip().upper()
    if code == "O":
        names = ("WB-OIL-DIST", "WB-OIL-LSE-NBR", "WB-OIL-WELL-NBR")
    elif code == "G":
        names = ("WB-GAS-DIST", "WB-GAS-RRC-ID", "WB-GAS-WELL-NO")
    else:
        raise ValueError(f"Unrecognized completion type: {code!r}")
    values = [row.get(name) for name in names]
    result = {"RECORD_TYPE": code}
    for target, source, value in zip(("DISTRICT_NO", "LEASE_NO", "WELL_NO"), names, values):
        result[target] = value
        result[target + "_SOURCE"] = source
    return result

def enrich_records(records):
    """Records: iterable of (line_number, root_key, parsed_row).

    RK01 is used ONLY as a boundary marker to avoid leaking RK02 metadata
    into the next wellbore; RK01 fields are not used as join identifiers.
    The nearest preceding RK02 is used within each RK01-delimited group.
    Records before the first RK02 remain unassigned.
    """
    records = list(records)
    if any(records[i][0] >= records[i+1][0] for i in range(len(records)-1)):
        raise ValueError("Records must be in strictly increasing source line order")
    starts, completions, boundaries = [], [], []
    for number, key, row in records:
        if key == "01":
            boundaries.append(number)
        elif key == "02":
            starts.append(number)
            completions.append(completion_identifiers(row))
    enriched = []
    for number, key, row in records:
        if key == "01":
            continue
        output = dict(row)
        position = bisect_right(starts, number) - 1
        last_boundary = boundaries[bisect_right(boundaries, number)-1] if bisect_right(boundaries, number) else None
        if position >= 0 and (last_boundary is None or starts[position] > last_boundary):
            output.update(completions[position])
        if key == "13" and output.get("WB-WGS84-LONGITUDE") is not None:
            output["WB-WGS84-LONGITUDE"] = -abs(output["WB-WGS84-LONGITUDE"])
        enriched.append((number, key, output))
    return enriched
