from sheets_client import fetch_sheet_data
from config import get_id_column,get_notion_database_id,get_column_mapping
from notion_client import create_page,update_page,find_page_by_id_property
from transformer import row_to_notion_page
from state_store import get_row_state,save_row_state,log_sync
from debug import logger

def get_id_property_name():
    id_col = get_id_column()
    mapping = get_column_mapping()
    if id_col not in mapping:
        logger.warning(f"ID column '{id_col}' is not in column_mapping in config.json.Add it to the mapping.")
    return mapping[id_col]["notion_property"]

def  run_sync():
    logger.debug("----Running sync----....")
    id_col = get_id_column()
    database_id = get_notion_database_id()
    id_property_name = get_id_property_name()
    rows_fetched = 0
    rows_updated = 0
    rows_created = 0
    errors = []
    seen_id = set()
    try:
        rows = fetch_sheet_data()
        rows_fetched = len(rows)
    except Exception as e:
        error_msg = f"Failed to fetch data from google sheet : {e}"
        logger.error(f"{error_msg}")
        log_sync(0,0,0,[error_msg])
        return 
    for row in rows:
        row_id = row.get(id_col,"").strip()
        if not row_id:
            logger.warning(f"ID not found for row. Skipping row {row}")
            continue

        if row_id in seen_id:
            logger.warning(f"Duplicate ID {row_id} found in sheet skipping second occurrence")
            errors.append(f"Duplicate ID {row_id}")
            continue
        seen_id.add(row_id)

        try:
            state_result = get_row_state(row_id)
            
            # 2. Check if it's None (New Row)
            if state_result is None:
                stored_data, notion_page_id = None, None
            else:
                # Safely unpack only if we actually got data back
                stored_data, notion_page_id = state_result
            if stored_data is None:
                logger.info(f"New row {row_id}")
                properties = row_to_notion_page(row)
                existing_page_id = find_page_by_id_property(
                    database_id,id_property_name,row_id
                )
                print(f"page_id : {existing_page_id}")
                if existing_page_id:  
                    logger.info(f"Row {row_id} already exists in Notion. Restoring state.")                    
                    save_row_state(row_id, row, existing_page_id)                
                else:                                     
                    new_page_id = create_page(database_id, properties)                    
                    save_row_state(row_id, row, new_page_id)                    
                    rows_created += 1                    
                    logger.info(f"Created Notion page for {row_id}: {new_page_id}")
            elif row != stored_data:
                logger.info(f"Updated row: {row_id}")
                properties = row_to_notion_page(row)
                update_page(notion_page_id,properties)
                save_row_state(row_id,row,notion_page_id)
                rows_updated +=1
                logger.info(f"Updated Notion page for {row_id}: {notion_page_id}")
        except Exception as e:
            error_msg = f"Error processing row '{row_id}': {e}"
            logger.error(error_msg)
            errors.append(error_msg)
    
    log_sync(rows_fetched,rows_created,rows_updated,errors if errors else None)
    logger.info(f"-----Sync Complete ----- :\n row fetched :{rows_fetched},\n rows created : {rows_created}, \n rows_updated:{rows_updated}")

