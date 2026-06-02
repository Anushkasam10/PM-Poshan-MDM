import os
import glob
import csv
import json
import traceback

DOWNLOADS_DIR = r"C:\Users\ssaum\Downloads"
DATA_DIR = r"C:\Users\ssaum\.gemini\antigravity-ide\scratch\mdm-dashboards\data"

# Mapping based on "bottom to top" dropdown order (oldest file to newest file)
REASON_MAPPING = {
    "1780378790": "Food Not Arrived from NGO/SHG",
    "1780378906": "Others",
    "1780379032": "Flood",
    "1780379263": "Holiday",
    "1780379471": "Single teacher",
    "1780379681": "Village dispute",
    "1780380043": "Vss problem",
    "1780380174": "Students are absent",
    "1780380366": "Vendor problem",
    "1780380558": "Cook not available",
    "1780380704": "Water problem",
    "1780380822": "LPG not available",
    "1780380934": "Grain not available"
}

def clean_val(val):
    if val is None:
        return ""
    return str(val).strip()

def merge_reasons():
    print("Starting merge of 13 reason-wise files...")
    
    # Store all school records with their associated reasons
    # Key: UDISE Code, Value: dict containing school info and set of reasons
    schools_db = {}
    
    # Track count of schools per reason
    reason_counts = {reason: 0 for reason in REASON_MAPPING.values()}
    
    for ts, reason in REASON_MAPPING.items():
        filename = f"Reason_PM_Poshan_Yojana_List_{ts}.csv"
        path = os.path.join(DOWNLOADS_DIR, filename)
        
        if not os.path.exists(path):
            print(f"Warning: File not found {filename}")
            continue
            
        print(f"Processing {filename} for reason: '{reason}'...")
        
        # Read file row by row
        rows = []
        for enc in ['utf-8', 'latin-1', 'iso-8859-1']:
            try:
                with open(path, 'r', encoding=enc) as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                break
            except UnicodeDecodeError:
                continue
                
        if not rows:
            print(f"Error: Could not read {filename}")
            continue
            
        # First row is header
        header = [x.strip() for x in rows[0]]
        udise_idx = -1
        school_name_idx = -1
        district_idx = -1
        block_idx = -1
        mgt_idx = -1
        cat_idx = -1
        
        for idx, h in enumerate(header):
            h_lower = h.lower()
            if 'udise' in h_lower:
                udise_idx = idx
            elif 'school' in h_lower and 'category' not in h_lower:
                school_name_idx = idx
            elif 'district' in h_lower:
                district_idx = idx
            elif 'block' in h_lower:
                block_idx = idx
            elif 'management' in h_lower or 'mgt' in h_lower:
                mgt_idx = idx
            elif 'category' in h_lower:
                cat_idx = idx
                
        if udise_idx == -1:
            print(f"Error: Could not find UDISE column in {filename}. Header was: {header}")
            continue
            
        # Process data rows
        file_school_count = 0
        for r_idx in range(1, len(rows)):
            row = rows[r_idx]
            if not row or len(row) <= udise_idx:
                continue
                
            udise = clean_val(row[udise_idx])
            if not udise or udise == "None":
                continue
                
            file_school_count += 1
            
            # Extract attributes
            name = clean_val(row[school_name_idx]) if school_name_idx != -1 else "Unknown"
            dist = clean_val(row[district_idx]) if district_idx != -1 else "Unknown"
            blk = clean_val(row[block_idx]) if block_idx != -1 else "Unknown"
            mgt = clean_val(row[mgt_idx]) if mgt_idx != -1 else "Unknown"
            cat = clean_val(row[cat_idx]) if cat_idx != -1 else "Unknown"
            
            # Add to DB
            if udise not in schools_db:
                schools_db[udise] = {
                    "udise": udise,
                    "name": name,
                    "district": dist,
                    "block": blk,
                    "management": mgt,
                    "category": cat,
                    "reasons": []
                }
            
            # Append reason if not already present
            if reason not in schools_db[udise]["reasons"]:
                schools_db[udise]["reasons"].append(reason)
                
        reason_counts[reason] = file_school_count
        print(f"  Associated {file_school_count} schools with reason '{reason}'")
        
    # Write aggregated reason counts
    counts_path = os.path.join(DATA_DIR, "reason_counts.json")
    with open(counts_path, 'w', encoding='utf-8') as f:
        json.dump(reason_counts, f, ensure_ascii=False, indent=2)
    print(f"Saved aggregated reason counts to: reason_counts.json")
    
    # Write merged list of schools
    merged_schools_list = list(schools_db.values())
    schools_path = os.path.join(DATA_DIR, "reason_wise_schools.json")
    with open(schools_path, 'w', encoding='utf-8') as f:
        json.dump(merged_schools_list, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(merged_schools_list)} merged school records to: reason_wise_schools.json")
    
    # Aggregated counts by district for each reason
    # Key: District Name, Value: dict of reason counts
    district_reason_counts = {}
    for school in merged_schools_list:
        dist = school["district"]
        if dist not in district_reason_counts:
            district_reason_counts[dist] = {reason: 0 for reason in REASON_MAPPING.values()}
        for reason in school["reasons"]:
            district_reason_counts[dist][reason] += 1
            
    dist_reasons_path = os.path.join(DATA_DIR, "district_reason_counts.json")
    with open(dist_reasons_path, 'w', encoding='utf-8') as f:
        json.dump(district_reason_counts, f, ensure_ascii=False, indent=2)
    print("Saved district-wise reason counts to: district_reason_counts.json")
    
    print("\nMerge complete successfully!")

if __name__ == '__main__':
    merge_reasons()
