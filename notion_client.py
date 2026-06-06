import requests
from config import get_notion_database_id
from dotenv import load_dotenv
import os
import time
from debug import logger
load_dotenv()

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = get_notion_database_id()
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}

def _request(method:str,endpoint:str,payload:dict=None):
    time.sleep(0.4)
    url = f"{NOTION_API_URL}/{endpoint}"
    for attempt in range(3):
        if method == "POST":
            logger.info(f"got request from {method} , {endpoint},{url},{payload}")
            response = requests.post(url, headers=HEADERS, json=payload)
        elif method == "PATCH":
            response = requests.patch(url, headers=HEADERS, json=payload)
        elif method == "GET":
            response = requests.get(url, headers=HEADERS, json=payload)
        else:
            logger.error(f"Unsupported HTTP method: {method}")
            raise ValueError("Unsupported HTTP method")
        
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 2**attempt))
            logger.warning(f"Received 429 Too Many Requests. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            continue

        if response.status_code == 404:
            logger.error(f"Endpoint not found: {response.text}")
            raise RuntimeError(f"Endpoint not found: {endpoint}")
        
        if response.status_code == 400:
            logger.error(f"Bad request to Notion API: {response.text}")
            raise RuntimeError(f"Bad request: {response.text}")
        response.raise_for_status()
        logger.info(f"Successfully made {method} request to {endpoint}")
        return response.json()
    logger.error(f"Failed to make {method} request to {endpoint} after 3 attempts")
    raise RuntimeError(f"Failed to make {method} request to {endpoint} after 3 attempts")

def create_page(database_id:str,properties:dict):
    try:
        payload = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        result = _request("POST","pages",payload)
        logger.debug(f"Created page with properties: {properties}")
        return result.get("id")
    except Exception as e:
        logger.error(f"Error creating page in Notion: {e}")
        raise
    # return result

def update_page(page_id:str,properties:dict):
    if not page_id or str(page_id).strip() == "None":
        logger.error("Attempted to update a page, but received an invalid or 'None' page_id.")
        raise ValueError("page_id cannot be None or 'None' for a PATCH request.")
    payload = {
        "properties": properties
    }
    result = _request("PATCH",f"pages/{page_id}",payload)
    logger.debug(f"Updated page {page_id} with properties: {properties}")
    return result

def find_page_by_id_property(database_id:str,id_property_name:str,id_value:str):
    try:
        numeric_id = int(id_value.strip())
    except ValueError:
        # Fallback to float if it contains decimals, or handle gracefully
        numeric_id = float(id_value.strip())
    payload = {
        "filter": {
            "property": id_property_name,
            "number": {
                "equals": numeric_id
            }
        }
    }
    result = _request("POST",f"databases/{database_id}/query",payload)
    results = result.get("results",[])
    if results:
        logger.info(f"Found page with {id_property_name}={id_value}")
        return results[0]["id"]
    logger.info(f"No page found with {id_property_name}={id_value}")
    return None

def verify_database_connection(database_id:str):
    try:
        _request("POST",f"databases/{database_id}/query",{})
        logger.info(f"Successfully connected to Notion database {database_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Notion database {database_id}: {e}")
        return False