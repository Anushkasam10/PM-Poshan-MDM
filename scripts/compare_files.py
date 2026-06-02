import os
import csv

DOWNLOADS_DIR = r"C:\Users\ssaum\Downloads"

def compare():
    p1 = os.path.join(DOWNLOADS_DIR, "Reason_PM_Poshan_Yojana_List_1780376745.csv")
    p2 = os.path.join(DOWNLOADS_DIR, "Reason_PM_Poshan_Yojana_List_1780380822.csv")
    
    rows1 = []
    with open(p1, 'r', encoding='utf-8') as f:
        rows1 = list(csv.reader(f))
        
    rows2 = []
    with open(p2, 'r', encoding='utf-8') as f:
        rows2 = list(csv.reader(f))
        
    print(f"File 1: {len(rows1)} rows")
    print(f"File 2: {len(rows2)} rows")
    
    # Compare first 5 rows
    print("Match first 5 rows?")
    match = True
    for i in range(min(5, len(rows1), len(rows2))):
        print(f"Row {i}: {rows1[i] == rows2[i]}")
        if rows1[i] != rows2[i]:
            match = False
    print(f"Overall Match: {match}")

if __name__ == '__main__':
    compare()
