import json
from debug import logger
CONFIG_FILE = 'config.json'

try:
    logger.info("Loading configuration from config.json")
    def load_config():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            
           
        return config
    google_config = load_config().get('google', {})
    def get_spreadsheet_id():
        
        return google_config.get('spreadsheet_id')

    def get_sheet_name():
        return google_config.get('sheet_name')

    def get_id_column():
        return google_config.get('id_column')

    def get_notion_database_id():
        return load_config().get('notion_database_id')

    def get_column_mapping():
        return load_config().get('column_mapping', {})

    def get_sync_interval():
        return load_config().get('sync_interval', 60)  

except FileNotFoundError:
    logger.error(f"Configuration file {CONFIG_FILE} not found.")
except json.JSONDecodeError:
    logger.error(f"Error decoding JSON from {CONFIG_FILE}. Please check the file format.")