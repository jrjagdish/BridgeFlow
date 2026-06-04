# import json 
# from transformer import row_to_notion_page 
# row = {"ID": "T001", "Task Name": "Test task", "Status": "To Do", "Due Date": "2025-06-15", "Assignee": "Sunil", "Notes": ""} 
# result = row_to_notion_page(row) 
# print(json.dumps(result, indent=2))

from dotenv import load_dotenv 
load_dotenv() 
from notion_client import create_page, verify_database_connection 
from transformer import row_to_notion_page
from config import get_notion_database_id 
# First verify database is accessible 
verify_database_connection(get_notion_database_id()) 
# Then create a test page 
row = {"Task ID": "T001","Tasks": "Test task", "status": "To Do", "Due": "2025-06-15", "Notes": ""} 
props = row_to_notion_page(row) 
page_id = create_page(get_notion_database_id(), props) 
print(f"Created page: {page_id}")