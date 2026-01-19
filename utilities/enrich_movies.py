import os
import requests
import time
from dotenv import load_dotenv
from rich.console import Console

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import TMDB skill
from rhea_noir.skills.tmdb.actions import skill as tmdb_skill

load_dotenv()
console = Console()

TOKEN = os.getenv("NOTION_TOKEN")
DB_ID = os.getenv("NOTION_MOVIES_DB_ID") # Using the NEW DB

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def scan_and_enrich():
    console.print(f"[cyan]Scanning Movies Database...[/cyan]")
    
    url = f"https://api.notion.com/v1/databases/{DB_ID}/query"
    
    # Filter: Missing TMDB ID or Missing Release Year
    payload = {
        "filter": {
            "or": [
                {"property": "TMDB ID", "number": {"is_empty": True}},
                {"property": "Release Year", "number": {"is_empty": True}},
            ]
        },
        "page_size": 25
    }
    
    resp = requests.post(url, headers=HEADERS, json=payload)
    if resp.status_code != 200:
        console.print(f"[red]Query failed: {resp.text}[/red]")
        return
        
    results = resp.json().get("results", [])
    console.print(f"[bold]Found {len(results)} movies to enrich.[/bold]")
    
    for page in results:
        enrich_movie(page)

def enrich_movie(page):
    props = page["properties"]
    page_id = page["id"]
    
    # Get Title
    title_list = props.get("Movie Title", {}).get("title", [])
    if not title_list: return
    title = title_list[0]["text"]["content"]
    
    console.print(f"\n[bold yellow]Processing: {title}[/bold yellow]")
    
    # 1. Check if we already have TMDB ID to skip search
    tmdb_id_prop = props.get("TMDB ID", {}).get("number")
    
    movie_data = None
    
    if tmdb_id_prop:
         # Direct Fetch
         console.print(f"  Fetching details for TMDB ID: {tmdb_id_prop}")
         res = tmdb_skill.execute("get_movie_details", tmdb_id=tmdb_id_prop)
         if res["success"]:
             movie_data = res["result"]
    else:
        # Search
        res = tmdb_skill.execute("search_movie", query=title)
        if res["success"] and res["result"].get("results"):
            # Best match (first result)
            hit = res["result"]["results"][0]
            console.print(f"  [green]Match Found:[/green] {hit.get('title')} ({hit.get('release_date')})")
            # Get full details
            res_det = tmdb_skill.execute("get_movie_details", tmdb_id=hit["id"])
            if res_det["success"]:
                movie_data = res_det["result"]
        else:
            console.print("  [dim]No match found on TMDB.[/dim]")
            return

    if not movie_data:
        console.print("  [red]Failed to retrieve movie details.[/red]")
        return

    # --- MAPPING ---
    update_props = {}
    
    md = movie_data
    
    # Helper for simple updates
    def set_num(key, val):
        if val is not None: update_props[key] = {"number": val}
    def set_text(key, val):
        if val: update_props[key] = {"rich_text": [{"text": {"content": str(val)[:2000]}}]}
    def set_url(key, val):
        if val: update_props[key] = {"url": val}
    def set_date(key, val):
        if val: update_props[key] = {"date": {"start": val}}
    def set_sel(key, val):
        if val: update_props[key] = {"select": {"name": val}}
        
    # Identifiers
    set_num("TMDB ID", md.get("tmdb_id"))
    set_text("IMDb ID", md.get("imdb_id"))
    
    # Release Info
    set_date("Theatrical Release Date", md.get("release_date"))
    if md.get("release_date"):
        set_num("Release Year", int(md.get("release_date")[:4]))
    
    # Financials
    set_num("Production Budget", md.get("budget"))
    set_num("Box Office Worldwide", md.get("revenue"))
    
    # Specs
    set_num("Runtime", md.get("runtime"))
    set_text("Original Language", md.get("original_language")) # Usually 'en', maybe map to full name?
    
    # People (Lists to string)
    set_text("Director", ", ".join(md.get("directors", [])))
    set_text("Producer", ", ".join(md.get("producers", [])[:5])) # Top 5
    set_text("Screenwriter", ", ".join(md.get("writers", [])))
    set_text("Cinematographer", ", ".join(md.get("cinematographers", [])))
    set_text("Composer", ", ".join(md.get("composers", [])))
    set_text("Editor", ", ".join(md.get("editors", [])))
    set_text("Actors", ", ".join(md.get("cast", [])[:10])) # Top 10 cast
    
    # Production
    set_text("Production Company", ", ".join(md.get("production_companies", [])))
    set_text("Production Country", ", ".join(md.get("production_countries", []))) # Should be multi-select?
    # Note: 'Production Country' in notion is multi_select.
    # Map country names to options? 
    # For now, let's skip multi-select complex mapping unless strictly needed or assume string is fine if mapped to text field.
    # Wait, 'Production Country' IS multi_select. We need a list of objects.
    if md.get("production_countries"):
        options = [{"name": c} for c in md.get("production_countries") if c]
        # Limit to valid options? Or just try sending. Notion API errors if option doesn't exist? 
        # Actually it creates them if authorized.
        if options:
            update_props["Production Country"] = {"multi_select": options[:10]}

    # Content
    set_text("Notes", md.get("overview")) # Synopsis in Notes?
    # set_text("Tagline", md.get("tagline")) # Removed: Property doesn't exist
    
    # Ratings
    set_num("IMDb Rating", md.get("vote_average"))
    # set_num("TMDB Popularity", md.get("popularity")) # Removed: Property doesn't exist
    
    # Genres
    if md.get("genres"):
        update_props["Genre"] = {"multi_select": [{"name": g} for g in md.get("genres")]}
        
    # Images
    set_url("Poster Image URL", md.get("poster_url"))
    set_url("Backdrop Image URL", md.get("backdrop_url"))
    set_url("Official Website", md.get("website"))
    
    # Certification
    if md.get("certification"):
        update_props["MPAA Rating"] = {"select": {"name": md.get("certification")}}

    # Send Update
    if update_props:
        update_url = f"https://api.notion.com/v1/pages/{page_id}"
        resp = requests.patch(update_url, headers=HEADERS, json={"properties": update_props})
        if resp.status_code == 200:
            console.print("  [blue]✓ Updated Movie Metadata[/blue]")
            console.print(f"    Fields: {len(update_props)} properties updated.")
        else:
            console.print(f"  [red]Update Failed: {resp.text}[/red]")
    else:
        console.print("  [dim]No data to update.[/dim]")
    
    time.sleep(0.5)

if __name__ == "__main__":
    scan_and_enrich()
