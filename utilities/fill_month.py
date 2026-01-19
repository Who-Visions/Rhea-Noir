import os
import requests
import time
import sys
import calendar
from dotenv import load_dotenv
from rich.console import Console

# Import TMDB skill
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rhea_noir.skills.tmdb.actions import skill as tmdb_skill

load_dotenv()
console = Console()

TOKEN = os.getenv("NOTION_TOKEN")
DB_ID = os.getenv("NOTION_MOVIES_DB_ID")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_date_range(yyyy_mm):
    try:
        parts = yyyy_mm.split("-")
        year = int(parts[0])
        month = int(parts[1])
        last_day = calendar.monthrange(year, month)[1]
        start = f"{year}-{month:02d}-01"
        end = f"{year}-{month:02d}-{last_day}"
        return start, end
    except:
        console.print("[red]Invalid format. Use YYYY-MM[/red]")
        sys.exit(1)

def fill_month(target_month):
    start_date, end_date = get_date_range(target_month)
    console.print(f"[cyan]Deep Scanning Movies for {target_month} ({start_date} to {end_date})...[/cyan]")
    
    all_movies = []

    # Check 5 pages (Top 100)
    for page in range(1, 6):
        console.print(f"Fetching page {page}...")
        res = tmdb_skill.execute("discover_movies", start_date=start_date, end_date=end_date, page=page)
        
        if not res["success"]:
            console.print(f"[red]Page {page} Failed: {res.get('error')}[/red]")
            continue
            
        page_results = res["result"].get("results", [])
        if not page_results:
            console.print("[dim]No more results.[/dim]")
            break
            
        all_movies.extend(page_results)
        time.sleep(0.5) 
        
    console.print(f"[bold]Found {len(all_movies)} movies total for {target_month}.[/bold]")
    
    for m in all_movies:
        process_movie(m)

def process_movie(partial_data):
    tmdb_id = partial_data["id"]
    title = partial_data["title"]
    
    # Check if exists
    query_payload = {
        "filter": {
            "property": "TMDB ID",
            "number": {
                "equals": tmdb_id
            }
        }
    }
    
    try:
        resp = requests.post(f"https://api.notion.com/v1/databases/{DB_ID}/query", headers=HEADERS, json=query_payload)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            if results:
                console.print(f"  [dim]Skipping (Exists): {title}[/dim]")
                return
    except Exception as e:
        console.print(f"  [red]Notion Query Error: {e}[/red]")
        return
    
    # Fetch Full Details
    console.print(f"\n[bold green]Adding: {title}[/bold green]")
    res_det = tmdb_skill.execute("get_movie_details", tmdb_id=tmdb_id)
    if not res_det["success"]:
        console.print(f"  [red]Failed to get details.[/red]")
        return
        
    md = res_det["result"]
    create_notion_page(md)

def create_notion_page(md):
    props = {}
    
    # Helpers
    def set_title(key, val):
        if val: props[key] = {"title": [{"text": {"content": str(val)}}]}
    def set_num(key, val):
        if val is not None: props[key] = {"number": val}
    def set_text(key, val):
        if val: props[key] = {"rich_text": [{"text": {"content": str(val)[:2000]}}]}
    def set_url(key, val):
        if val: props[key] = {"url": val}
    def set_date(key, val):
        if val: props[key] = {"date": {"start": val}}
    
    set_title("Movie Title", md.get("title"))
    set_num("TMDB ID", md.get("tmdb_id"))
    set_text("IMDb ID", md.get("imdb_id"))
    set_date("Theatrical Release Date", md.get("release_date"))
    if md.get("release_date"):
        set_num("Release Year", int(md.get("release_date")[:4]))
    set_num("Runtime", md.get("runtime"))
    set_num("Production Budget", md.get("budget"))
    set_num("Box Office Worldwide", md.get("revenue"))
    set_num("IMDb Rating", md.get("vote_average")) 
    set_text("Director", ", ".join(md.get("directors", [])))
    set_text("Actors", ", ".join(md.get("cast", [])[:10]))
    set_text("Production Company", ", ".join(md.get("production_companies", [])))
    set_text("Notes", md.get("overview"))
    set_url("Poster Image URL", md.get("poster_url"))
    set_url("Backdrop Image URL", md.get("backdrop_url"))
    set_url("Official Website", md.get("website"))
    
    if md.get("genres"):
        props["Genre"] = {"multi_select": [{"name": g} for g in md.get("genres")]}
    if md.get("certification"):
        props["MPAA Rating"] = {"select": {"name": md.get("certification")}}
    
    props["Watch Status"] = {"status": {"name": "Want to Watch"}}

    body = {
        "parent": {"database_id": DB_ID},
        "properties": props
    }
    
    resp = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=body)
    if resp.status_code == 200:
        console.print("  [blue]✓ Created Page[/blue]")
    else:
        console.print(f"  [red]Creation Failed: {resp.text}[/red]")
    
    time.sleep(0.5)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("Usage: python fill_month.py YYYY-MM")
    else:
        fill_month(sys.argv[1])
