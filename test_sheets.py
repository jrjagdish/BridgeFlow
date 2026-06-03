from sheets_client import fetch_sheet_data
rows = fetch_sheet_data() 
for row in rows: 
    print(row)