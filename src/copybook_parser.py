"""Fixed-width COBOL copybook adapter for the historical RRC workflow.

Requires the third-party 'copybook' package used in the original scripts.
"""
from pathlib import Path
import re

ZONES = dict(zip("{ABCDEFGHI}JKLMNOPQR", list("0123456789") + list("0123456789")))

def zoned_to_number(value, precision=0):
    value = value.strip()
    if not value:
        return None
    sign = -1 if value[-1] in "}JKLMNOPQR" else 1
    if value[-1] in ZONES:
        value = value[:-1] + ZONES[value[-1]]
    value = re.sub(r"[^\x20-\x7e]", "", value).replace(",", "")
    if not value.isdigit():
        raise ValueError(f"Invalid zoned decimal: {value!r}")
    return sign * (int(value) / 10**precision)

def load_copybooks(directory):
    import copybook
    layouts = {}
    for path in sorted(Path(directory).glob("*.cpy")):
        source = "\n".join(line for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
                           if not line.strip().startswith("*"))
        layouts[f"{int(path.stem):02d}"] = copybook.parse_string(source)
    return layouts

def parse_record(line, layout):
    import copybook
    row = {}
    for field in layout.flatten():
        if not isinstance(field, copybook.Field):
            continue
        raw = line[field.start_pos:field.start_pos + field.get_total_length()].strip()
        kind = "alphanum" if field.name.upper() == "WB-RULE-37-NBR" else field.datatype
        if kind == "decimal":
            value = zoned_to_number(raw, field.precision)
        elif kind == "int":
            value = zoned_to_number(raw)
            value = int(value) if value is not None else None
        elif kind == "alphanum":
            value = raw
        else:
            value = field.parse(raw)
        row[field.name.upper()] = value
    return row
