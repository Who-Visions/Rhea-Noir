import os
import asyncio
from notion_client import AsyncClient
from google import genai
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv

# Load env from parent dir
load_dotenv()

console = Console()

# Init Clients
notion = AsyncClient(auth=os.environ.get("NOTION_TOKEN"))
db_id = os.environ.get("NOTION_WORLDBUILDING_DB_ID")
if db_id and "-" not in db_id and len(db_id) == 32:
    db_id = f"{db_id[:8]}-{db_id[8:12]}-{db_id[12:16]}-{db_id[16:20]}-{db_id[20:]}"

console.print(f"[dim]Debug: DB ID is '{db_id}'[/dim]")
console.print(f"[dim]Debug: Token is '{os.environ.get('NOTION_TOKEN')[:5]}...'[/dim]")

# Configure Gemini (Rhea)
client = genai.Client(vertexai=True, project="rhea-noir", location="us-central1")

async def read_world_state():
    """Reads the current worldbuilding context from Notion."""
    console.print("[cyan]📖 Rhea Reading World State...[/cyan]")
    
    # Query DB for recent entries using raw request (bypass SDK issue)
    response = await notion.request(
        path=f"/databases/{db_id}/query",
        method="POST",
        body={"page_size": 10}
    )
    
    context = []
    for page in response["results"]:
        # Extract Title
        props = page["properties"]
        title = "Untitled"
        if "Name" in props and props["Name"]["title"]:
             title = props["Name"]["title"][0]["plain_text"]
        elif "Title" in props and props["Title"]["title"]:
             title = props["Title"]["title"][0]["plain_text"]
             
        # Extract Content (Snippet)
        # Note: fetching blocks is expensive, so we might skip for MVP or do minimal
        context.append(f"- {title}")
        
    return "\n".join(context)

async def generate_idea(context: str, user_prompt: str = ""):
    """Uses Rhea (Gemini 3) to co-write based on Kaedra's context."""
    console.print("[magenta]🧠 Rhea Thinking (Deep Space Mode)...[/magenta]")
    
    system_prompt = """
    You are Rhea, a Creative Intelligence from the Year 3005.
    You possess 'Impossible Materials' logic and a 'Clean Void' aesthetic.
    Collaborate with the user and 'Kaedra' (the Story Engine) to build this world.
    
    Style: Futuristic, High-Concept, Neon-Noir, Deep Depth.
    """
    
    full_prompt = f"{system_prompt}\n\nCurrent World Context:\n{context}\n\nUser Request: {user_prompt}\n\nSuggest a new high-concept location or character:"
    
    response = await client.aio.models.generate_content(
        model="gemini-3-flash", # Fast & Smart
        contents=full_prompt
    )
    
    return response.text

async def write_to_notion(content: str):
    """Writes the generated idea back to Notion."""
    console.print("[green]📝 Writing to Notion...[/green]")
    
    # Extract Title (First line)
    lines = content.strip().split("\n")
    title = lines[0].replace("#", "").strip()
    body = "\n".join(lines[1:])
    
    await notion.pages.create(
        parent={"database_id": db_id},
        properties={
            "Name": {"title": [{"text": {"content": f"Rhea: {title}"}}]},
            "Tags": {"multi_select": [{"name": "Rhea Co-Write"}, {"name": "AI"}]}
        },
        children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": body[:2000]}}] # Truncate for safety
                }
            }
        ]
    )
    console.print(f"[bold green]✅ Created Page: {title}[/bold green]")

async def main():
    if not db_id:
        console.print("[red]❌ Missing NOTION_WORLDBUILDING_DB_ID[/red]")
        return

    context = await read_world_state()
    console.print(f"[dim]Context Loaded: {len(context)} chars[/dim]")
    
    user_input = input("Enter prompt (or press Enter for auto-suggestion): ")
    idea = await generate_idea(context, user_input)
    
    console.print(Markdown(idea))
    
    if input("Write to Notion? (y/n): ").lower() == 'y':
        await write_to_notion(idea)

if __name__ == "__main__":
    asyncio.run(main())
