import os
import sys
import json
import traceback

def install_dependencies():
    print("Checking dependencies...")
    try:
        import pandas
        import openpyxl
        print("Dependencies found.")
    except ImportError:
        print("Missing pandas or openpyxl. Attempting to install...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "openpyxl"])
            print("Successfully installed dependencies.")
        except Exception as e:
            print(f"Failed to install dependencies: {e}")
            sys.exit(1)

install_dependencies()

import pandas as pd
import numpy as np

DOWNLOADS_DIR = r"C:\Users\ssaum\Downloads"
DATA_DIR = r"C:\Users\ssaum\.gemini\antigravity-ide\scratch\mdm-dashboards\data"

FILES_TO_PROCESS = [
    {
        "name": "MdmServedCountReport_1780376275.xlsx",
        "type": "excel",
        "out": "served_count.json",
        "desc": "PM Poshan Yojna (MDM) - Served Student Count Report"
    },
    {
        "name": "MdmStockReport_1780376443.xlsx",
        "type": "excel",
        "out": "stock_report.json",
        "desc": "PM Poshan Yojna Total School Stock Report"
    },
    {
        "name": "SchoolTaggedForMDMCountReport_1780376562.xlsx",
        "type": "excel",
        "out": "school_tagged.json",
        "desc": "MDM School Tagging Count Report"
    },
    {
        "name": "ReasonWiseNoOfSchoolMdmNotServed_1780377052.xlsx",
        "type": "excel",
        "out": "reason_not_served.json",
        "desc": "Reason wise no of school where PM Poshan Yojna (MDM) not served"
    },
    {
        "name": "Reason_PM_Poshan_Yojana_List_1780376745.csv",
        "type": "csv",
        "out": "reason_yojana_list.json",
        "desc": "Reason wise PM Poshan Yojana Count Report"
    },
    {
        "name": "schoolNotSubmittedPMPoshanYojana_report_1780376412.csv",
        "type": "csv",
        "out": "not_submitted_report.json",
        "desc": "PM Poshan Yojna Total School Not Submitted MDM"
    }
]

def clean_val(val):
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        # Convert numpy types to native Python types
        if isinstance(val, (np.integer, int)):
            return int(val)
        if isinstance(val, (np.floating, float)):
            return float(val)
        return val
    val_str = str(val).strip()
    try:
        if '.' in val_str:
            return float(val_str)
        return int(val_str)
    except ValueError:
        return val_str

def parse_metadata_and_header(rows):
    """
    Scans list of rows to extract metadata (key-value before header)
    and find the main header index.
    """
    metadata = {}
    header_idx = -1
    
    for idx, row in enumerate(rows):
        row_clean = [str(x).strip() for x in row if not pd.isna(x) and str(x).strip() != '']
        if not row_clean:
            continue
            
        # Check if this row looks like a table header
        row_lower = [r.lower() for r in row_clean]
        if any(h in row_lower for h in ['sln#', 'sl.no', 'sl. no', 'district name', 'district', 'udise code', 'udise']):
            header_idx = idx
            break
            
        # If it contains ': --' or ':-' or is key-value
        for cell in row_clean:
            if ':-' in cell or ':' in cell:
                parts = cell.split(':', 1)
                key = parts[0].strip()
                val = parts[1].strip() if len(parts) > 1 else ''
                if key and val:
                    metadata[key] = val
            elif len(row_clean) == 2:
                # Key and value in adjacent cells
                k, v = row_clean[0], row_clean[1]
                if 'district' in k.lower() or 'block' in k.lower() or 'date' in k.lower() or 'generated' in k.lower():
                    metadata[k] = v
            elif len(row_clean) == 1 and idx < 3:
                # Page heading or title
                if 'bihar education' in row_clean[0].lower() or 'pm poshan' in row_clean[0].lower():
                    metadata['Title'] = row_clean[0]
                    
    return metadata, header_idx

def process_single_file(file_info):
    name = file_info["name"]
    file_type = file_info["type"]
    out_name = file_info["out"]
    
    input_path = os.path.join(DOWNLOADS_DIR, name)
    
    if not os.path.exists(input_path):
        print(f"File not found: {name}")
        return False
        
    try:
        # Load all rows as raw lists first to analyze structure
        raw_rows = []
        
        if file_type == "excel":
            xls = pd.ExcelFile(input_path, engine='openpyxl')
            sheet_name = xls.sheet_names[0] # use first sheet
            df_raw = pd.read_excel(input_path, sheet_name=sheet_name, header=None, engine='openpyxl')
            raw_rows = df_raw.values.tolist()
        else: # csv
            import csv
            raw_rows = []
            for enc in ['utf-8', 'latin-1', 'iso-8859-1']:
                try:
                    with open(input_path, 'r', encoding=enc) as f:
                        reader = csv.reader(f)
                        raw_rows = list(reader)
                    break
                except UnicodeDecodeError:
                    continue
            if not raw_rows:
                raise ValueError("Could not decode CSV file with any supported encoding.")
            
        # Parse metadata and locate header row
        metadata, header_idx = parse_metadata_and_header(raw_rows)
        
        if header_idx == -1:
            # Fallback if no header found: use first row
            header_idx = 0
            
        # Headers clean
        headers = [str(x).strip() for x in raw_rows[header_idx]]
        # Remove empty headers at the end
        while headers and (headers[-1] == 'None' or headers[-1] == ''):
            headers.pop()
            
        print(f"  Header found at row {header_idx + 1}: {headers}")
        
        # Parse data rows
        data_records = []
        summary_totals = {}
        
        for r_idx in range(header_idx + 1, len(raw_rows)):
            row = raw_rows[r_idx]
            # Make sure we don't exceed header count
            row_cells = [clean_val(row[c_idx]) if c_idx < len(row) else None for c_idx in range(len(headers))]
            
            # Skip empty rows
            if all(c is None for c in row_cells):
                continue
                
            first_cell = row_cells[0]
            
            # Check if this is the summary/total row
            is_total_row = False
            first_cell_str = str(first_cell).strip().lower()
            if first_cell_str in ['total', 'grand total', 'total school', 'total / total'] or any(str(c).strip().lower() == 'total' for c in row_cells[:2]):
                is_total_row = True
                
            if is_total_row:
                for h_idx, h in enumerate(headers):
                    summary_totals[h] = row_cells[h_idx]
            else:
                record = {}
                for h_idx, h in enumerate(headers):
                    record[h] = row_cells[h_idx]
                
                # Check if first cell is just index and others are empty
                non_null_count = sum(1 for v in record.values() if v is not None)
                if non_null_count > 1: # more than just SLN#
                    data_records.append(record)
                    
        # Special optimization for the huge not-submitted school report (66,000+ records)
        if out_name == "not_submitted_report.json":
            df_schools = pd.DataFrame(data_records)
            
            # Aggregate counts for charts
            district_summary = df_schools.groupby('District').size().to_dict()
            block_summary = df_schools.groupby(['District', 'Block']).size().reset_index(name='count')
            block_summary_dict = {}
            for _, r in block_summary.iterrows():
                d = r['District']
                b = r['Block']
                c = int(r['count'])
                if d not in block_summary_dict:
                    block_summary_dict[d] = {}
                block_summary_dict[d][b] = c
                
            category_summary = df_schools.groupby('School Category').size().to_dict()
            management_summary = df_schools.groupby('School Management').size().to_dict()
            
            summary_totals = {
                "Total Districts": len(district_summary),
                "Total Not Submitted Schools": len(df_schools)
            }
            
            # Write aggregated metadata separately
            agg_data = {
                "metadata": metadata,
                "summary": summary_totals,
                "district_counts": district_summary,
                "block_counts": block_summary_dict,
                "category_counts": category_summary,
                "management_counts": management_summary
            }
            
            # Save summary file
            summary_path = os.path.join(DATA_DIR, "not_submitted_summary.json")
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(agg_data, f, ensure_ascii=False, indent=2)
            print(f"  Created aggregated summary at: not_submitted_summary.json")
            
            # Save optimized schools file (full list) for searching
            schools_optimized = []
            for r in data_records:
                schools_optimized.append({
                    "d": r.get("District"),
                    "b": r.get("Block"),
                    "c": r.get("Cluster"),
                    "u": r.get("UDISE Code"),
                    "n": r.get("School Name"),
                    "cat": r.get("School Category"),
                    "m": r.get("School Management")
                })
                
            schools_full_path = os.path.join(DATA_DIR, "not_submitted_schools.json")
            with open(schools_full_path, 'w', encoding='utf-8') as f:
                json.dump(schools_optimized, f, ensure_ascii=False)
            print(f"  Created full school records (compressed) at: not_submitted_schools.json")
            
        else:
            # Standard formatting for other files
            output_data = {
                "metadata": metadata,
                "summary": summary_totals,
                "data": data_records
            }
            
            output_path = os.path.join(DATA_DIR, out_name)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"  Saved cleaned data to: {out_name} (records: {len(data_records)})")
            
        return True
    except Exception as e:
        print(f"Error parsing {name}:")
        traceback.print_exc()
        return False

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    success_count = 0
    for file_info in FILES_TO_PROCESS:
        if process_single_file(file_info):
            success_count += 1
            
    print(f"\nProcessing complete: {success_count}/{len(FILES_TO_PROCESS)} files processed successfully.")

if __name__ == '__main__':
    main()
