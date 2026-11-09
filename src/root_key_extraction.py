"""CLI: parse DBF900 records and export RK02–RK13 CSVs.

Example: python -m src.root_key_extraction --source dbf900.txt --copybooks copybooks --output output
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path
from .copybook_parser import load_copybooks, parse_record
from .wellbore_integration import enrich_records

NAMES = {"02":"WBCOMPL","03":"WBDATE","04":"WBRMKS","05":"WBTUBE",
         "06":"WBCASE","07":"WBPERF","08":"WBLINE","09":"WBFORM",
         "10":"WBSQEZE","11":"WBFRESH","12":"WBOLDLOC","13":"WBNEWLOC"}

def extract(source, copybooks, output):
    layouts = load_copybooks(copybooks)
    parsed = []
    with open(source, encoding="latin-1") as stream:
        for number, line in enumerate(stream, 1):
            key = line[:2]
            if key not in layouts or key not in {"01", *NAMES}:
                continue
            try:
                row = parse_record(line.rstrip("\r\n"), layouts[key])
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Line {number}, key {key}: {exc}") from exc
            parsed.append((number, key, row))
    groups = defaultdict(list)
    for number, key, row in enrich_records(parsed):
        if key in NAMES:
            groups[key].append({"LineNumber":number, **row})
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    for key, rows in groups.items():
        columns = list(dict.fromkeys(column for row in rows for column in row))
        with (destination / f"{key}_{NAMES[key]}_out.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
    return {key:len(rows) for key, rows in groups.items()}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--copybooks", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(extract(args.source, args.copybooks, args.output))

if __name__ == "__main__":
    main()
