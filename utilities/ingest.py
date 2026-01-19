#!/usr/bin/env python3
"""
🌙 RHEA NOIR Knowledge Ingestion CLI
Premium Rich-based interface with spinners, progress bars, and watchdog monitoring.
"""
import sys
import re
import os
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict

# Add project root to path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name == "scripts" else SCRIPT_DIR
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout
    from rich.text import Text
    from rich import box
except ImportError:
    print("Installing rich library...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout
    from rich.text import Text
    from rich import box

console = Console()

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 BANNER & STYLING
# ═══════════════════════════════════════════════════════════════════════════════

BANNER = """
[bold magenta]
██████╗ ██╗  ██╗███████╗ █████╗     ███╗   ██╗ ██████╗ ██╗██████╗ 
██╔══██╗██║  ██║██╔════╝██╔══██╗    ████╗  ██║██╔═══██╗██║██╔══██╗
██████╔╝███████║█████╗  ███████║    ██╔██╗ ██║██║   ██║██║██████╔╝
██╔══██╗██╔══██║██╔══╝  ██╔══██║    ██║╚██╗██║██║   ██║██║██╔══██╗
██║  ██║██║  ██║███████╗██║  ██║    ██║ ╚████║╚██████╔╝██║██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═══╝ ╚═════╝ ╚═╝╚═╝  ╚═╝
[/bold magenta]
[dim]Knowledge Ingestion System • BigQuery + SQLite • Memory Engine[/dim]
"""

def print_banner():
    console.print(BANNER)
    console.print()

# ═══════════════════════════════════════════════════════════════════════════════
# 📦 CHUNK PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

def chunk_markdown(content: str, source_file: str) -> List[Dict]:
    """Split markdown by H2 headers for chunking."""
    parts = re.split(r'(^## .+$)', content, flags=re.MULTILINE)
    
    chunks = []
    current_chunk = ''
    current_header = 'Overview'
    
    for part in parts:
        if part.startswith('## '):
            if current_chunk.strip():
                chunks.append({
                    'content': current_chunk.strip(),
                    'header': current_header,
                    'source': Path(source_file).name
                })
            current_header = part.replace('## ', '').strip()
            current_chunk = part + '\n'
        else:
            current_chunk += part
    
    if current_chunk.strip():
        chunks.append({
            'content': current_chunk.strip(),
            'header': current_header,
            'source': Path(source_file).name
        })
    
    return chunks

def chunk_text(content: str, source_name: str, chunk_size: int = 1000) -> List[Dict]:
    """Split plain text into chunks by size."""
    words = content.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        if current_size + len(word) > chunk_size and current_chunk:
            chunks.append({
                'content': ' '.join(current_chunk),
                'header': f'Chunk {len(chunks) + 1}',
                'source': source_name
            })
            current_chunk = [word]
            current_size = len(word)
        else:
            current_chunk.append(word)
            current_size += len(word) + 1
    
    if current_chunk:
        chunks.append({
            'content': ' '.join(current_chunk),
            'header': f'Chunk {len(chunks) + 1}',
            'source': source_name
        })
    
    return chunks

# ═══════════════════════════════════════════════════════════════════════════════
# 🔄 INGESTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class RheaIngestionEngine:
    """Knowledge ingestion engine for Rhea Noir."""
    
    def __init__(self, project_id: str = 'rhea-noir', location: str = 'us-central1'):
        self.project_id = project_id
        self.location = location
        self.short_term = None
        self.long_term = None
        self.stats = {
            'files_processed': 0,
            'chunks_ingested': 0,
            'chunks_failed': 0,
            'retries': 0,
            'start_time': None,
            'errors': []
        }
    
    def connect(self) -> bool:
        """Connect to Rhea's memory stores."""
        try:
            # Try to import Rhea's memory modules
            from rhea_noir.memory import ShortTermMemory, LongTermMemory
            
            self.short_term = ShortTermMemory()
            self.long_term = LongTermMemory(self.project_id)
            
            return True
        except ImportError as e:
            console.print(f"[yellow]⚠️ Memory modules not available: {e}[/yellow]")
            console.print("[dim]Using standalone mode (local storage only)[/dim]")
            
            # Fallback to simple SQLite
            try:
                import sqlite3
                self.db_path = PROJECT_ROOT / "rhea_knowledge.db"
                self.conn = sqlite3.connect(str(self.db_path))
                self._init_db()
                return True
            except Exception as db_err:
                console.print(f"[red]❌ Database error: {db_err}[/red]")
                return False
        except Exception as e:
            console.print(f"[red]❌ Connection failed: {e}[/red]")
            return False
    
    def _init_db(self):
        """Initialize standalone SQLite database."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source TEXT,
                section TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def ingest_chunk(self, chunk: Dict, retry_count: int = 3) -> bool:
        """Ingest a single chunk with retry logic."""
        metadata = {
            'source': chunk['source'],
            'section': chunk['header'],
            'type': 'knowledge',
            'ingested_at': datetime.now().isoformat()
        }
        content_with_context = f"Source: {chunk['source']}\nSection: {chunk['header']}\n\n{chunk['content']}"
        
        for attempt in range(retry_count):
            try:
                if self.short_term:
                    self.short_term.store(content_with_context, metadata)
                elif hasattr(self, 'conn'):
                    import json
                    cursor = self.conn.cursor()
                    cursor.execute(
                        "INSERT INTO knowledge (content, source, section, metadata) VALUES (?, ?, ?, ?)",
                        (content_with_context, chunk['source'], chunk['header'], json.dumps(metadata))
                    )
                    self.conn.commit()
                return True
            except Exception as e:
                error_str = str(e)
                if 'RESOURCE_EXHAUSTED' in error_str or '429' in error_str:
                    self.stats['retries'] += 1
                    wait_time = 30 * (2 ** attempt)
                    time.sleep(wait_time)
                else:
                    self.stats['errors'].append(str(e)[:100])
                    return False
        return False
    
    def ingest_file(self, file_path: Path, progress: Progress = None, task_id = None) -> int:
        """Ingest a single knowledge file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            console.print(f"[red]❌ Failed to read {file_path.name}: {e}[/red]")
            return 0
        
        # Choose chunking method based on file type
        if file_path.suffix == '.md':
            chunks = chunk_markdown(content, str(file_path))
        else:
            chunks = chunk_text(content, file_path.name)
        
        ingested = 0
        
        for i, chunk in enumerate(chunks):
            if progress and task_id:
                progress.update(task_id, description=f"[cyan]{file_path.name}[/cyan] • {chunk['header'][:30]}...")
            
            if self.ingest_chunk(chunk):
                ingested += 1
                self.stats['chunks_ingested'] += 1
            else:
                self.stats['chunks_failed'] += 1
            
            if progress and task_id:
                progress.advance(task_id)
            
            time.sleep(0.5)  # Rate limiting
        
        self.stats['files_processed'] += 1
        return ingested
    
    def ingest_directory(self, directory: Path, pattern: str = "*.md"):
        """Ingest all matching files in a directory."""
        files = list(directory.glob(pattern))
        
        if not files:
            console.print(f"[yellow]⚠️  No files matching '{pattern}' found in {directory}[/yellow]")
            return
        
        # Calculate total chunks first
        total_chunks = 0
        file_chunks = {}
        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    content = fp.read()
                if f.suffix == '.md':
                    chunks = chunk_markdown(content, str(f))
                else:
                    chunks = chunk_text(content, f.name)
                file_chunks[f] = chunks
                total_chunks += len(chunks)
            except:
                pass
        
        console.print(f"\n[bold green]📂 Found {len(files)} files with {total_chunks} total chunks[/bold green]\n")
        
        self.stats['start_time'] = datetime.now()
        
        with Progress(
            SpinnerColumn(spinner_name="dots12"),
            TextColumn("[bold magenta]{task.description}"),
            BarColumn(bar_width=40, complete_style="magenta", finished_style="bright_magenta"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            expand=True
        ) as progress:
            
            main_task = progress.add_task("[bold]Ingesting knowledge...", total=total_chunks)
            
            for file_path, chunks in file_chunks.items():
                for i, chunk in enumerate(chunks):
                    progress.update(main_task, description=f"[cyan]{file_path.name}[/cyan] • {chunk['header'][:25]}...")
                    
                    if self.ingest_chunk(chunk):
                        self.stats['chunks_ingested'] += 1
                    else:
                        self.stats['chunks_failed'] += 1
                    
                    progress.advance(main_task)
                    time.sleep(0.5)
                
                self.stats['files_processed'] += 1
        
        self.print_summary()
    
    def ingest_single(self, file_path: Path):
        """Ingest a single file with progress."""
        if not file_path.exists():
            console.print(f"[red]❌ File not found: {file_path}[/red]")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            console.print(f"[red]❌ Failed to read file: {e}[/red]")
            return
        
        if file_path.suffix == '.md':
            chunks = chunk_markdown(content, str(file_path))
        else:
            chunks = chunk_text(content, file_path.name)
        
        console.print(f"\n[bold magenta]📄 {file_path.name}[/bold magenta] • {len(chunks)} chunks\n")
        
        self.stats['start_time'] = datetime.now()
        
        with Progress(
            SpinnerColumn(spinner_name="dots12"),
            TextColumn("[bold magenta]{task.description}"),
            BarColumn(bar_width=50, complete_style="magenta", finished_style="bright_magenta"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            expand=True
        ) as progress:
            
            task = progress.add_task(f"[cyan]{file_path.name}[/cyan]", total=len(chunks))
            
            for chunk in chunks:
                progress.update(task, description=f"[cyan]{chunk['header'][:40]}...[/cyan]")
                
                if self.ingest_chunk(chunk):
                    self.stats['chunks_ingested'] += 1
                else:
                    self.stats['chunks_failed'] += 1
                
                progress.advance(task)
                time.sleep(0.5)
        
        self.stats['files_processed'] = 1
        self.print_summary()
    
    def ingest_youtube(self, url_or_id: str, source: str = "YouTube", dry_run: bool = False):
        """Ingest a YouTube video transcript."""
        try:
            from rhea_noir.youtube import YouTubeIngestor
            
            ingestor = YouTubeIngestor(console=console)
            
            self.stats['start_time'] = datetime.now()
            
            success, chunks = ingestor.ingest_video(
                url_or_id=url_or_id,
                source=source,
                memory_store=self.short_term,
                dry_run=dry_run
            )
            
            if success:
                self.stats['chunks_ingested'] = len(chunks)
                self.stats['files_processed'] = 1
                self.print_summary()
            
        except ImportError:
            console.print("[red]❌ YouTube module not available[/red]")
            console.print("[dim]Run: pip install youtube-transcript-api pytube[/dim]")
    
    def print_summary(self):
        """Print ingestion summary."""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds() if self.stats['start_time'] else 0
        
        table = Table(title="🌙 Rhea Noir Ingestion Summary", box=box.ROUNDED, border_style="magenta")
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right", style="bright_magenta")
        
        table.add_row("Files Processed", str(self.stats['files_processed']))
        table.add_row("Chunks Ingested", f"[green]{self.stats['chunks_ingested']}[/green]")
        table.add_row("Chunks Failed", f"[red]{self.stats['chunks_failed']}[/red]" if self.stats['chunks_failed'] else "0")
        table.add_row("Retries", str(self.stats['retries']))
        table.add_row("Duration", f"{elapsed:.1f}s")
        table.add_row("Rate", f"{self.stats['chunks_ingested'] / max(elapsed, 1) * 60:.1f} chunks/min")
        
        console.print()
        console.print(table)
        
        if self.stats['errors']:
            console.print("\n[red]Errors:[/red]")
            for err in self.stats['errors'][:5]:
                console.print(f"  [dim]• {err}[/dim]")

# ═══════════════════════════════════════════════════════════════════════════════
# 👁️ WATCHDOG MODE
# ═══════════════════════════════════════════════════════════════════════════════

def watchdog_mode(directory: Path, engine: RheaIngestionEngine):
    """Watch directory for new files and auto-ingest."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        console.print("[yellow]Installing watchdog...[/yellow]")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog"])
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    
    class KnowledgeHandler(FileSystemEventHandler):
        def on_created(self, event):
            if event.is_directory:
                return
            if event.src_path.endswith(('.md', '.txt')):
                console.print(f"\n[bold magenta]📥 New file detected: {Path(event.src_path).name}[/bold magenta]")
                time.sleep(1)
                engine.ingest_single(Path(event.src_path))
    
    observer = Observer()
    observer.schedule(KnowledgeHandler(), str(directory), recursive=False)
    observer.start()
    
    console.print(Panel(
        f"[bold magenta]👁️  WATCHDOG MODE ACTIVE[/bold magenta]\n\n"
        f"Monitoring: [yellow]{directory}[/yellow]\n"
        f"Patterns: [dim]*.md, *.txt[/dim]\n\n"
        f"[dim]Press Ctrl+C to stop[/dim]",
        border_style="magenta",
        box=box.DOUBLE
    ))
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        console.print("\n[yellow]Watchdog stopped.[/yellow]")
    observer.join()

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="🌙 Rhea Noir Knowledge Ingestion CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('path', nargs='?', help='File, directory, or YouTube URL to ingest')
    parser.add_argument('--watch', '-w', action='store_true', help='Watch directory for new files')
    parser.add_argument('--all', '-a', action='store_true', help='Ingest all .md files in knowledge directory')
    parser.add_argument('--youtube', '-y', action='store_true', help='Treat path as YouTube URL')
    parser.add_argument('--source', '-s', default='Knowledge', help='Source name for metadata')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Preview without saving')
    parser.add_argument('--project', default='rhea-noir', help='GCP Project ID')
    parser.add_argument('--location', default='us-central1', help='Location')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Initialize engine
    engine = RheaIngestionEngine(args.project, args.location)
    
    with console.status("[bold magenta]Connecting to memory stores...", spinner="dots12"):
        if not engine.connect():
            sys.exit(1)
    
    console.print("[green]✅ Connected to Rhea Noir memory stores[/green]\n")
    
    # Determine mode
    knowledge_dir = PROJECT_ROOT / 'resources' / 'knowledge'
    
    if args.youtube and args.path:
        engine.ingest_youtube(args.path, source=args.source, dry_run=args.dry_run)
    elif args.watch:
        target = Path(args.path) if args.path else knowledge_dir
        watchdog_mode(target, engine)
    elif args.all:
        if knowledge_dir.exists():
            engine.ingest_directory(knowledge_dir)
        else:
            console.print(f"[yellow]⚠️ Knowledge directory not found: {knowledge_dir}[/yellow]")
    elif args.path:
        target = Path(args.path)
        if target.is_dir():
            engine.ingest_directory(target)
        else:
            engine.ingest_single(target)
    else:
        console.print(Panel(
            "[bold]Usage Examples:[/bold]\n\n"
            "  [cyan]python ingest.py document.md[/cyan]          Ingest a file\n"
            "  [cyan]python ingest.py ./knowledge/[/cyan]         Ingest a directory\n"
            "  [cyan]python ingest.py -y 'youtube.com/...'[/cyan] Ingest YouTube video\n"
            "  [cyan]python ingest.py --watch ./knowledge/[/cyan] Watch for new files\n"
            "  [cyan]python ingest.py --all[/cyan]                Ingest all knowledge\n",
            title="🌙 Rhea Noir Knowledge Ingestion",
            border_style="magenta"
        ))

if __name__ == "__main__":
    main()
