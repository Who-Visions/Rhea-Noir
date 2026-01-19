
"""
Enrich Watchlist Script
Scans Notion Entertainment Tracker for missing metadata and fills it from TVmaze.
"""

import os
import requests
import time
from dotenv import load_dotenv
from rich.console import Console

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import skills manually or use logic directly?
# Let's use logic directly to avoid dependency hell with notion-client
from rhea_noir.skills.tvmaze.actions import skill as tvmaze_skill

load_dotenv()
console = Console()

TOKEN = os.getenv("NOTION_TOKEN")
DB_ID = os.getenv("NOTION_DB_ID")

if not TOKEN or not DB_ID:
    console.print("[red]Missing Token or DB ID[/red]")
    exit()

# Format UUID
if len(DB_ID) == 32:
    DB_ID = f"{DB_ID[:8]}-{DB_ID[8:12]}-{DB_ID[12:16]}-{DB_ID[16:20]}-{DB_ID[20:]}"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def scan_and_enrich():
    console.print(f"[cyan]Scanning Database for Date/Time Audit...[/cyan]")
    
    url = f"https://api.notion.com/v1/databases/{DB_ID}/query"
    
    # No filter - we want to audit everything
    payload = {
        "page_size": 50 
    }
    
    resp = requests.post(url, headers=HEADERS, json=payload)
    if resp.status_code != 200:
        console.print(f"[red]Query failed: {resp.text}[/red]")
        return
        
    results = resp.json().get("results", [])
    console.print(f"[bold]Found {len(results)} items to audit.[/bold]")
    
    for page in results:
        audit_page(page)

def audit_page(page):
    props = page["properties"]
    page_id = page["id"]
    
    # Get Title
    title_list = props.get("Title", {}).get("title", [])
    if not title_list: return
    title = title_list[0]["text"]["content"]
    
    console.print(f"\n[bold yellow]Auditing: {title}[/bold yellow]")
    
    # Search TVmaze
    search_res = tvmaze_skill.execute("show_info", query=title)
    
    if not search_res["success"]:
        search_res = tvmaze_skill.execute("search", query=title)
        if search_res["success"] and search_res["result"].get("results"):
            data = search_res["result"]["results"][0]
        else:
            console.print("  [dim]No match found.[/dim]")
            return
    else:
        data = search_res["result"]

    n_data = data.get("notion_data", {})
    update_props = {}

    # --- VALIDATION LOGIC ---

    # 1. Release Date
    api_date = n_data.get("Release Date")
    current_date = props.get("Release Date", {}).get("date", {})
    current_date_val = current_date.get("start") if current_date else None
    
    if api_date and api_date != current_date_val:
        update_props["Release Date"] = {"date": {"start": api_date}}
        console.print(f"  [cyan]Fixing Date:[/cyan] {current_date_val} -> {api_date}")

    # 2. Air Time
    api_air = n_data.get("Air Time")
    current_air_list = props.get("Air Time", {}).get("rich_text", [])
    current_air_val = current_air_list[0]["text"]["content"] if current_air_list else ""
    
    # Clean up string comparison (strip)
    if api_air and api_air.strip() != current_air_val.strip():
        update_props["Air Time"] = {"rich_text": [{"text": {"content": api_air}}]}
        console.print(f"  [cyan]Fixing Air Time:[/cyan] '{current_air_val}' -> '{api_air}'")

    # Apply Update
    if update_props:
        update_url = f"https://api.notion.com/v1/pages/{page_id}"
        resp = requests.patch(update_url, headers=HEADERS, json={"properties": update_props})
        if resp.status_code == 200:
            console.print("  [blue]✓ Corrected Data[/blue]")
        else:
            console.print(f"  [red]Update Failed: {resp.text}[/red]")
    else:
        console.print("  [green]✓ Data Verified (Correct)[/green]")
    
    time.sleep(0.5)

if __name__ == "__main__":
    scan_and_enrich()
