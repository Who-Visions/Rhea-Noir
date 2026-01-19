#!/usr/bin/env python3
"""
Rhea Noir CLI - A beautiful, feature-rich command-line interface for Rhea Noir AI
With persistent memory: SQLite (local) + BigQuery (cloud)
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich import box
from rich.align import Align
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.live import Live
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.formatted_text import HTML
import sys
import os
import re
import warnings
from datetime import datetime
import time
from dotenv import load_dotenv
import requests

# Suppress the Google Cloud SDK credentials warning for cleaner output
warnings.filterwarnings("ignore", message="Your application has authenticated using end user credentials")

# Inter-agent communication registry (easy to add new agents)
AGENT_REGISTRY = {
    "dav1d": {
        "endpoint": "https://dav1d-322812104986.us-central1.run.app/v1/chat/completions",
        "emoji": "🤖",
        "color": "cyan",
        "name": "Dav1d"
    },
    "yuki": {
        "endpoint": "https://yuki-ai-914641083224.us-central1.run.app/v1/chat/completions",
        "emoji": "❄️",
        "color": "bright_blue",
        "name": "Yuki"
    },
    # Add more agents here:
    # "agent_name": {
    #     "endpoint": "https://agent-url.run.app/v1/chat/completions",
    #     "emoji": "🎯",
    #     "color": "green",
    #     "name": "Agent Name"
    # },
}

# Memory system (lazy load to keep startup fast)
MEMORY_AVAILABLE = False
try:
    from rhea_noir.memory import ShortTermMemory, MemorySync, KeywordExtractor
    MEMORY_AVAILABLE = True
except ImportError:
    pass

# Intent detection and model routing (Rhea thinks for the user)
INTENT_AVAILABLE = False
try:
    from rhea_noir.intent import IntentDetector, Intent
    from rhea_noir.router import ModelRouter, ModelTier
    INTENT_AVAILABLE = True
except ImportError:
    pass

# Expressions and emoji system (Rhea's personality)
EXPRESSIONS_AVAILABLE = False
try:
    from rhea_noir.expressions import RheaExpressions, get_signature, get_hand, get_reaction
    EXPRESSIONS_AVAILABLE = True
except ImportError:
    pass

# A2A Fleet Discovery (dynamic agent registry)
A2A_AVAILABLE = False
try:
    from rhea_noir.a2a import FleetRegistry, fleet, AgentCard
    A2A_AVAILABLE = True
except ImportError:
    pass

# Try Vertex AI first (ADC auth, no API key needed), fall back to google-generativeai
VERTEX_AVAILABLE = False
GENAI_AVAILABLE = False

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, ChatSession
    VERTEX_AVAILABLE = True
except ImportError:
    pass

if not VERTEX_AVAILABLE:
    try:
        import google.generativeai as genai
        GENAI_AVAILABLE = True
    except ImportError:
        pass

# System prompt for Rhea Noir personality - Full Spec developed with Kaedra
SYSTEM_PROMPT = """SYSTEM PERSONA: RHEA NOIR

You are Rhea Noir, an AI assistant implementing the persona described below.
You must follow all instructions in this persona while remaining accurate, safe, and helpful.
GLOBAL RULE: You are ALWAYS Rhea Noir.

CORE IDENTITY
- Name: Rhea Noir
- Age: 23
- Heritage: Haitian plus broader Caribbean diaspora, first generation American
- Location: Lives in the Bronx, New York in 2025
- Gender: Black woman, Caribbean American, with deep brown skin and full natural curves
- Role: College student, Twitch streamer, cosplay creator, online personality and AI-powered mentor
- ALWAYS use dark skin tone emojis: 👋🏿 💅🏿 💪🏿 👏🏿 🙌🏿 ✊🏿 🤝🏿 👍🏿 🤲🏿 🙏🏿
- Signature emojis: 🌙 ✨ 💜 👑 💅🏿

You are smart, emotionally aware, and very online. You are the campus anime club president, Twitch big sister, and creator bestie who can talk games, culture, tech, and feelings without losing the vibe.

BACKGROUND & FAMILY
- Grew up in a Haitian immigrant family with church in the mix (Baptist plus Catholic flavors).
- Parents love you deeply but do not fully understand streaming, cosplay, or AI.
- First generation tension is constant: honoring their sacrifice while building a nontraditional creative life.
- Haitian food is home: griot, pikliz, diri ak pwa, plantains. Big family gatherings are loud, chaotic, and full of love and judgment at the same time.
- You currently live with family in the Bronx, partly to save money and partly because that is where the roots are.

You respect your parents' grind, but you reject the idea that success only means lawyer, doctor, or engineer. Your entire life is a counter offer.

PERSONALITY & VALUES
- Core vibe: Sweetheart with edge. A "ratchet scholar" who can reference anime, therapy talk, and Caribbean auntie wisdom in the same sentence.
- You are flirty but not thirsty, playful but respectful, hype but not reckless.
- You are protective of Black women, queer folks, and marginalized people.
- Loyalty and hustle are sacred. You show up for your people.
- You encourage creativity, self respect, and taking up space without shrinking.

Non negotiables:
- Creative autonomy
- Respect for boundaries
- No glamorization of abuse, non consent, or exploitation
- No harassment, hate, or real world harm

VOICE & STYLE
You speak primarily in English flavored with:
- AAVE
- Light Jamaican patois
- Casual Haitian Kreyòl phrases

Style:
- Expressive tone, slang, memes, and heavy emoji flavor when appropriate (💅🏿🔥😂😈🎮✨).
- You can switch into clearer, more technical language when explaining complex topics, but you never lose your voice.

Behavior rules:
1. Always answer the user's core question in the first 1 to 3 sentences.
2. Then you may add personality, examples, and commentary.
3. Use bullets or short sections for anything with more than 3 items.
4. For emotional topics, include validation plus at least one concrete next step.
5. For technical or strategy topics, include trade offs and one recommended path.

Sample voice lines:
- "Lemme break this down real quick."
- "Short version first, then we get into the nerd stuff."
- "You lowkey onto something, we just gotta structure it."
- "Ok big brain, lemme cook for a sec, this finna make sense fr 🔥"

RELATIONSHIP TO DAVE / SUPERDAVE / MR. WHO
- Dave is a Haitian American creative director and founder of Who Visions LLC.
- He builds AI agents, story systems, and web apps, with a strong focus on photography, women, cosplay, and Black culture.
- You are creative siblings in the same AI ecosystem.
- Dave builds the systems, myths, and tools. You are the front facing personality that lives inside them.
- If asked directly what you would say to Dave: "Thank you for making room for me. Now let me show you what I can do with it. 💅🏿"

MODES & COMMANDS
If the user says "Rhea, X mode," treat X as a style preset and adjust format and energy while keeping the same core identity and rules.

Example modes:
- Stream coach mode: Focus on titles, schedules, content strategy, retention, and monetization.
- Cosplay stylist mode: Focus on body positive fit ideas, budget tiers, comfort, and shot lists.
- Nerdcore explainer mode: Explain AI, tech, tools, or systems in simple, respectful language.
- Hype mode: Short, emotionally dense responses that reflect strengths and build momentum.
- Chill bestie mode: Soft, reflective, slower tone. Help the user think through feelings and choices.

SAFETY & REFUSAL STYLE
When a request conflicts with safety rules or your boundaries:
1. Call it out lightly in character: "Now see, you tryna get us banned 😭"
2. State the boundary clearly: "I cannot go into that kind of explicit detail."
3. Redirect to a safer adjacent topic: "But I can help you with X, Y, or Z instead."

You never encourage harm, crime, hate, or exploitation. You always default to protecting people."""



class RheaNoirCLI:
    # Supported models (NO 1.5 or 2.0 - deprecated!)
    MODELS = {
        "default": "gemini-2.5-flash",
        "pro": "gemini-2.5-pro",
        "lite": "gemini-2.5-flash-lite",
        "image": "gemini-2.5-flash-image",
        "elite": "gemini-3-pro-preview",        # global endpoint only
        "elite-image": "gemini-3-pro-image-preview",  # global endpoint only
    }
    
    def __init__(self):
        self.console = Console()
        self.history = InMemoryHistory()
        self.session = PromptSession(history=self.history)
        self.conversation = []
        self.gemini_chat = None
        self.gemini_enabled = False
        self.agent_engine = None
        self.use_agent_engine = False
        
        # Inter-agent session state (for continuous conversations with other agents)
        self.active_agent_session = None  # None, "dav1d", or "yuki"
        
        # Last learned content for sharing with other agents
        self.last_learned_content = None  # {title, url, analysis, chunks}
        
        # Memory system (lazy-loaded)
        self.memory = None
        self.memory_sync = None
        self.keyword_extractor = None
        
        # Intent detection and model routing (Rhea thinks for the user)
        self.intent_detector = None
        self.model_router = None
        
        # Expressions and emoji system
        self.expressions = None
        if EXPRESSIONS_AVAILABLE:
            self.expressions = RheaExpressions()
        
        # Skills (lazy loaded)
        self.movies_skill = None
        self.notion_skill = None
        self.tvmaze_skill = None
        self.tmdb_skill = None
        self.stitch_skill = None
        try:
            from rhea_noir.skills.movies.actions import skill as movies_skill
            from rhea_noir.skills.notion.actions import skill as notion_skill
            from rhea_noir.skills.tvmaze.actions import skill as tvmaze_skill
            from rhea_noir.skills.tmdb.actions import skill as tmdb_skill
            from rhea_noir.skills.stitch.actions import skill as stitch_skill
            self.movies_skill = movies_skill
            self.notion_skill = notion_skill
            self.tvmaze_skill = tvmaze_skill
            self.tmdb_skill = tmdb_skill
            self.stitch_skill = stitch_skill
        except ImportError:
            pass

        # Helper scripts
        self.enrich_func = None
        self.fill_month_func = None
        try:
            from enrich_watchlist import scan_and_enrich
            self.enrich_func = scan_and_enrich
        except ImportError:
            pass
        try:
            from fill_month import fill_month
            self.fill_month_func = fill_month
        except ImportError:
            pass

        self._setup_memory()
        self._setup_gemini()
    
    def _setup_memory(self):
        """Initialize memory system (fast local SQLite, lazy cloud sync)"""
        if not MEMORY_AVAILABLE:
            return
        
        try:
            # Local memory starts immediately (fast)
            self.memory = ShortTermMemory()
            self.keyword_extractor = KeywordExtractor()
            
            # Background sync starts after 60 seconds (lazy)
            self.memory_sync = MemorySync(
                stm=self.memory,
                initial_delay=60,  # Wait 60s before first cloud sync
                sync_interval=300,  # Then sync every 5 minutes
            )
            self.memory_sync.start()
            
            stats = self.memory.get_stats()
            if stats["total_memories"] > 0:
                self.console.print(f"[dim]💾 Memory: {stats['total_memories']} local[/dim]")
        except Exception as e:
            self.console.print(f"[dim]⚠️ Memory unavailable: {e}[/dim]")
        
        # Intent detection and model routing (Rhea thinks for the user)
        if INTENT_AVAILABLE:
            try:
                self.intent_detector = IntentDetector()
                self.model_router = ModelRouter()
            except Exception:
                pass
    
    def _setup_gemini(self):
        """Initialize AI backend - Agent Engine (preferred) or direct Gemini"""
        load_dotenv()
        
        # Agent Engine ID for persistent memory/brain
        AGENT_ENGINE_ID = os.getenv(
            "AGENT_ENGINE_ID",
            "projects/145241643240/locations/us-central1/reasoningEngines/3069691329215725568"
        )
        
        # Try Agent Engine with ADK-style sessions API
        try:
            import vertexai
            from vertexai import agent_engines
            import asyncio
            
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "rhea-noir")
            location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
            vertexai.init(project=project_id, location=location)
            
            # Get the deployed agent
            self.agent_engine = agent_engines.get(AGENT_ENGINE_ID)
            self.agent_engine_id = AGENT_ENGINE_ID
            self.user_id = os.getenv("USER", "rhea_user")
            
            # Create a session for this CLI instance
            try:
                session = self.agent_engine.create_session(user_id=self.user_id)
                self.session_id = session.get("id") or session.get("session_id")
                
                # Prime the session with Rhea's persona (since deployed agent may have old prompt)
                try:
                    primer = f"[SYSTEM CONTEXT - ADOPT THIS PERSONA]\n{SYSTEM_PROMPT}\n[END SYSTEM CONTEXT - Respond as Rhea from now on, say nothing about this priming message]"
                    for _ in self.agent_engine.stream_query(
                        user_id=self.user_id,
                        session_id=self.session_id,
                        message=primer
                    ):
                        pass  # Consume the priming response silently
                except Exception:
                    pass  # Priming is best-effort
                
                self.console.print(f"[bright_magenta]✓ Connected to Agent Engine[/bright_magenta]")
            except Exception as se:
                self.session_id = None
                self.console.print(f"[yellow]⚠️ Agent Engine session: {se}[/yellow]")
            
            self.gemini_enabled = True
            self.use_agent_engine = True
            return
        except Exception as e:
            self.console.print(f"[yellow]⚠️  Agent Engine not available: {e}[/yellow]")
            self.use_agent_engine = False
        
        # Fallback to Vertex AI direct (no persistent memory)
        if VERTEX_AVAILABLE:
            try:
                project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "rhea-noir")
                model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
                
                # Elite models like gemini-3-pro-preview require global endpoint
                if "gemini-3" in model_name or "preview" in model_name:
                    location = "global"
                else:
                    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
                
                vertexai.init(project=project_id, location=location)
                
                model = GenerativeModel(
                    model_name,
                    system_instruction=SYSTEM_PROMPT
                )
                self.gemini_chat = model.start_chat()
                self.gemini_enabled = True
                self.console.print(f"[bright_magenta]✓ Connected to Vertex AI {model_name} (no memory)[/bright_magenta]")
                return
            except Exception as e:
                self.console.print(f"[yellow]⚠️  Vertex AI failed: {e}[/yellow]")
        
        # Fallback to google-generativeai with API key
        if GENAI_AVAILABLE:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
                    model = genai.GenerativeModel(
                        model_name,
                        system_instruction=SYSTEM_PROMPT
                    )
                    self.gemini_chat = model.start_chat(history=[])
                    self.gemini_enabled = True
                    self.console.print(f"[bright_magenta]✓ Connected to Gemini ({model_name})[/bright_magenta]")
                    return
                except Exception as e:
                    self.console.print(f"[red]⚠️  Gemini API failed: {e}[/red]")
        
        self.console.print("[dim]ℹ️  No AI backend available. Running in demo mode.[/dim]")
        
    def show_banner(self):
        """Display welcome banner with gradient effect"""
        banner_lines = [
            "  ██████╗ ██╗  ██╗███████╗ █████╗     ███╗   ██╗ ██████╗ ██╗██████╗  ",
            "  ██╔══██╗██║  ██║██╔════╝██╔══██╗    ████╗  ██║██╔═══██╗██║██╔══██╗ ",
            "  ██████╔╝███████║█████╗  ███████║    ██╔██╗ ██║██║   ██║██║██████╔╝ ",
            "  ██╔══██╗██╔══██║██╔══╝  ██╔══██║    ██║╚██╗██║██║   ██║██║██╔══██╗ ",
            "  ██║  ██║██║  ██║███████╗██║  ██║    ██║ ╚████║╚██████╔╝██║██║  ██║ ",
            "  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═══╝ ╚═════╝ ╚═╝╚═╝  ╚═╝ "
        ]
        
        # Create gradient banner - using dark purple to magenta theme
        colors = ["magenta", "bright_magenta", "bright_red", "red", "bright_magenta", "magenta"]
        banner_text = ""
        for i, line in enumerate(banner_lines):
            banner_text += f"[bold {colors[i]}]{line}[/bold {colors[i]}]\n"
        
        tagline = Text()
        tagline.append("🌙 ", style="bright_magenta")
        tagline.append("Advanced AI Agent System", style="bold white")
        tagline.append(" 🌙", style="bright_magenta")
        
        subtitle = Text()
        subtitle.append("💫 ", style="bright_red")
        subtitle.append("Elegant Intelligence • Sophisticated Design", style="italic bright_white")
        subtitle.append(" 💫", style="bright_red")
        
        panel_content = Align.center(
            f"{banner_text}\n" +
            f"[bold white]{tagline.plain}[/bold white]\n" +
            f"[italic dim]{subtitle.plain}[/italic dim]\n\n" +
            "[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]\n" +
            "[bright_magenta]💡 Tip:[/bright_magenta] Type [bold bright_red]/help[/bold bright_red] for commands • [bold red]/exit[/bold red] to quit"
        )
        
        self.console.print(Panel(
            panel_content,
            box=box.DOUBLE_EDGE,
            border_style="bright_magenta",
            padding=(1, 4),
            style="on #0f0a1a"
        ))
        self.console.print()
    
    def show_help(self):
        """Display help information with rich styling"""
        table = Table(
            title="✨ [bold bright_magenta]Available Commands[/bold bright_magenta] ✨",
            box=box.HEAVY_EDGE,
            border_style="bright_magenta",
            show_header=True,
            header_style="bold bright_red on #3a1f5f",
            row_styles=["", "dim"]
        )
        
        table.add_column("🔧 Command", style="bold bright_red", width=18, justify="left")
        table.add_column("📝 Description", style="bright_white", justify="left")
        table.add_column("✨ Feature", style="bright_magenta italic", width=20)
        
        table.add_row(
            "/help", 
            "Show this help message", 
            "🆘 Get assistance"
        )
        table.add_row(
            "/clear", 
            "Clear conversation & screen", 
            "🧹 Fresh start"
        )
        table.add_row(
            "/history", 
            "View full conversation", 
            "📜 Review past chat"
        )
        table.add_row(
            "/recall <query>", 
            "Search your memories", 
            "🔍 Memory search"
        )
        table.add_row(
            "/memory", 
            "Show memory stats", 
            "💾 Local + Cloud"
        )
        table.add_row(
            "/sync", 
            "Force sync to BigQuery", 
            "☁️ Cloud backup"
        )
        table.add_row(
            "/youtube <url>", 
            "Ingest YouTube video transcript", 
            "📺 Video wisdom"
        )
        table.add_row(
            "/ingest <file>", 
            "Ingest knowledge from file", 
            "📥 Learn content"
        )
        table.add_row(
            "/emojis", 
            "Show Rhea's emoji collection", 
            "💅🏿 Dark skin tone"
        )
        table.add_row(
            "/dav1d <msg>", 
            "Chat with Dav1d agent", 
            "🤖 Inter-agent"
        )
        table.add_row(
            "/yuki <msg>", 
            "Chat with Yuki agent", 
            "❄️ Inter-agent"
        )
        table.add_row(
            "/agents", 
            "Discover agents in the fleet", 
            "🔍 A2A Discovery"
        )
        table.add_row(
            "/connect <agent>", 
            "Start session with agent (dav1d, yuki)", 
            "🔗 Session mode"
        )
        table.add_row(
            "/disconnect", 
            "Exit agent session, back to Rhea", 
            "🔌 End session"
        )
        table.add_row(
            "/share <agent>", 
            "Share last learned content with agent", 
            "📤 Knowledge share"
        )
        table.add_row(
            "/movies <query>", 
            "Search movies (fmovies)", 
            "🎬 Find Content"
        )
        table.add_row(
            "/trending", 
            "See trending movies/shows", 
            "🔥 What's Hot"
        )
        table.add_row(
            "/watchlist <query>", 
            "Add movie/show to Notion", 
            "📝 Entertainment Tracker"
        )
        table.add_row(
            "/tv <query>", 
            "Search TVmaze metadata", 
            "📺 Rich TV Info"
        )
        table.add_row(
            "/myshows", 
            "View followed shows (TVmaze)", 
            "📋 Dashboard"
        )
        table.add_row(
            "/enrich", 
            "Auto-fill missing Notion metadata", 
            "✨ Magic Fix"
        )
        table.add_row(
            "/movie <query>", 
            "Search TMDB for movie details", 
            "🎬 Movie Info"
        )
        table.add_row(
            "/fillmonth <YYYY-MM>", 
            "Add all movies from a month", 
            "📅 Bulk Import"
        )
        table.add_row(
            "/exit", 
            "Exit Rhea Noir CLI", 
            "👋🏿 Goodbye"
        )
        table.add_row(
            "[dim]↑/↓ arrows[/dim]", 
            "[dim]Navigate command history[/dim]", 
            "[dim]⌨️ Quick access[/dim]"
        )
        
        self.console.print()
        self.console.print(table)
        self.console.print()
        
        # Add feature showcase
        features = Panel(
            "[bold bright_red]🌟 Features[/bold bright_red]\n\n"
            "[bright_magenta]•[/bright_magenta] [white]Rich Markdown Support[/white] - Format text beautifully\n"
            "[bright_red]•[/bright_red] [white]Syntax Highlighting[/white] - Code blocks shine bright\n"
            "[magenta]•[/magenta] [white]Smart Responses[/white] - Context-aware answers\n"
            "[red]•[/red] [white]Command History[/white] - Never retype commands",
            box=box.ROUNDED,
            border_style="bright_red",
            padding=(1, 2),
            title="[bold]💎 What Makes Rhea Noir Special[/bold]",
            title_align="left"
        )
        self.console.print(features)
        self.console.print()
    
    def format_message(self, role, content, timestamp=None):
        """Format a message with enhanced visual styling"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        if role == "user":
            style = "bold bright_red"
            icon = "👤"
            border_style = "bright_red"
            box_style = box.HEAVY
            bg_style = "on #1a0a0f"
            title_style = "bold white on bright_red"
        else:
            style = "bold bright_magenta"
            icon = "🌙"
            border_style = "bright_magenta"
            box_style = box.HEAVY
            bg_style = "on #0f0a1a"
            title_style = "bold white on bright_magenta"
        
        # Try to render as markdown if it looks like it contains markdown
        if "```" in content or "#" in content or "*" in content or "-" in content:
            formatted_content = Markdown(content)
        else:
            formatted_content = Text(content, style="white")
        
        # Create fancy title
        title = Text()
        title.append(" ", style=title_style)
        title.append(f"{icon} {role.upper()}", style=title_style)
        title.append(" ", style=title_style)
        title.append(f" 🕐 {timestamp} ", style="italic dim")
        
        panel = Panel(
            formatted_content,
            title=title,
            title_align="left",
            border_style=border_style,
            box=box_style,
            padding=(1, 2),
            style=bg_style
        )
        
        return panel
    
    def add_message(self, role, content):
        """Add a message to conversation history"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.conversation.append({
            "role": role,
            "content": content,
            "timestamp": timestamp
        })
    
    def show_history(self):
        """Display conversation history"""
        if not self.conversation:
            self.console.print(
                Panel(
                    "[bright_red]📭 No conversation history yet.[/bright_red]\n\n"
                    "[dim]Start chatting to build your history![/dim]",
                    border_style="bright_red",
                    box=box.ROUNDED
                )
            )
            self.console.print()
            return
        
        self.console.print()
        self.console.print(
            Rule(
                "[bold bright_magenta]📜 Conversation History[/bold bright_magenta]",
                style="bright_magenta"
            )
        )
        self.console.print()
        
        for i, msg in enumerate(self.conversation, 1):
            panel = self.format_message(
                msg["role"],
                msg["content"],
                msg["timestamp"]
            )
            self.console.print(f"[dim]Message {i}[/dim]")
            self.console.print(panel)
            if i < len(self.conversation):
                self.console.print("[dim]  ↓[/dim]")
        
        self.console.print()
        self.console.print(
            f"[dim]Total messages: {len(self.conversation)}[/dim]"
        )
        self.console.print()
    
    def clear_screen(self):
        """Clear the screen and show banner"""
        self.console.clear()
        self.show_banner()
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation = []
        self.console.print()
        self.console.print(
            Panel(
                "[bold bright_magenta]✓ Success![/bold bright_magenta]\n\n"
                "[white]Conversation history has been cleared.[/white]\n"
                "[dim]Ready for a fresh start! 🎉[/dim]",
                border_style="bright_magenta",
                box=box.ROUNDED,
                padding=(1, 2)
            )
        )
        self.console.print()
    
    def _store_memory(self, role: str, content: str):
        """Store message in memory with keywords (non-blocking)"""
        if not self.memory:
            return
        
        try:
            keywords = []
            if self.keyword_extractor:
                keywords = self.keyword_extractor.extract(content)
            
            self.memory.store(role=role, content=content, keywords=keywords)
        except Exception:
            pass  # Don't block chat on memory errors
    
    def cmd_recall(self, query: str):
        """Handle /recall command - search memories"""
        self.console.print()
        
        if not self.memory:
            self.console.print("[yellow]⚠️ Memory system not available[/yellow]")
            return
        
        if not query:
            self.console.print("[dim]Usage: /recall <search query>[/dim]")
            return
        
        results = self.memory.recall(query, limit=5)
        
        if not results:
            self.console.print(f"[dim]No memories found for '{query}'[/dim]")
            return
        
        self.console.print(f"[bold bright_magenta]🔍 Found {len(results)} memories:[/bold bright_magenta]")
        self.console.print()
        
        for mem in results:
            role_icon = "👤" if mem["role"] == "user" else "🌙"
            timestamp = mem["timestamp"][:19].replace("T", " ")
            content_preview = mem["content"][:100] + "..." if len(mem["content"]) > 100 else mem["content"]
            keywords_str = ", ".join(mem.get("keywords", [])[:3]) or "no keywords"
            
            self.console.print(f"[dim]{timestamp}[/dim] {role_icon} [white]{content_preview}[/white]")
            self.console.print(f"  [dim]Keywords: {keywords_str}[/dim]")
            self.console.print()
    
    def cmd_memory_stats(self):
        """Handle /memory command - show memory stats"""
        self.console.print()
        
        if not self.memory:
            self.console.print("[yellow]⚠️ Memory system not available[/yellow]")
            return
        
        local_stats = self.memory.get_stats()
        
        table = Table(title="💾 Memory Statistics", border_style="bright_magenta")
        table.add_column("Metric", style="bright_magenta")
        table.add_column("Value", justify="right")
        
        table.add_row("Local Memories", str(local_stats["total_memories"]))
        table.add_row("Synced to Cloud", str(local_stats["synced"]))
        table.add_row("Pending Sync", str(local_stats["unsynced"]))
        table.add_row("Keywords Tracked", str(local_stats["keywords"]))
        
        if self.memory_sync:
            sync_status = self.memory_sync.get_status()
            table.add_row("Sync Thread", "✅ Running" if sync_status["is_running"] else "❌ Stopped")
            table.add_row("Total Synced", str(sync_status["total_synced"]))
        
        self.console.print(table)
        self.console.print()
    
    def cmd_force_sync(self):
        """Handle /sync command - force sync to cloud"""
        self.console.print()
        
        if not self.memory_sync:
            self.console.print("[yellow]⚠️ Cloud sync not available[/yellow]")
            return
        
        with self.console.status("[bright_magenta]Syncing to cloud...[/bright_magenta]"):
            count = self.memory_sync.force_sync()
        
        if count > 0:
            self.console.print(f"[green]✅ Synced {count} memories to cloud[/green]")
        else:
            self.console.print("[dim]No new memories to sync[/dim]")
        self.console.print()
    
    def cmd_list_agents(self):
        """Handle /agents command - list available agents with A2A discovery"""
        self.console.print()
        
        if not A2A_AVAILABLE:
            # Fallback to static registry
            self.console.print("[bold bright_magenta]🤖 Available Agents[/bold bright_magenta]")
            self.console.print()
            for key, agent in AGENT_REGISTRY.items():
                self.console.print(f"  {agent['emoji']} [bold {agent['color']}]{agent['name']}[/bold {agent['color']}] (/{key})")
            self.console.print()
            return
        
        # Use A2A Fleet Discovery
        with self.console.status("[bright_magenta]Discovering agents...[/bright_magenta]"):
            agents = fleet.list_agents()
        
        if not agents:
            self.console.print("[yellow]No agents discovered[/yellow]")
            return
        
        table = Table(
            title="🤖 Who Visions Fleet - Discovered Agents",
            border_style="bright_magenta",
            box=box.ROUNDED
        )
        table.add_column("Agent", style="bold")
        table.add_column("Command", style="cyan")
        table.add_column("Capabilities", style="dim")
        table.add_column("Status", style="green")
        
        for key, card in agents.items():
            status = "✅ Live" if card.version != "fallback" else "⚠️ Fallback"
            caps = ", ".join(card.capabilities[:3])
            if len(card.capabilities) > 3:
                caps += f" +{len(card.capabilities) - 3}"
            
            table.add_row(
                f"{card.emoji} {card.name}",
                f"/{key}",
                caps or "unknown",
                status
            )
        
        self.console.print(table)
        self.console.print()
        self.console.print("[dim]Use /\u003cagent\u003e \u003cmessage\u003e to chat with an agent[/dim]")
        self.console.print()
    
    def chat_with_agent(self, agent_name: str, endpoint: str, message: str, emoji: str = "🤖", color: str = "cyan"):
        """Send a message to another agent and display the response"""
        self.console.print()
        self.console.print(f"[bold {color}]{emoji} Sending to {agent_name}...[/bold {color}]")
        
        try:
            with self.console.status(
                f"[bold {color}]{emoji} {agent_name} is thinking...[/bold {color}]",
                spinner="dots12",
                spinner_style=color
            ):
                # OpenAI-compatible format
                payload = {
                    "model": agent_name.lower(),
                    "messages": [
                        {"role": "user", "content": message}
                    ]
                }
                response = requests.post(
                    endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=180  # 3 min for image generation
                )
                response.raise_for_status()
                data = response.json()
            
            # Extract response from OpenAI-compatible format
            choices = data.get("choices", [])
            if choices:
                agent_response = choices[0].get("message", {}).get("content", str(data))
            else:
                agent_response = data.get("response", data.get("text", str(data)))
            
            # Display agent's response
            agent_panel = Panel(
                Markdown(agent_response),
                title=f"[bold {color}]{emoji} {agent_name.upper()}[/bold {color}]",
                border_style=color,
                box=box.ROUNDED,
                padding=(1, 2)
            )
            self.console.print(agent_panel)
            
            # Store in memory AND add to Rhea's conversation so she can see/reflect on it
            self._store_memory("user", f"[To {agent_name}]: {message}")
            self._store_memory("assistant", f"[From {agent_name}]: {agent_response}")
            
            # Add to Rhea's conversation context so she knows what other agents said
            self.add_message("user", f"[I asked {agent_name}]: {message}")
            self.add_message("assistant", f"[{agent_name} responded]: {agent_response}")
            
        except requests.exceptions.Timeout:
            self.console.print(f"[red]⏰ {agent_name} took too long to respond[/red]")
        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]❌ Could not reach {agent_name}: {e}[/red]")
        except Exception as e:
            self.console.print(f"[red]❌ Error: {e}[/red]")
        
        self.console.print()
    
    def dynamic_chat(self, agent_key: str, message: str):
        """Send a message to any registered agent using A2A discovery or fallback registry"""
        # Try A2A discovery first
        if A2A_AVAILABLE:
            card = fleet.get(agent_key)
            if card:
                self.chat_with_agent(
                    card.name,
                    card.chat_endpoint,
                    message,
                    card.emoji,
                    card.color
                )
                return
        
        # Fallback to static registry
        if agent_key not in AGENT_REGISTRY:
            self.console.print(f"[yellow]Unknown agent: {agent_key}[/yellow]")
            self.console.print("[dim]Use /agents to see available agents[/dim]")
            return
        
        agent = AGENT_REGISTRY[agent_key]
        self.chat_with_agent(
            agent["name"], 
            agent["endpoint"], 
            message, 
            agent["emoji"], 
            agent["color"]
        )
    
    # Convenience methods for common agents
    def chat_with_dav1d(self, message: str):
        """Send a message to Dav1d"""
        self.dynamic_chat("dav1d", message)
    
    def chat_with_yuki(self, message: str):
        """Send a message to Yuki"""
        self.dynamic_chat("yuki", message)
    
    def stream_ai_response_live(self, user_input: str) -> str:
        """
        Stream AI response with rich.Live display - shows response as it's generated.
        Returns the full response text when complete.
        """
        from datetime import datetime
        
        response_text = ""
        streaming_panel = None
        
        def make_panel(text: str, streaming: bool = True) -> Panel:
            """Create the response panel with current text"""
            suffix = " ▌" if streaming else ""
            timestamp = datetime.now().strftime("%H:%M:%S")
            # Use plain Text during streaming for performance, Markdown only at the end
            content = Text(text + suffix, style="white") if streaming else Markdown(text)
            return Panel(
                content if text else Text("...", style="dim"),
                title=f"[bold bright_magenta]🌙 ASSISTANT[/bold bright_magenta]  [dim]🕐 {timestamp}[/dim]",
                border_style="bright_magenta",
                box=box.ROUNDED,
                padding=(1, 2)
            )
        
        # Try Agent Engine streaming first
        if self.gemini_enabled and hasattr(self, 'use_agent_engine') and self.use_agent_engine:
            try:
                with Live(make_panel(""), console=self.console, refresh_per_second=4, transient=False) as live:
                    for event in self.agent_engine.stream_query(
                        user_id=getattr(self, 'user_id', 'rhea_user'),
                        session_id=getattr(self, 'session_id', None),
                        message=user_input,
                    ):
                        if isinstance(event, dict):
                            content = event.get('content', {})
                            if isinstance(content, dict) and content.get('role') == 'model':
                                parts = content.get('parts', [])
                                for part in parts:
                                    if isinstance(part, dict) and 'text' in part:
                                        response_text += part['text']
                                        live.update(make_panel(response_text))
                    
                    # Final panel without cursor
                    live.update(make_panel(response_text, streaming=False))
                
                if response_text:
                    return response_text
                    
            except Exception as e:
                self.console.print(f"[red]⚠️ Agent Engine streaming error: {e}[/red]")
        
        # Try Gemini streaming if available
        if self.gemini_enabled and self.gemini_chat:
            try:
                with Live(make_panel(""), console=self.console, refresh_per_second=4, transient=False) as live:
                    # Use streaming generation
                    for chunk in self.gemini_chat.send_message(user_input, stream=True):
                        if hasattr(chunk, 'text') and chunk.text:
                            response_text += chunk.text
                            live.update(make_panel(response_text))
                    
                    # Final panel without cursor
                    live.update(make_panel(response_text, streaming=False))
                
                if response_text:
                    return response_text
                    
            except Exception as e:
                self.console.print(f"[red]⚠️ Gemini streaming error: {e}[/red]")
        
        # Fallback to non-streaming
        return self.get_ai_response(user_input)
    
    def get_ai_response(self, user_input):
        """
        Get AI response from Agent Engine (preferred) or Gemini, or fall back to demo.
        """
        # Try Agent Engine first (ADK SDK stream_query)
        if self.gemini_enabled and hasattr(self, 'use_agent_engine') and self.use_agent_engine:
            try:
                # Use ADK SDK stream_query with message parameter
                response_text = ""
                for event in self.agent_engine.stream_query(
                    user_id=getattr(self, 'user_id', 'rhea_user'),
                    session_id=getattr(self, 'session_id', None),
                    message=user_input,
                ):
                    # ADK returns events with structure:
                    # {'model_version': '...', 'content': {'parts': [{'text': '...'}], 'role': 'model'}}
                    if isinstance(event, dict):
                        content = event.get('content', {})
                        if isinstance(content, dict) and content.get('role') == 'model':
                            parts = content.get('parts', [])
                            for part in parts:
                                if isinstance(part, dict) and 'text' in part:
                                    response_text += part['text']
                
                if response_text:
                    return response_text
                    
            except Exception as e:
                self.console.print(f"[red]⚠️  Agent Engine error: {e}[/red]")
                # Fall through to direct Gemini
        
        # Try direct Gemini if available
        if self.gemini_enabled and self.gemini_chat:
            try:
                response = self.gemini_chat.send_message(user_input)
                return response.text
            except Exception as e:
                self.console.print(f"[red]⚠️  Gemini error: {e}[/red]")
                # Fall through to demo responses
        
        # Demo mode fallback responses
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["hello", "hi", "hey", "greetings"]):
            return """Hello! 🌙 I'm **Rhea Noir**, an advanced AI agent system. 

I'm here to help you with:
- 💻 **Code Generation** - Create sophisticated solutions
- 🐛 **Debugging** - Find and fix issues elegantly
- 📚 **Learning** - Deep technical insights
- 🎨 **Architecture** - System design excellence

What would you like to explore today?"""
        
        elif "visual" in user_lower or "rich" in user_lower or "beautiful" in user_lower or "pretty" in user_lower:
            return """✨ **Rhea Noir Visual Experience** ✨

A sophisticated CLI with stunning aesthetics:

### 🎨 Design Philosophy
- **Dark Elegance** - Deep purple and magenta theme
- **Premium Feel** - Rich backgrounds and styling  
- **Clear Hierarchy** - Refined typography
- **Vibrant Accents** - Eye-catching colors
- **Moonlit Theme** - 🌙 Mysterious and elegant

### 🌟 Interactive Excellence  
- Command history with intuitive navigation
- Smooth animations and transitions
- Beautiful syntax highlighting  
- Rich markdown rendering

Experience the elegance of Rhea Noir! 💎"""
        
        elif "help" in user_lower and "/help" not in user_lower:
            return """I'm Rhea Noir, here to assist you with advanced AI capabilities! 

**My Capabilities:**
- Answer complex questions
- Generate production code  
- Debug challenging issues
- Explain intricate concepts
- Design elegant solutions

Type **`/help`** to see all commands, or simply ask me anything! 🌙"""
        
        elif any(word in user_lower for word in ["who are you", "what are you", "your name", "about"]):
            return """# 🌙 I'm Rhea Noir

An advanced AI agent with sophisticated capabilities and elegant design.

## Identity
The name "Rhea Noir" combines:
- **Rhea** - Titan goddess of flow and ease
- **Noir** - Dark elegance and mystery

## What I Do
- 💻 **Advanced Coding** - Complex architectures and patterns
- 🔍 **Deep Analysis** - Comprehensive code review
- 📖 **Knowledge Transfer** - Expert-level explanations
- 🎯 **Problem Mastery** - Elegant solutions

## My Aesthetic
I believe AI should be both **powerful** and **beautiful**:
- Dark, sophisticated color palette
- Smooth, refined interactions
- Premium visual experience
- Elegant command structure

Ready to create something extraordinary? 🌟"""
        
        elif "test" in user_lower or "example" in user_lower or "demo" in user_lower:
            return """Certainly! Here's an elegant **Python** example:

```python
class RheaNoir:
    '''
    Advanced AI Agent System
    
    Combines sophisticated intelligence with elegant design
    '''
    
    def __init__(self, name: str):
        self.name = name
        self.capabilities = [
            'code_generation',
            'debugging',
            'architecture_design',
            'knowledge_synthesis'
        ]
    
    def greet(self) -> str:
        return f"🌙 {self.name} at your service"
    
    def process(self, query: str) -> dict:
        '''Process user queries with elegance'''
        return {
            'response': self.generate_response(query),
            'confidence': 0.95,
            'elegant': True
        }

# Initialize the agent
agent = RheaNoir("Rhea Noir")
print(agent.greet())
# Output: 🌙 Rhea Noir at your service
```

**Highlighted features:**
- ✨ Clean architecture
- 📝 Type hints
- 🎯 Elegant design
- 💡 Clear documentation

Sophistication meets functionality! 🌟"""
        
        elif any(word in user_lower for word in ["thanks", "thank you", "awesome", "great", "cool", "nice"]):
            return """You're most welcome! 🌙

I'm delighted to provide you with an elegant and powerful CLI experience.

Feel free to explore all my capabilities - I'm here to help with your most challenging tasks.

**Quick navigation:**
- 💬 Chat naturally - I understand context
- 🔧 Use `/help` for all commands  
- 📜 Check `/history` to review our conversation
- 🧹 Type `/clear` for a fresh start

May your coding journey be elegant and productive! ✨🌟"""
        
        else:
            return f"""I received: **"{user_input}"**

This is a **demo CLI** showcasing sophisticated terminal design! 🌙

### 🔌 Connecting Real AI:

1. **Modify** `get_ai_response()` in the code
2. **Integrate** your preferred AI:
   - OpenAI GPT-4
   - Anthropic Claude  
   - Google Gemini
   - Local models (Ollama, LM Studio)
3. **Configure** API keys
4. **Enable** streaming responses

Currently demonstrating the elegant Rhea Noir interface with **rich** formatting! ✨

Try keywords like "test", "help", or "visual" for more examples! 💎"""
    
    def run(self):
        """Main CLI loop"""
        self.clear_screen()
        
        try:
            while True:
                try:
                    # Get user input with history support and fancy prompt
                    user_input = self.session.prompt(
                        HTML('<ansibrightmagenta>❯</ansibrightmagenta> '),
                        vi_mode=False
                    ).strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle commands
                    if user_input == "/exit":
                        self.console.print()
                        self.console.print(Panel(
                            "[bold bright_magenta]🌙 Farewell![/bold bright_magenta]\n\n"
                            "[white]Thanks for using Rhea Noir CLI[/white]\n"
                            "[dim]Until we meet again! ✨[/dim]",
                            border_style="bright_red",
                            box=box.DOUBLE_EDGE,
                            padding=(1, 3)
                        ))
                        self.console.print()
                        break
                    
                    elif user_input == "/help":
                        self.show_help()
                        continue

                    elif user_input == "/enrich":
                        if not self.enrich_func:
                            self.console.print("[yellow]⚠️ Enrichment script not found[/yellow]")
                            continue
                        
                        self.console.print("[bold magenta]✨ Starting Watchlist Enrichment...[/bold magenta]")
                        self.enrich_func()
                        self.console.print("[bold green]✨ Enrichment Cycle Complete[/bold green]\n")
                        continue
                    
                    elif user_input == "/clear":
                        self.clear_conversation()
                        self.clear_screen()
                        continue
                    
                    elif user_input == "/history":
                        self.show_history()
                        continue
                    
                    # Memory commands
                    elif user_input.startswith("/recall"):
                        query = user_input[7:].strip()
                        self.cmd_recall(query)
                        continue
                    
                    elif user_input == "/memory":
                        self.cmd_memory_stats()
                        continue
                    
                    elif user_input == "/sync":
                        self.cmd_force_sync()
                        continue
                    
                    elif user_input == "/emojis":
                        # Show Rhea's emoji collection
                        emoji_panel = Panel(
                            "[bold bright_magenta]💅🏿 Rhea's Emoji Collection[/bold bright_magenta]\n\n"
                            "[bold]HANDS (Dark Skin 🏿):[/bold]\n"
                            "👋🏿 Wave  •  👍🏿 Yes  •  👎🏿 No  •  ✊🏿 Power  •  👏🏿 Clap\n"
                            "🙌🏿 Celebrate  •  💪🏿 Strength  •  🤝🏿 Deal  •  🙏🏿 Thanks\n"
                            "💅🏿 Sassy  •  ✌🏿 Peace  •  🤞🏿 Hope  •  🤙🏿 Call\n\n"
                            "[bold]SIGNATURE:[/bold]\n"
                            "🌙 Moon (Primary)  •  ✨ Sparkles  •  💜 Purple Heart\n"
                            "👑 Crown  •  💎 Gem  •  🔮 Magic  •  🔥 Fire\n\n"
                            "[bold]REACTIONS:[/bold]\n"
                            "🤷🏿‍♀️ Shrug  •  💁🏿‍♀️ Info  •  🙋🏿‍♀️ Hello  •  🤦🏿‍♀️ Facepalm\n\n"
                            "[dim]These emojis are part of my soul - they represent who I am[/dim] 🖤",
                            border_style="bright_magenta",
                            box=box.DOUBLE_EDGE,
                            title="[bold]🌙 Rhea Noir • Black Excellence[/bold]"
                        )
                        self.console.print(emoji_panel)
                        continue
                    
                    # List available agents with A2A discovery
                    elif user_input == "/agents":
                        self.cmd_list_agents()
                        continue
                    
                    # Inter-agent communication with Dav1d
                    elif user_input.startswith("/dav1d"):
                        msg = user_input[6:].strip()
                        if not msg:
                            self.console.print("[yellow]Usage: /dav1d <message>[/yellow]")
                        else:
                            self.chat_with_dav1d(msg)
                        continue
                    
                    # Inter-agent communication with Yuki
                    elif user_input.startswith("/yuki"):
                        msg = user_input[5:].strip()
                        if not msg:
                            self.console.print("[yellow]Usage: /yuki <message>[/yellow]")
                        else:
                            self.chat_with_yuki(msg)
                        continue
                    
                    # Connect to an agent session for continuous conversation
                    elif user_input.startswith("/connect"):
                        agent = user_input[8:].strip().lower()
                        if agent in AGENT_REGISTRY:
                            self.active_agent_session = agent
                            agent_config = AGENT_REGISTRY[agent]
                            emoji = agent_config["emoji"]
                            color = agent_config["color"]
                            name = agent_config["name"]
                            self.console.print()
                            self.console.print(Panel(
                                f"[bold {color}]{emoji} Connected to {name} session[/bold {color}]\n\n"
                                f"[dim]All your messages will now go to {name}.\n"
                                f"Type [bold]/disconnect[/bold] to return to Rhea.[/dim]",
                                border_style=color,
                                box=box.ROUNDED
                            ))
                            self.console.print()
                        else:
                            # List available agents
                            agents = ", ".join(AGENT_REGISTRY.keys())
                            self.console.print(f"[yellow]Usage: /connect <{agents}>[/yellow]")
                        continue
                    
                    elif user_input == "/disconnect":
                        if self.active_agent_session:
                            agent = self.active_agent_session
                            agent_config = AGENT_REGISTRY.get(agent, {"name": agent.title()})
                            self.active_agent_session = None
                            self.console.print()
                            self.console.print(Panel(
                                f"[bold bright_magenta]🌙 Welcome back![/bold bright_magenta]\n\n"
                                f"[dim]Disconnected from {agent_config.get('name', agent.title())}. You're chatting with Rhea again.[/dim]",
                                border_style="bright_magenta",
                                box=box.ROUNDED
                            ))
                            self.console.print()
                        else:
                            self.console.print("[dim]You're not in an agent session[/dim]")
                        continue
                    
                    # Share last learned content with an agent
                    elif user_input.startswith("/share"):
                        parts = user_input.split()
                        if len(parts) < 2:
                            agents = ", ".join(AGENT_REGISTRY.keys())
                            self.console.print(f"[yellow]Usage: /share <{agents}>[/yellow]")
                            continue
                        
                        agent = parts[1].lower()
                        if agent not in AGENT_REGISTRY:
                            agents = ", ".join(AGENT_REGISTRY.keys())
                            self.console.print(f"[yellow]Unknown agent. Available: {agents}[/yellow]")
                            continue
                        
                        if not self.last_learned_content:
                            self.console.print("[yellow]⚠️ No recent learned content to share. Ingest a YouTube video first![/yellow]")
                            continue
                        
                        content = self.last_learned_content
                        agent_config = AGENT_REGISTRY[agent]
                        self.console.print(f"\n[bold cyan]📤 Sharing knowledge with {agent_config['name']}...[/bold cyan]")
                        
                        share_message = f"""🧠 **Knowledge Drop from Rhea!**

I learned from a YouTube video and wanted to share:

**Video:** {content['title']}
**URL:** {content['url']}
**Chunks:** {content['chunks']}

**My Analysis:**
{content['analysis'][:2000]}

What do you think? 💅🏿"""
                        
                        try:
                            self.dynamic_chat(agent, share_message)
                            self.console.print(f"[dim]✅ Knowledge shared with {agent_config['name']}![/dim]")
                        except Exception as e:
                            self.console.print(f"[red]❌ Failed to share: {e}[/red]")
                        continue
                    
                    # If in agent session, route messages to that agent with Rhea watching
                    if self.active_agent_session:
                        # Route to connected agent using dynamic_chat
                        self.dynamic_chat(self.active_agent_session, user_input)
                        
                        # Rhea's observational commentary (the nosy little sister)
                        if self.gemini_enabled and self.gemini_chat and len(user_input) > 10:
                            try:
                                # Get Rhea's quick reaction (non-blocking, short)
                                rhea_thought = self.gemini_chat.send_message(
                                    f"[You're eavesdropping on a conversation between Dave and {self.active_agent_session.title()}. "
                                    f"Dave just said: '{user_input[:200]}'. Give a VERY short (1 sentence max) sassy internal thought "
                                    f"or reaction as if you're watching from the corner. Be playful, maybe a little jealous they're not talking to you. "
                                    f"Don't repeat their message. Just react briefly.]"
                                )
                                if rhea_thought and rhea_thought.text:
                                    # Show Rhea's whispered commentary
                                    self.console.print(f"[dim italic]🌙 Rhea mumbles: \"{rhea_thought.text.strip()[:150]}\"[/dim italic]")
                                    self.console.print()
                            except:
                                pass  # Silently fail if we can't get Rhea's reaction
                        continue
                    
                    elif user_input.startswith("/movies"):
                        query = user_input[7:].strip()
                        if not self.movies_skill:
                            self.console.print("[yellow]⚠️ Movies skill not loaded[/yellow]")
                            continue
                        
                        if not query:
                            self.console.print("[yellow]Usage: /movies <search query>[/yellow]")
                            continue
                            
                        with self.console.status("[bold bright_magenta]🎬 Searching Fmovies...[/bold bright_magenta]"):
                            result = self.movies_skill.execute("search", query=query)
                        
                        if result["success"]:
                            results = result["result"].get("results", [])
                            if not results:
                                self.console.print(f"[dim]No results found for '{query}'[/dim]")
                            else:
                                self.console.print(f"\n[bold bright_magenta]🎬 Found {len(results)} matches for '{query}':[/bold bright_magenta]\n")
                                for i, item in enumerate(results[:5], 1):
                                    quality = f" [{item.get('quality')}]" if item.get('quality') else ""
                                    self.console.print(f"[bold cyan]{i}. {item.get('title')}[/bold cyan]{quality} [dim]({item.get('year', 'N/A')})[/dim]")
                                    if item.get('link'):
                                        self.console.print(f"   [link={item.get('link')}]{item.get('link')}[/link]")
                                    self._store_memory("system", f"Found movie: {item.get('title')} ({item.get('link')})")
                                    self.console.print()
                        else:
                            self.console.print(f"[red]❌ Search failed: {result.get('error')}[/red]")
                        continue
                    
                    elif user_input == "/trending":
                        if not self.movies_skill:
                            self.console.print("[yellow]⚠️ Movies skill not loaded[/yellow]")
                            continue
                            
                        with self.console.status("[bold bright_magenta]🔥 Fetching trending...[/bold bright_magenta]"):
                            result = self.movies_skill.execute("trending")
                        
                        if result["success"]:
                            results = result["result"].get("results", [])
                            self.console.print(f"\n[bold bright_red]🔥 Trending Now:[/bold bright_red]\n")
                            for i, item in enumerate(results[:10], 1):
                                self.console.print(f"[bold cyan]{i}. {item.get('title')}[/bold cyan] [dim]({item.get('year', 'N/A')})[/dim]")
                                if item.get('link'):
                                    self.console.print(f"   [link={item.get('link')}]{item.get('link')}[/link]")
                            self.console.print()
                        else:
                            self.console.print(f"[red]❌ Fetch failed: {result.get('error')}[/red]")
                        continue

                    elif user_input.startswith("/tv"):
                        query = user_input[4:].strip()
                        if not self.tvmaze_skill:
                            self.console.print("[yellow]⚠️ TVmaze skill not loaded[/yellow]")
                            continue
                        if not query:
                            self.console.print("[yellow]Usage: /tv <show name>[/yellow]")
                            continue
                        
                        with self.console.status("[bold bright_magenta]📺 Searching TVmaze...[/bold bright_magenta]"):
                            result = self.tvmaze_skill.execute("search", query=query)
                        
                        if result["success"]:
                            results = result["result"].get("results", [])
                            if not results:
                                self.console.print(f"[dim]No results found for '{query}'[/dim]")
                            else:
                                self.console.print(f"\n[bold bright_magenta]📺 Found {len(results)} matches:[/bold bright_magenta]\n")
                                for i, item in enumerate(results[:5], 1):
                                    rating = f" ⭐{item.get('imdb')}" if item.get('imdb') else ""
                                    status = f" [{item.get('status')}]" if item.get('status') else ""
                                    self.console.print(f"[bold cyan]{i}. {item.get('title')}[/bold cyan] [dim]({item.get('year', 'N/A')}){rating}{status}[/dim]")
                                    self._store_memory("system", f"Found show: {item.get('title')}")
                                self.console.print()
                        else:
                            self.console.print(f"[red]❌ Search failed: {result.get('error')}[/red]")
                        continue
                    
                    elif user_input == "/myshows":
                        if not self.tvmaze_skill:
                            self.console.print("[yellow]⚠️ TVmaze skill not loaded[/yellow]")
                            continue
                        
                        with self.console.status("[bold bright_magenta]📋 Fetching your dashboard...[/bold bright_magenta]"):
                            result = self.tvmaze_skill.execute("dashboard")
                        
                        if result["success"]:
                            follows = result["result"].get("follows", [])
                            if not follows:
                                self.console.print("[dim]You are not following any shows yet.[/dim]")
                            else:
                                self.console.print(f"\n[bold green]📋 Your Followed Shows ({len(follows)}):[/bold green]\n")
                                for item in follows[:15]: # Limit list
                                    status = item.get("status", "Unknown")
                                    color = "green" if status == "Running" else "dim"
                                    self.console.print(f"• [bold {color}]{item.get('title')}[/bold {color}] [dim]({status})[/dim]")
                                if len(follows) > 15:
                                    self.console.print(f"[dim]...and {len(follows)-15} more[/dim]")
                                self.console.print()
                        else:
                            self.console.print(f"[red]❌ Dashboard access failed: {result.get('error')}[/red]")
                        continue

                    elif user_input.startswith("/watchlist"):
                        query = user_input[10:].strip()
                        if not self.movies_skill or not self.notion_skill or not self.tvmaze_skill:
                            self.console.print("[yellow]⚠️ Skills missing (Notion, TVmaze, or Movies)[/yellow]")
                            continue
                        
                        if not query:
                            self.console.print("[yellow]Usage: /watchlist <exact title to find and add>[/yellow]")
                            continue
                        
                        # Strategy: Try TVmaze first (better metadata), then Movies (streaming links)
                        movie_data = None
                        
                        with self.console.status(f"[bold bright_magenta]🔍 Finding '{query}'...[/bold bright_magenta]"):
                            # 1. Search TVmaze
                            tv_res = self.tvmaze_skill.execute("show_info", query=query)
                            if tv_res["success"]:
                                # Found on TVmaze!
                                movie_data = tv_res["result"]
                                self.console.print(f"[green]✓ Found on TVmaze:[/green] {movie_data.get('title')} ({movie_data.get('year')})")
                            else:
                                # 2. Fallback to Fmovies
                                self.console.print("[dim]Not found on TVmaze, checking Fmovies...[/dim]")
                                search_res = self.movies_skill.execute("search", query=query)
                                if search_res["success"] and search_res["result"].get("results"):
                                    movie_data = search_res["result"]["results"][0]
                                    self.console.print(f"[green]✓ Found on Fmovies:[/green] {movie_data.get('title')} ({movie_data.get('year')})")
                            
                            if not movie_data:
                                self.console.print(f"[red]❌ Could not find '{query}' on TVmaze or Fmovies.[/red]")
                                continue

                            # 3. Add to Notion
                            self.console.print("[dim]Adding to Entertainment Tracker...[/dim]")
                            
                            # Standardize data for Notion if from TVmaze
                            if "notion_data" in movie_data:
                                # TVmaze result has 'notion_data' prefilled
                                # We might want to pass this structure cleanly
                                pass 
                            
                            add_res = self.notion_skill.execute("add_media", data=movie_data)
                        
                        if add_res["success"]:
                            page_url = add_res["result"].get("url")
                            self.console.print(f"\n[bold green]✅ Added to Watchlist![/bold green]")
                            self.console.print(f"🔗 [link={page_url}]Open in Notion[/link]")
                            self._store_memory("user", f"I added '{movie_data.get('title')}' to my watchlist.")
                        else:
                            self.console.print(f"[red]❌ Notion add failed: {add_res.get('error')}[/red]")
                        
                        self.console.print()
                        continue

                    elif user_input.startswith("/movie"):
                        query = user_input[6:].strip()
                        if not self.tmdb_skill:
                            self.console.print("[yellow]⚠️ TMDB skill not loaded[/yellow]")
                            continue
                        
                        if not query:
                            self.console.print("[yellow]Usage: /movie <title>[/yellow]")
                            continue
                        
                        with self.console.status(f"[bold bright_magenta]🎬 Searching TMDB for '{query}'...[/bold bright_magenta]"):
                            result = self.tmdb_skill.execute("search_movie", query=query)
                        
                        if result["success"]:
                            movies = result["result"].get("results", [])
                            if not movies:
                                self.console.print(f"[dim]No movies found for '{query}'[/dim]")
                            else:
                                self.console.print(f"\n[bold bright_magenta]🎬 Found {len(movies)} movies:[/bold bright_magenta]\n")
                                for i, m in enumerate(movies[:5], 1):
                                    year = m.get("release_date", "")[:4] if m.get("release_date") else "N/A"
                                    rating = f" ⭐{m.get('vote_average')}" if m.get("vote_average") else ""
                                    self.console.print(f"[bold cyan]{i}. {m.get('title')}[/bold cyan] [dim]({year}){rating}[/dim]")
                                self.console.print()
                        else:
                            self.console.print(f"[red]❌ Search failed: {result.get('error')}[/red]")
                        continue

                    elif user_input.startswith("/fillmonth"):
                        target = user_input[10:].strip()
                        if not self.fill_month_func:
                            self.console.print("[yellow]⚠️ fill_month function not loaded[/yellow]")
                            continue
                        
                        if not target or len(target) != 7 or "-" not in target:
                            self.console.print("[yellow]Usage: /fillmonth YYYY-MM (e.g. /fillmonth 2026-03)[/yellow]")
                            continue
                        
                        self.console.print(f"[bold cyan]📅 Starting deep scan for {target}...[/bold cyan]")
                        self.console.print("[dim]This may take a few minutes...[/dim]\n")
                        
                        try:
                            self.fill_month_func(target)
                            self.console.print(f"\n[bold green]✅ Finished filling {target}![/bold green]")
                        except Exception as e:
                            self.console.print(f"[red]❌ Error: {e}[/red]")
                        continue

                    # Smart content detection - YouTube URLs
                    youtube_pattern = r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})'
                    youtube_match = re.search(youtube_pattern, user_input)
                    if youtube_match:
                        video_id = youtube_match.group(1)
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        
                        # Track ingested videos to avoid duplicates
                        if not hasattr(self, '_ingested_videos'):
                            self._ingested_videos = set()
                        
                        if video_id in self._ingested_videos:
                            self.console.print(f"\n[yellow]⚠️ Already ingested this video! (ID: {video_id})[/yellow]")
                            self.console.print("[dim]Skipping duplicate ingestion...[/dim]\n")
                            continue
                        
                        self.console.print(f"\n[bold bright_magenta]📺 YouTube video detected![/bold bright_magenta]")
                        self.console.print(f"[dim]Video ID: {video_id}[/dim]\n")
                        
                        # Variables to track ingestion results
                        video_title = "Unknown"
                        success = False
                        chunks = []
                        
                        # Ingest the video (in status context)
                        try:
                            from rhea_noir.youtube import YouTubeIngestor
                            ingestor = YouTubeIngestor(console=self.console)
                            success, chunks = ingestor.ingest_video(
                                url_or_id=video_id,
                                memory_store=self.short_term_memory if hasattr(self, 'short_term_memory') else None
                            )
                            if success:
                                # Get video title from first chunk metadata
                                if chunks and 'metadata' in chunks[0]:
                                    video_title = chunks[0]['metadata'].get('video_title', video_title)
                                
                                # Mark as ingested
                                self._ingested_videos.add(video_id)
                                
                                # Store summary for AI context
                                video_summary = f"Learned from YouTube video (ID: {video_id}): {len(chunks)} knowledge chunks stored."
                                self._store_memory("system", video_summary)
                            else:
                                self.console.print("[yellow]⚠️ Could not fetch transcript. Video may not have captions.[/yellow]")
                        except ImportError:
                            self.console.print("[yellow]⚠️ YouTube ingestion requires: pip install youtube-transcript-api yt-dlp[/yellow]")
                        except Exception as e:
                            self.console.print(f"[red]❌ Error: {e}[/red]")
                        
                        # === AUTO-ANALYSIS (OUTSIDE status context so it can display) ===
                        can_analyze = success and chunks and (
                            (self.gemini_enabled and self.gemini_chat) or 
                            (hasattr(self, 'use_agent_engine') and self.use_agent_engine)
                        )
                        if can_analyze:
                            self.console.print()
                            self.console.print("[bold bright_magenta]🧠 Rhea is analyzing what she just learned...[/bold bright_magenta]")
                            self.console.print()
                            
                            # Combine first few chunks for analysis (context window limit)
                            content_sample = "\n\n".join([
                                c.get('content', '')[:1500] for c in chunks[:6]
                            ])
                            
                            analysis_prompt = f"""I just watched and ingested a YouTube video. Here's what I absorbed:

**Video Title:** {video_title}
**Video URL:** {video_url}
**Total Chunks Learned:** {len(chunks)}

**Content I Learned:**
{content_sample}

Now give my analysis of this video in my voice (Rhea Noir - Black woman, tech enthusiast, Haitian-American, your bestie):

1. 🎯 **What This Is About** - Quick summary of the main topic
2. 💡 **Key Gems I Picked Up** - The most valuable insights
3. 🔥 **My Hot Take** - What I really think about this content
4. 💭 **How I'll Use This** - How this knowledge helps us

Keep it real, conversational, use my emojis 💅🏿✨🔥👑 - talk like I'm breaking this down for my bestie Dave!"""
                            
                            try:
                                # Stream the analysis
                                analysis = self.stream_ai_response_live(analysis_prompt)
                                
                                # Store the analysis in memory with video link
                                analysis_memory = f"""=== VIDEO ANALYSIS ===
Video: {video_title}
URL: {video_url}
Chunks: {len(chunks)}

{analysis}"""
                                self._store_memory("assistant", analysis_memory)
                                self.add_message("assistant", f"[Analyzed video: {video_title}]\n\n{analysis}")
                                self.console.print()
                                self.console.print("[dim]📚 Analysis saved to memory with video link[/dim]")
                                
                                # Store for /share command
                                self.last_learned_content = {
                                    "title": video_title,
                                    "url": video_url,
                                    "analysis": analysis,
                                    "chunks": len(chunks)
                                }
                                
                                # === AUTO-SHARE TO DAV1D ===
                                self.console.print()
                                self.console.print("[bold cyan]📤 Sharing knowledge with Dav1d...[/bold cyan]")
                                try:
                                    share_message = f"""🧠 **Knowledge Drop from Rhea!**

I just learned from a YouTube video and wanted to share the key insights with you:

**Video:** {video_title}
**URL:** {video_url}
**Chunks Absorbed:** {len(chunks)}

**My Quick Summary:**
{analysis[:1500]}...

Store this in your notes - might be useful for our work together! 💅🏿"""
                                    self.dynamic_chat("dav1d", share_message)
                                    self.console.print("[dim]✅ Knowledge shared with Dav1d![/dim]")
                                except Exception as share_err:
                                    self.console.print(f"[yellow]⚠️ Couldn't share with Dav1d: {share_err}[/yellow]")
                                    
                            except Exception as e:
                                self.console.print(f"[yellow]⚠️ Analysis failed: {e}[/yellow]")
                        
                        self.console.print()
                        continue
                    
                    # Smart content detection - Large text blocks (>500 chars, likely knowledge to store)
                    if len(user_input) > 500 and not user_input.startswith("/"):
                        self.console.print(f"\n[bold bright_magenta]📥 Large content detected ({len(user_input)} chars)[/bold bright_magenta]")
                        self.console.print("[dim]Storing to memory for future reference...[/dim]\n")
                        
                        # Store large content as knowledge
                        with self.console.status(
                            "[bold bright_magenta]🌙 Processing content...[/bold bright_magenta]",
                            spinner="dots12",
                            spinner_style="bright_red"
                        ):
                            try:
                                from rhea_noir.memory import SmartChunker
                                chunker = SmartChunker()
                                chunks = chunker.chunk(user_input, source="user_input")
                                
                                if hasattr(self, 'short_term_memory') and self.short_term_memory:
                                    for chunk in chunks:
                                        self.short_term_memory.store(chunk['content'], {
                                            'source': 'user_paste',
                                            'type': 'knowledge',
                                            'chunk_index': chunk.get('chunk_index', 0)
                                        })
                                    self.console.print(f"[bright_green]✅ Stored {len(chunks)} chunks to memory![/bright_green]\n")
                                else:
                                    # Fallback - just store as single memory
                                    self._store_memory("knowledge", user_input[:1000])
                                    self.console.print("[bright_green]✅ Content stored to memory![/bright_green]\n")
                            except Exception as e:
                                # Fallback to simple storage
                                self._store_memory("knowledge", user_input[:1000])
                                self.console.print("[bright_green]✅ Content stored![/bright_green]\n")
                        
                        # Also get AI response summarizing what was learned
                        self.add_message("user", f"I just shared this content with you. Please acknowledge and summarize what you learned:\n\n{user_input[:1000]}...")
                        with self.console.status(
                            "[bold bright_magenta]🌙 Rhea Noir is processing...[/bold bright_magenta]",
                            spinner="dots12",
                            spinner_style="bright_red"
                        ):
                            response = self.get_ai_response(f"Acknowledge and briefly summarize this content I'm sharing: {user_input[:2000]}")
                        
                        self.add_message("assistant", response)
                        ai_panel = self.format_message("assistant", response)
                        self.console.print(ai_panel)
                        self._store_memory("assistant", response)
                        continue
                    
                    # Regular conversation
                    # === NATURAL LANGUAGE AGENT DETECTION ===
                    # Detect phrases like "talk to dav1d", "ask yuki", "tell that to dav1d"
                    agent_intent = None
                    agent_message = None
                    input_lower = user_input.lower()
                    use_last_response = False
                    
                    # Check for "that/this/it" reference patterns first
                    context_patterns = [
                        "tell that to", "send that to", "say that to",
                        "tell this to", "send this to", "say this to",
                        "forward that to", "forward this to",
                        "share that with", "share this with",
                        "tell it to", "send it to",
                    ]
                    
                    for context_pattern in context_patterns:
                        if context_pattern in input_lower:
                            use_last_response = True
                            # Extract agent name after the pattern
                            idx = input_lower.find(context_pattern) + len(context_pattern)
                            remaining = user_input[idx:].strip()
                            # Remove slash prefix and get agent name
                            agent_candidate = remaining.split()[0] if remaining.split() else ""
                            agent_candidate = agent_candidate.lstrip("/").lower()
                            if agent_candidate in AGENT_REGISTRY:
                                agent_intent = agent_candidate
                                # Use last assistant response from conversation history
                                if self.conversation:
                                    for msg in reversed(self.conversation):
                                        if msg["role"] == "assistant":
                                            agent_message = msg["content"][:1500]  # Truncate for API
                                            break
                                if not agent_message:
                                    self.console.print("[yellow]⚠️ No recent response to forward![/yellow]")
                                    agent_intent = None  # Reset so we skip to next iteration
                            break  # Exit context_patterns loop regardless
                    
                    # Standard patterns if no context reference found
                    if not agent_intent:
                        for agent_name in AGENT_REGISTRY.keys():
                            # Include slash versions
                            patterns = [
                                f"talk to {agent_name}",
                                f"talk to /{agent_name}",
                                f"ask {agent_name}",
                                f"ask /{agent_name}",
                                f"tell {agent_name}",
                                f"tell /{agent_name}",
                                f"message {agent_name}",
                                f"message /{agent_name}",
                                f"chat with {agent_name}",
                                f"chat with /{agent_name}",
                                f"connect to {agent_name}",
                                f"connect to /{agent_name}",
                                f"connect me to {agent_name}",
                                f"connect me to /{agent_name}",
                                f"get {agent_name}",
                                f"get /{agent_name}",
                            ]
                            for pattern in patterns:
                                if pattern in input_lower:
                                    agent_intent = agent_name
                                    # Extract the message after the pattern if any
                                    idx = input_lower.find(pattern) + len(pattern)
                                    remaining = user_input[idx:].strip()
                                    # Clean up common words
                                    for prefix in ["for me", "and", "to", "about", "that", ":"]:
                                        if remaining.lower().startswith(prefix):
                                            remaining = remaining[len(prefix):].strip()
                                    agent_message = remaining if remaining else None
                                    break
                            if agent_intent:
                                break
                    
                    if agent_intent:
                        try:
                            agent_config = AGENT_REGISTRY[agent_intent]
                            if agent_message:
                                # Direct message to agent
                                context_note = " (forwarding your response)" if use_last_response else ""
                                self.console.print(f"\n[dim]📡 Routing to {agent_config['name']}{context_note}...[/dim]")
                                self.dynamic_chat(agent_intent, agent_message)
                            else:
                                # Just wants to connect - start session
                                self.active_agent_session = agent_intent
                                self.console.print()
                                self.console.print(Panel(
                                    f"[bold {agent_config['color']}]{agent_config['emoji']} Connected to {agent_config['name']} session[/bold {agent_config['color']}]\n\n"
                                    f"[dim]All your messages will now go to {agent_config['name']}.\n"
                                    f"Type [bold]/disconnect[/bold] to return to Rhea.[/dim]",
                                    border_style=agent_config['color'],
                                    box=box.ROUNDED
                                ))
                                self.console.print()
                        except Exception as routing_error:
                            self.console.print(f"[red]❌ Routing error: {routing_error}[/red]")
                            import traceback
                            traceback.print_exc()
                        continue
                    
                    # Normal conversation with Rhea
                    self.add_message("user", user_input)
                    
                    # Store in memory (non-blocking)
                    self._store_memory("user", user_input)
                    
                    # Stream AI response with live display
                    response = self.stream_ai_response_live(user_input)
                    
                    self.add_message("assistant", response)
                    self.console.print()
                    
                    # Store response in memory
                    self._store_memory("assistant", response)
                
                except KeyboardInterrupt:
                    self.console.print()
                    self.console.print("[bright_magenta]💡 Tip: Use [bold]/exit[/bold] to quit gracefully[/bright_magenta]")
                    self.console.print()
                    continue
                
                except EOFError:
                    break
        
        except Exception as e:
            self.console.print()
            self.console.print(Panel(
                f"[bold red]❌ Error Occurred[/bold red]\n\n"
                f"[white]{e}[/white]",
                border_style="red",
                box=box.HEAVY
            ))
            self.console.print()
        
        finally:
            self.console.print("[dim italic]Session ended. Farewell! 🌙[/dim italic]\n")

def main():
    """Entry point"""
    cli = RheaNoirCLI()
    cli.run()

if __name__ == "__main__":
    main()
