import os
import requests
import time
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

def fill_january():
    console.print(f"[cyan]Deep Scanning January 2026 Movies (Top 100)...[/cyan]")
    
    total_found = 0
    all_movies = []

    # Check 5 pages (20 * 5 = 100 movies)
    for page in range(1, 6):
        console.print(f"Fetching page {page}...")
        res = tmdb_skill.execute("discover_movies", start_date="2026-01-01", end_date="2026-01-31", page=page)
        
        if not res["success"]:
            console.print(f"[red]Page {page} Failed: {res.get('error')}[/red]")
            continue
            
        page_results = res["result"].get("results", [])
        all_movies.extend(page_results)
        time.sleep(0.5) # Rate limit politeness
        
    console.print(f"[bold]Found {len(all_movies)} movies total.[/bold]")
    
    for m in all_movies:
        process_movie(m)

def process_movie(partial_data):
    tmdb_id = partial_data["id"]
    title = partial_data["title"]
    
    # 2. Check if exists in Notion
    # We query Notion for a page with "TMDB ID" == tmdb_id
    query_payload = {
        "filter": {
            "property": "TMDB ID",
            "number": {
                "equals": tmdb_id
            }
        }
    }
    
    resp = requests.post(f"https://api.notion.com/v1/databases/{DB_ID}/query", headers=HEADERS, json=query_payload)
    if resp.status_code == 200:
        results = resp.json().get("results", [])
        if results:
            console.print(f"  [dim]Skipping (Exists): {title}[/dim]")
            return
    
    # 3. Fetch Full Details if not exists
    console.print(f"\n[bold green]Adding: {title}[/bold green]")
    res_det = tmdb_skill.execute("get_movie_details", tmdb_id=tmdb_id)
    if not res_det["success"]:
        console.print(f"  [red]Failed to get details.[/red]")
        return
        
    md = res_det["result"]
    
    # 4. Create Page
    create_notion_page(md)

def create_notion_page(md):
    props = {}
    
    # Helper functions for properties
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
    def set_sel(key, val):
        if val: props[key] = {"select": {"name": val}}
    
    # Core
    set_title("Movie Title", md.get("title"))
    set_num("TMDB ID", md.get("tmdb_id"))
    set_text("IMDb ID", md.get("imdb_id"))
    
    # Release
    set_date("Theatrical Release Date", md.get("release_date"))
    if md.get("release_date"):
        set_num("Release Year", int(md.get("release_date")[:4]))

    # Stats
    set_num("Runtime", md.get("runtime"))
    set_num("Production Budget", md.get("budget"))
    set_num("Box Office Worldwide", md.get("revenue"))
    set_num("IMDb Rating", md.get("vote_average")) # Using vote_average as proxy
    
    # Crew & Cast
    set_text("Director", ", ".join(md.get("directors", [])))
    set_text("Actors", ", ".join(md.get("cast", [])[:10]))
    set_text("Production Company", ", ".join(md.get("production_companies", [])))
    
    # Content
    set_text("Notes", md.get("overview"))
    # No tagline property
    
    # Images
    set_url("Poster Image URL", md.get("poster_url"))
    set_url("Backdrop Image URL", md.get("backdrop_url"))
    set_url("Official Website", md.get("website"))
    
    # Genres (Multi-select)
    if md.get("genres"):
        props["Genre"] = {"multi_select": [{"name": g} for g in md.get("genres")]}
        
    # Certification / Status
    if md.get("certification"):
        props["MPAA Rating"] = {"select": {"name": md.get("certification")}}
    
    # Default Watch Status
    props["Watch Status"] = {"status": {"name": "Want to Watch"}}

    # Create Request
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
    fill_january()
