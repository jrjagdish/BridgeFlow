from config import get_column_mapping
from debug import logger

NOTION_RICH_TEXT = 2000
def row_to_notion_page(row:dict):
    mapping = get_column_mapping()
    page = {}
    missing_columns = []
    for sheet_col,config in mapping.items():
        # print(f"config: {config}")
        # print(f"column: {sheet_col}")
        if sheet_col not in row:
            missing_columns.append(sheet_col)
            logger.warning(f"Missing column '{sheet_col}' in row data. Skipping this column.")
            continue
        value = row[sheet_col].strip()
        notion_property = config['notion_property']
        notion_type = config['type']

        if not value:
            logger.info(f"Empty value for column '{sheet_col}'. Skipping this column.")
            continue

        if notion_type == 'title':
            value = value[:NOTION_RICH_TEXT]
            page[notion_property] = {
                "title": [
                    {
                        "text": {
                            "content": value
                        }
                    }
                ]
            }
        elif notion_type == 'rich_text':
            value = value[:NOTION_RICH_TEXT]
            page[notion_property] = {
                "rich_text": [
                    {
                        "text": {
                            "content": value
                        }
                    }
                ]
            }
        elif notion_type == "status":
            page[notion_property] = {
                "status": {
                    "name": value
                }
            }
        elif notion_type == "Date":
            page[notion_property] = {
                "date": {
                    "start": value
                }
            }
        # elif notion_type == "people":
        #     page[notion_property]={
        #         "people":[{
        #             "object": "user",
        #             "id":value
        #         }]
        #     }
        elif notion_type == "number":
            try:
                number_value = int(value)
                page[notion_property] = {
                    "number": number_value
                }
            except ValueError:
                logger.error(f"Invalid number format for column '{sheet_col}': '{value}'. Skipping this column.")
        else:
            logger.warning(f"Unsupported notion type '{notion_type}' for column '{sheet_col}'. Skipping this column.")
        logger.debug(f"Processed column '{sheet_col}' with value '{value}' into Notion property '{notion_property}' of type '{notion_type}'.")
    
    if missing_columns:
        logger.warning(f"Row is missing the following columns: {', '.join(missing_columns)}. These columns were skipped in the Notion page creation.")
    
    return page

