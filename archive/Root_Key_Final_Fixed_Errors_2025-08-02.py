# HISTORICAL ARCHIVE — original script with internal local paths redacted.
# Not independently validated; see docs/methodology.md.
# Replace <LOCAL_...> placeholders before running.

import csv
import copybook
import glob
from pathlib import PurePath
import os
import logging
import re
import csv
from datetime import datetime
import pretty_errors
import bisect

def preprocess_copybook(file_path):
    """Removes comment lines before parsing"""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
   
    # Filter out leading comment lines
    cleaned_lines = []
    for line in lines:
        if not line.strip().startswith("*"):  # Skip comment lines
            cleaned_lines.append(line)
   
    # Save to temp file (or use directly)
    return "\n".join(cleaned_lines)

def add_zero_to_single_digit_keys(input_dict):
    updated_dict = {}
    for key, value in input_dict.items():
        if isinstance(key, int) and 0 <= key <= 9:
            new_key = f'0{key}'
        else:
            new_key = str(key)
        updated_dict[new_key] = value
    return updated_dict

def zoned_to_number(input_str, precision):
    if not input_str:
        return None

    ZONED_MAP = {
        '{':('0',1),
        '}':('0',-1),
        'A':('1',1),
        'B':('2',1),
        'C':('3',1),
        'D':('4',1),
        'E':('5',1),
        'F':('6',1),
        'G':('7',1),
        'H':('8',1),
        'I':('9',1),
        'J':('1',-1),
        'K':('2',-1),
        'L':('3',-1),
        'M':('4',-1),
        'N':('5',-1),
        'O':('6',-1),
        'P':('7',-1),
        'Q':('8',-1),
        'R':('9',-1),
    }

    last_char = input_str[-1]
    if last_char in ZONED_MAP:
        digit, sign = ZONED_MAP[last_char]
        numeric = input_str[:-1] + digit
    else:
        numeric = input_str
        sign = 1

    # Remove Non-Printale characters (Nulls)
    numeric = re.sub(r"[^\x20-\x7E]","",numeric)
    
    # Remove commas
    numeric = numeric.replace(",", "")

    # Remove any trailing non-numeric junk
    numeric = re.sub(r"[^\d.-]+$", "", numeric)

    if precision > 0:
        whole = numeric[:-precision] or '0'
        fraction = numeric[-precision:]
        num_str = f"{whole}.{fraction}"
    else:
        num_str = numeric

    try:
        return sign * float(num_str)
    except ValueError:
        raise ValueError(
            f"Could not parse numeric value from: '{input_str}' cleaned as '{num_str}'"
        )

    
def safe_filename(name):
    """Makes a string safe for use as a filename"""
    return "".join(x for x in name if x.isalnum() or x == " ")

def update_progress(i, line_count):
    if i % 10 == 0:
        progress = (i + 1) / line_count
        bar_length = 30
        filled_length = int(bar_length * progress)
        bar = "#" * filled_length + "-" * (bar_length - filled_length)
        print(f"\r[{bar}] {progress:.1%} ", end="", flush=True)

def get_file_length(file):
    t_i = file.tell()
    file.seek(0)
    length = sum(1 for _ in file)
    file.seek(t_i)
    return length

def extract_error_value(error):
    """
    Extracts the value from a ValueError message.
    
    :param error: ValueError exception
    :return: Extracted erroneous value as a string
    """
    error_message = str(error)  # Convert exception to string
    match = re.search(r"'(.*?)'", error_message)
    if match:
        extracted_value = match.group(1)
        return extracted_value
    return None  # Return None if format is unexpected
def safe_filename(name):
    """Makes a string safe for use as a filename"""
    return "".join(x for x in name if x.isalnum() or x == " ")

# ----------------------- Logging Setup ------------------------------
# You may need to hard code this
output_folder = r"<LOCAL_OUTPUT_DIR>"
# Ensure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    
# Use a log file in the data output directory
currentDateTime = datetime.now().strftime("%m-%d-%Y")
log_file = os.path.join(output_folder, f"dbf900_processing_errors_Fixed_Version_{currentDateTime}.log")

# Delete the error file
if os.path.exists(log_file):
    os.remove(log_file)

# Setup the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a new file to log errors
file_handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# ----------------------- Copybook Parsing ------------------------------

# Path to directory containing .cpy files
dir_path = r'<LOCAL_COPYBOOK_DIR>\\*.cpy'
paths = glob.glob(dir_path)

cpy_dict = {}

for p in paths:
    filename = PurePath(p).stem
    # print(f"Processing: {filename}")

    try:
        # Preprocess copybook to remove comments
        preprocessed_content = preprocess_copybook(p)

        if not preprocessed_content.strip():
            print(f"Skipping {filename} (empty after preprocessing)")
            continue  # Skip empty files
        # Parse using cleaned content
        cpy_dict[filename] = copybook.parse_string(preprocessed_content)
    except Exception as e:
        print(f"Error parsing {filename}: {e}")

cpy_dict = {int(k): v for k, v in cpy_dict.items()}
cpy_dict = add_zero_to_single_digit_keys(cpy_dict)

well_bore_dictionary = {
    2: "WBCOMPL", 3: "WBDATE", 4: "WBRMKS", 5: "WBTUBE", 6: "WBCASE", 7: "WBPERF", 8: "WBLINE", 9: "WBFORM", 10: "WBSQEZE",
    11: "WBFRESH", 12: "WBOLDLOC", 13: "WBNEWLOC"}

parent_folder = './dbf900.txt/dbf900'
source_file = r"<LOCAL_SOURCE_FILE>"

well_bore_segments= {f"{key:02}" if isinstance(key,int) else str(key): value for key,value in well_bore_dictionary.items()}

OVERRIDES = {
    'WB-RULE-37-NBR': 'alphanum',
}

propagated_fields = [
    "DISTRICT_NO",
    "DISTRICT_NO_SOURCE",
    "LEASE_NO",
    "LEASE_NO_SOURCE",
    "WELL_NO",
    "WELL_NO_SOURCE",
    "COMP_NO"
]

rk02_lookup = {}
rk02_intervals = []
records_by_key = {str(i).zfill(2): [] for i in range(2, 14)}
error_log = []

# Pass 1: build RK02 lookup and intervals
with open(source_file, "r", encoding='latin-1') as f:
    for i, line in enumerate(f, start=1):
        if line[:2] == "02":
            root = cpy_dict.get("02")
            if not root:
                continue

            row_fields = {"LineNumber": i}
            for field in root.flatten():
                if isinstance(field, copybook.Field):
                    str_field = line[field.start_pos:field.start_pos + field.get_total_length()].strip()
                    datatype = OVERRIDES.get(field.name.upper(), field.datatype)
                    try:
                        parsed = zoned_to_number(str_field, 0) if datatype in ['decimal', 'int'] else str_field
                    except:
                        parsed = None
                    row_fields[field.name.upper()] = parsed

            current_completion_info = {}
            for fname, val in row_fields.items():
                if fname == "WB-OIL-CODE":
                    current_completion_info['RECORD_TYPE'] = val
                elif fname in ["WB-OIL-DIST", "WB-GAS-DIST"]:
                    current_completion_info.update({"DISTRICT_NO": val, "DISTRICT_NO_SOURCE": fname})
                elif fname in ["WB-OIL-LSE-NBR", "WB-GAS-RRC-ID"]:
                    current_completion_info.update({"LEASE_NO": val, "LEASE_NO_SOURCE": fname})
                elif fname in ["WB-OIL-WELL-NBR", "WB-GAS-WELL-NO"]:
                    current_completion_info.update({"WELL_NO": val, "WELL_NO_SOURCE": fname})
                elif fname == "WB-OIL-COMP-NBR":
                    current_completion_info["COMP_NO"] = val

            row_fields.update(current_completion_info)

            key = (
                row_fields.get("WB-GAS-DIST"),
                row_fields.get("WB-GAS-RRC-ID"),
                row_fields.get("WB-GAS-WELL-NO")
            )
            rk02_lookup[key] = row_fields

            rk02_intervals.append({
                "start": i,
                "key": key
            })

# Precompute sorted list of starts for binary search
rk02_intervals.sort(key=lambda x: x["start"])

for idx in range(len(rk02_intervals)):
    if idx < len(rk02_intervals) - 1:
        rk02_intervals[idx]["end"] = rk02_intervals[idx+1]["start"]
    else:
        rk02_intervals[idx]["end"] = float("inf")  # last interval goes to EOF


starts = [iv["start"] for iv in rk02_intervals]

# Pass 2: parse all rows and enrich
with open(source_file, "r", encoding='latin-1') as f:
    total = get_file_length(f)
    for i, line in enumerate(f, start=1):
        update_progress(i - 1, total)
        k = line[:2]
        if k not in records_by_key:
            continue

        csv_row = {"LineNumber": i}
        root = cpy_dict.get(k)
        if not root:
            continue

        for field in root.flatten():
            if isinstance(field, copybook.Field):
                str_field = line[field.start_pos:field.start_pos + field.get_total_length()].strip()
                try:
                    datatype = OVERRIDES.get(field.name.upper(), field.datatype)
                    if datatype == 'decimal':
                        parsed = zoned_to_number(str_field, field.precision)
                    elif datatype == 'int':
                        num = zoned_to_number(str_field, 0)
                        parsed = int(num) if num is not None else None
                    elif datatype == 'alphanum':
                        parsed = str_field
                    else:
                        parsed = field.parse(str_field)
                    csv_row[field.name] = parsed
                except:
                    csv_row[field.name] = None

        # Use binary search to find nearest RK02 interval
        pos = bisect.bisect_right(starts, i) - 1
        if pos >= 0:
            interval = rk02_intervals[pos]
            if interval["start"] <= i < interval["end"]:
                key = interval["key"]
                if key in rk02_lookup:
                    for fld in propagated_fields:
                        csv_row[fld] = rk02_lookup[key].get(fld)

        if k == "13" and csv_row.get("WB-WGS84-LONGITUDE") is not None:
            csv_row["WB-WGS84-LONGITUDE"] = -abs(csv_row["WB-WGS84-LONGITUDE"])

        records_by_key[k].append(csv_row)
# ------------------ Write outputs for values between 2 and 12 -----------------------
for k, rows in records_by_key.items():
    if not rows:
        continue
    SafeRootKeyName = safe_filename(well_bore_segments.get(k,f"Key_{k}"))
    output_file = os.path.join(output_folder, f"{k}_{SafeRootKeyName}_out.csv")
    
    # Ensure Propagated Fields are always present
    copybook_fields = []
    root = cpy_dict.get(k)
    
    if root:
        copybook_fields = [field.name for field in root.flatten() if isinstance(field, copybook.Field)]
    all_fields = ['LineNumber'] + propagated_fields + [f for f in copybook_fields if f not in propagated_fields]
    
    with open(output_file, "w", newline ="", encoding ="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote Rootkey {k} with {len(rows)} records to Output_file")

# Save error log
if error_log:
    error_path = r'<LOCAL_OUTPUT_DIR>\\Error_log'
    os.makedirs(error_path, exist_ok=True)
    error_log_file = os.path.join(error_path, "error_log_all.csv")
    with open(error_log_file, "w", newline='') as file:
        writer = csv.DictWriter(file, fieldnames = ["Root Key", "Field", "Value", "Line"])
        writer.writeheader()
        writer.writerows(error_log)
    
print("\n All processes done")
exit()
