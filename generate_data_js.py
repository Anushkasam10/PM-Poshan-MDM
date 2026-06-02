import os
import json

DATA_DIR = r"C:\Users\ssaum\.gemini\antigravity-ide\scratch\mdm-dashboards\data"
JS_DIR = r"C:\Users\ssaum\.gemini\antigravity-ide\scratch\mdm-dashboards\js"

def compile_data_js():
    print("Compiling JSON files to js/data.js...")
    
    files_to_load = {
        "served_count": "served_count.json",
        "stock_report": "stock_report.json",
        "school_tagged": "school_tagged.json",
        "reason_not_served": "reason_not_served.json",
        "not_submitted_summary": "not_submitted_summary.json",
        "reason_counts": "reason_counts.json",
        "reason_wise_schools": "reason_wise_schools.json"
    }
    
    mdm_data = {}
    
    for key, filename in files_to_load.items():
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            print(f"Warning: Data file not found {filename}")
            continue
            
        print(f"Loading {filename}...")
        with open(path, 'r', encoding='utf-8') as f:
            mdm_data[key] = json.load(f)
            
    # Write to js/data.js
    os.makedirs(JS_DIR, exist_ok=True)
    js_path = os.path.join(JS_DIR, "data.js")
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write("// Compiled MDM Data for Offline CORS-free Dashboard\n")
        f.write("window.MDM_DATA = ")
        json.dump(mdm_data, f, ensure_ascii=False, indent=2)
        f.write(";\n")
        
    print(f"Successfully compiled all datasets into: {js_path} (size: {os.path.getsize(js_path)} bytes)")

if __name__ == '__main__':
    compile_data_js()
