import os
import glob
import csv

DOWNLOADS_DIR = r"C:\Users\ssaum\Downloads"

def inspect_files():
    csv_files = glob.glob(os.path.join(DOWNLOADS_DIR, "Reason_PM_Poshan_Yojana_List_*.csv"))
    # Sort chronologically by timestamp in filename
    # File name format: Reason_PM_Poshan_Yojana_List_<timestamp>.csv
    def get_timestamp(path):
        name = os.path.basename(path)
        parts = name.replace(".csv", "").split("_")
        try:
            return int(parts[-1])
        except ValueError:
            return 0
            
    csv_files.sort(key=get_timestamp)
    
    print(f"Found {len(csv_files)} reason list CSV files:")
    for idx, path in enumerate(csv_files):
        name = os.path.basename(path)
        timestamp = get_timestamp(path)
        size = os.path.getsize(path)
        
        # Read first few lines and count rows
        row_count = 0
        sample_rows = []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for r in reader:
                    row_count += 1
                    if len(sample_rows) < 3:
                        sample_rows.append(r)
        except Exception:
            try:
                with open(path, 'r', encoding='latin-1') as f:
                    reader = csv.reader(f)
                    for r in reader:
                        row_count += 1
                        if len(sample_rows) < 3:
                            sample_rows.append(r)
            except Exception as e:
                print(f"Error reading {name}: {e}")
                continue
                
        print(f"Index {idx+1}: {name} (size: {size} bytes, rows: {row_count})")
        print(f"  Header: {sample_rows[0] if sample_rows else 'None'}")
        if len(sample_rows) > 1:
            print(f"  Row 1:  {sample_rows[1]}")

if __name__ == '__main__':
    inspect_files()
