import requests
import time
from debug import logger
from oauth import get_valid_access_token
from config import get_spreadsheet_id, get_sheet_name

sheets_api_url = "https://sheets.googleapis.com/v4/spreadsheets"

def fetch_sheet_data():
    access_token = get_valid_access_token()
    spreadsheet_id = get_spreadsheet_id()
    sheet_name = get_sheet_name()

    url = f"{sheets_api_url}/{spreadsheet_id}/values/{sheet_name}"

    for attempt in range(3):
        try:
            response = requests.get(url,headers={"Authorization": f"Bearer {access_token}"})
            if response.status_code == 429:
                logger.warning("Received 429 Too Many Requests. Retrying after backoff.")
                time.sleep(2 ** attempt)
                continue

            if response.status_code == 401:
                logger.info("Access token might be expired. Refreshing token and retrying.")
                access_token = get_valid_access_token()
                continue
            response.raise_for_status()
            logger.info("Successfully fetched sheet data.")
            break
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred while fetching sheet data: {http_err}")
            
        except Exception as e:
            logger.error(f"Network error while fetching sheet data: {e}")
        
    data = response.json()
    logger.debug(f"Fetched sheet data: {data}")
    values = data.get('values', [])
    if not values:
        logger.warning("No data found in the sheet.")
        return []
    headers = values[0]
    rows = values[1:]
    sheet_data = [dict(zip(headers, row)) for row in rows if len(row)!=0 and any(cell.strip() for cell in row)]

    return sheet_data
