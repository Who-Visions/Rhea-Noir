import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")

if not NOTION_TOKEN or not NOTION_DB_ID:
    print("Error: NOTION_TOKEN or NOTION_DB_ID not found in .env")
    exit(1)

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_db_schema():
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        properties = data.get("properties", {})
        
        # Simplified output
        clean_schema = {}
        for name, prop in properties.items():
            p_type = prop.get("type")
            info = {"type": p_type}
            
            if p_type in ["select", "multi_select"]:
                opts = prop.get(p_type, {}).get("options", [])
                info["options"] = [o["name"] for o in opts]
            elif p_type == "formula":
                info["expression"] = prop.get("formula", {}).get("expression")
            elif p_type == "relation":
                info["related_db"] = prop.get("relation", {}).get("database_id")
                
            clean_schema[name] = info

        print(json.dumps(clean_schema, indent=2))
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching database: {e}")

if __name__ == "__main__":
    get_db_schema()
