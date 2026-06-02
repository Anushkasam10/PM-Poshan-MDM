import os
import glob

DOWNLOADS_DIR = r"C:\Users\ssaum\Downloads"

def find_files():
    # Find all Excel and CSV files in Downloads
    excel_files = glob.glob(os.path.join(DOWNLOADS_DIR, "*.xlsx"))
    csv_files = glob.glob(os.path.join(DOWNLOADS_DIR, "*.csv"))
    
    print("Excel files in Downloads:")
    # Sort by modification time to see the most recent ones first
    excel_files.sort(key=os.path.getmtime, reverse=True)
    for f in excel_files[:25]:
        mtime = os.path.getmtime(f)
        size = os.path.getsize(f)
        print(f"  {os.path.basename(f)} (size: {size} bytes, modified: {mtime})")
        
    print("\nCSV files in Downloads:")
    csv_files.sort(key=os.path.getmtime, reverse=True)
    for f in csv_files[:25]:
        mtime = os.path.getmtime(f)
        size = os.path.getsize(f)
        print(f"  {os.path.basename(f)} (size: {size} bytes, modified: {mtime})")

if __name__ == '__main__':
    find_files()
