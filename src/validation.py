"""Basic structural and identifier validation helpers."""
def validate_records(records):
    errors = []
    previous = 0
    for number, key, row in records:
        if number <= previous:
            errors.append(f"Line {number}: non-increasing source order")
        previous = number
        if key == "02":
            code = str(row.get("RECORD_TYPE", "")).strip()
            if code not in {"O", "G"}:
                errors.append(f"Line {number}: missing/invalid completion type")
            for name in ("DISTRICT_NO", "LEASE_NO", "WELL_NO"):
                if row.get(name) in (None, ""):
                    errors.append(f"Line {number}: missing {name}")
        if key == "13":
            lon = row.get("WB-WGS84-LONGITUDE")
            if lon is not None and not -180 <= lon <= 180:
                errors.append(f"Line {number}: invalid longitude")
    return errors
