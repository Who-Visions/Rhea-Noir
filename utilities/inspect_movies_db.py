import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("NOTION_TOKEN")
DB_ID = os.getenv("NOTION_MOVIES_DB_ID")

if not TOKEN or not DB_ID:
    print("Error: NOTION_TOKEN or NOTION_MOVIES_DB_ID not set")
    exit(1)

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def inspect():
    url = f"https://api.notion.com/v1/databases/{DB_ID}"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Error: {resp.text}")
        return

    props = resp.json().get("properties", {})
    clean = {}
    
    for name, prop in props.items():
        ptype = prop.get("type")
        info = {"type": ptype}
        if ptype in ["select", "multi_select"]:
            opts = prop.get(ptype, {}).get("options", [])
            info["options"] = [o["name"] for o in opts]
        clean[name] = info
        
    print(json.dumps(clean, indent=2))

if __name__ == "__main__":
    inspect()
