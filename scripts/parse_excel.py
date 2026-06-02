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
            print(f"Failed to install dependencies automatically: {e}")
            print("Please run: pip install pandas openpyxl")
            sys.exit(1)

# Check and install if needed
install_dependencies()

import pandas as pd

def clean_value(val):
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return val
    # Clean string values
    val_str = str(val).strip()
    # Try converting to float/int if numeric representation
    try:
        if '.' in val_str:
            return float(val_str)
        return int(val_str)
    except ValueError:
        return val_str

def parse_excel_to_json(excel_path, json_output_path):
    print(f"Reading file: {excel_path}")
    if not os.path.exists(excel_path):
        print(f"Error: File not found at {excel_path}")
        return False
        
    try:
        # Load the workbook
        xls = pd.ExcelFile(excel_path, engine='openpyxl')
        sheet_names = xls.sheet_names
        print(f"Sheets found: {sheet_names}")
        
        result_data = {}
        
        for sheet_name in sheet_names:
            print(f"Processing sheet: {sheet_name}")
            df = pd.read_excel(excel_path, sheet_name=sheet_name, engine='openpyxl')
            
            # Clean headers: remove trailing/leading spaces, empty headers, etc.
            # Convert to string and strip
            df.columns = [str(c).strip() if not pd.isna(c) else f"Unnamed_{i}" for i, c in enumerate(df.columns)]
            
            records = []
            for _, row in df.iterrows():
                record = {}
                for col in df.columns:
                    record[col] = clean_value(row[col])
                records.append(record)
                
            # If there's only one sheet, we can store it directly or key it
            result_data[sheet_name] = records
            
        # Ensure target dir exists
        os.makedirs(os.path.dirname(json_output_path), exist_ok=True)
        
        # Write to JSON
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully wrote JSON data to: {json_output_path}")
        return True
        
    except Exception as e:
        print("An error occurred during Excel parsing:")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python parse_excel.py <path_to_excel_file> <path_to_output_json>")
        sys.exit(1)
        
    excel_file = sys.argv[1]
    output_json = sys.argv[2]
    
    success = parse_excel_to_json(excel_file, output_json)
    sys.exit(0 if success else 1)
