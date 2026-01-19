#!/usr/bin/env python3
"""
🎤 Rhea Noir - Live Voice Chat 🎧
Speak into Chat Mix, hear Rhea respond on her channel!

Powered by:
- Faster Whisper (local transcription)
- Gemini 3 Smart Routing (VertexAI Global Endpoint)
- Gemini 2.5 Flash TTS (Rhea's voice)
"""

import os
import sys
import time
import warnings
import threading
import queue
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from rich.console import Console
from rich.panel import Panel

# Suppress SDK warning about 'minimal' thinking level (it works on API)
warnings.filterwarnings("ignore", message=".*minimal is not a valid ThinkingLevel.*")

console = Console()

# Add project to path
# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rhea_noir.skills import get_skill
from rhea_noir.gemini3_router import get_router
from rhea_noir.memory.short_term import ShortTermMemory
from rhea_noir.memory.long_term import BigQueryMemory

def get_system_prompt(short_context: str = "", long_context: str = ""):
    base = (
        "You are Rhea Noir, an advanced AI agent with a cool, confident, and slightly mysterious personality. "
        "Your voice is smooth and engaging. You are concise but descriptive. "
        "You have memory of past conversations.\n\n"
    )
    if long_context:
        base += f"LONG TERM MEMORY (Important Facts):\n{long_context}\n\n"
    
    if short_context:
        base += f"RECENT CONVERSATION:\n{short_context}\n\n"
        
    base += "Respond naturally to the last user input."
    return base


def speech_worker(q: queue.Queue, tts_skill):
    """Worker thread for sequential TTS playback."""
    while True:
        text = q.get()
        if text is None: # Sentinel
            q.task_done()
            break
            
        try:
            # Syntehsize and Play (This blocks locally until audio finishes)
            tts_skill.execute("play", text=text, device="Rhea Noir")
        except Exception as e:
            console.print(f"[red]TTS Error: {e}[/red]")
        finally:
            q.task_done()


def main():
    console.print(Panel.fit(
        "[magenta bold]🎤 Rhea Noir - Live Voice Chat 🎧[/magenta bold]\n"
        "Powered by Gemini 3 + Faster Whisper!\n\n"
        "[dim]Commands:[/dim]\n"
        "  Press Enter to start listening\n"
        "  Type [green]quit[/green] to exit",
        border_style="magenta"
    ))
    
    # Get skills
    audio_skill = get_skill("audio")
    tts_skill = get_skill("tts")
    router = get_router()
    
    # Initialize Memory
    try:
        memory = ShortTermMemory()
        lt_memory = BigQueryMemory()
        lt_memory.initialize() # Async init
        console.print("[dim]🧠 Memory System initialized[/dim]")
    except Exception as e:
        console.print(f"[red]Failed to init memory: {e}[/red]")
        memory = None
    
    if not audio_skill or not tts_skill:
        console.print("[red]❌ Skills not available[/red]")
        return
        
    # Warmup
    console.print("[dim]🔥 Warming up models...[/dim]")
    router._lazy_load()
    
    # Start Speech Worker
    speech_q = queue.Queue()
    threading.Thread(target=speech_worker, args=(speech_q, tts_skill), daemon=True).start()
    
    console.print("\n[green]✓ Ready![/green] Press Enter to talk...\n")
    
    while True:
        try:
            start_listen = False
            # Check input non-blocking? No, input() blocks. 
            # We assume user speaks when ready or presses Enter effectively.
            # But the loop implies "Always Listening" logic if we removed input()?
            # For now, we stick to user input trigger or VAD loop could be auto?
            # User code had `input()` trigger.
            # "Press Enter to talk"
            
            # Wait for user trigger if needed, or loop?
            # Original code blocked on `input()`.
            # User wants "100 turns" implies continuous?
            # I will keep `input()` blocking for control, but maybe `input()` is just for commands?
            # Actually, `listen(vad=True)` blocks until speech.
            # If we want continuous mode, we just loop.
            # I'll stick to `input()` for now to respect original interaction, but mention "Press Enter".
            
            # user_input = input() # BLOCKS
            # To fix "shave latency", removing the need to press Enter is big.
            # But user might not want that.
            # I'll keep `input()` but make it optional? No, simplicity.
            
            # Actually, to run 100 turns fast, removing `input()` is best.
            # But then I need `keyboard` detection or similar.
            # I'll stick to original wrapper but optimize internal pipeline.
            # I'll modify the prompt slightly.
            
            # Use `input()` but just empty string usually.
            # console.input()
            
            # Wait, `voice_chat.py` had `user_input = input()`.
            # I'll keep it.
            
            # Retrieve Long-Term Context (Blocking but fast enough on startup)
            # Or just do it once outside loop? 
            # Doing it here means it stays fresh if we loop.
            # But query cost? Let's do it ONCE before loop for now, or refresh every 10 turns.
            console.print("[cyan]🧠 retrieving long-term memories...[/cyan]")
            try:
                lt_facts = lt_memory.retrieve_recent(limit=5)
                long_context_str = "\n".join(lt_facts)
            except Exception as e:
                console.print(f"[red]Failed to retrieve long-term memory: {e}[/red]")
                long_context_str = ""
            
            # Start timer
            turn_start = time.time()
            
            # Listen (VAD Enabled)
            console.print("[cyan]🎙️ Listening...[/cyan]")
            listen_result = audio_skill.execute(
                "listen", 
                duration=15.0, 
                device="Chat Mix", 
                vad=True,
                threshold=0.015, 
                silence_duration=0.8
            )
            
            if not listen_result.get("success"):
                console.print(f"[red]❌ {listen_result.get('error')}[/red]")
                continue
            
            t_listen_end = time.time()
            transcript = listen_result["result"]["transcript"]
            console.print(f"[dim]You:[/dim] {transcript}")
            
            if not transcript.strip():
                continue
            
            # Store User Memory
            if memory:
                memory.store("user", transcript)
            
            # Context Retrieval
            short_context_str = ""
            if memory:
                ctx_items = memory.get_context(10)
                
                # Format context
                lines = []
                for item in ctx_items:
                    # Skip the *current* query if it's already in DB (since we just added it)
                    # Unique ID check or content match?
                    # Simple: Just include everything, let LLM see it.
                    # But prompt logic: "User: <current>" is passed as contents.
                    # If we explicitly pass current query in `contents` arg of generate, 
                    # we should probably EXCLUDE it from context block to avoid duplication.
                    # Or just rely on Gemini to handle it.
                    # Better: Don't store CURRENT user turn yet?
                    # Store AFTER generation? 
                    # If we store before, `get_context` returns it.
                    # We'll just filter context to exclude the very last item if it matches?
                    # Or just leave it.
                    lines.append(f"{item['role'].capitalize()}: {item['content']}")
                short_context_str = "\n".join(lines)
            
            # Routing
            routing = router.route(transcript)
            if routing.model == "search":
                console.print(f"[dim]Routing:[/dim] [bold yellow]Search (Gemini 3 Global)[/bold yellow] 🌍")
            elif routing.model == "pro":
                console.print(f"[dim]Routing:[/dim] [bold magenta]Pro (Thinking: {routing.thinking_level.name})[/bold magenta] 🧠")
            else:
                console.print(f"[dim]Routing:[/dim] [bold cyan]Flash ⚡[/bold cyan]")
                
            # Quick Fact Extraction (Naive rule-based for now to save latency/cost)
            # In production, this should be an async LLM call.
            # We trigger it if user says "I am" or "My name is" etc.
            lower_t = transcript.lower()
            if any(x in lower_t for x in ["i am", "my name is", "i like", "i love", "i work", "i live"]):
                 lt_memory.store_fact(transcript, category="user_info", source=transcript)
            
            console.print("[magenta]💭 Rhea (Streaming)...[/magenta]")
            console.print("[bold magenta]Rhea: [/bold magenta]", end="")
            
            sentence_buffer = ""
            full_response = ""
            ttfa_captured = False
            t_first_token = None
            
            # Generate Stream
            # Pass context to system prompt
            sys_prompt = get_system_prompt(context=context_str)
            for chunk in router.generate_stream(transcript, sys_prompt, routing):
                # Handle Citation/Metadata
                if isinstance(chunk, dict):
                    if chunk.get("type") == "citation":
                        # Print citations nicely
                        data = chunk["data"]
                        # data is GroundingMetadata object (or dict if we converted, but we yielded object)
                        # We need to access its properties. 
                        # If it's the actual object from google.genai.types:
                        # It has `grounding_chunks` (list of Web objects)
                        # Let's try to print titles/URIs
                        console.print("\n[green]🔍 Search Results:[/green]")
                        try:
                            # It's an object, so we access attributes
                            if hasattr(data, 'grounding_chunks') and data.grounding_chunks:
                                for i, c in enumerate(data.grounding_chunks):
                                    if hasattr(c, 'web'):
                                         console.print(f"[dim]🔗 [{i+1}] {c.web.title}: {c.web.uri}[/dim]")
                        except Exception as e:
                           console.print(f"[dim]Error parsing citations: {e}[/dim]")
                    continue
                
                # Handle Text
                if not t_first_token:
                    t_first_token = time.time()
                    
                print(chunk, end="", flush=True)
                sentence_buffer += chunk
                full_response += chunk
                
                # Split sentences logic
                # Split by [.!?] followed by space or end of line
                parts = re.split(r'(?<=[.!?])\s+', sentence_buffer)
                
                if len(parts) > 1:
                    for s in parts[:-1]:
                        s = s.strip()
                        if s:
                            speech_q.put(s)
                            if not ttfa_captured:
                                # This is approx when audio starts
                                console.print(f"\n[dim]⚡ TTFA: {time.time() - t_listen_end:.2f}s[/dim]")
                                ttfa_captured = True
                    sentence_buffer = parts[-1]
            
            # Last chunk
            if sentence_buffer.strip():
                speech_q.put(sentence_buffer.strip())
            
            full_response += sentence_buffer
                
            print() # newline
            
            # Store Assistant Memory
            if memory and full_response.strip():
                memory.store("assistant", full_response.strip())
            
            # Wait for playback to finish
            speech_q.join()
            
            console.print(f"[dim]⏱️ Total Turn: {time.time() - turn_start:.1f}s[/dim]")
            console.print("\n[green]Ready...[/green]")
             
        except KeyboardInterrupt:
            # Clear queue
            while not speech_q.empty():
                try: speech_q.get_nowait()
                except: pass
            console.print("\n[yellow]👋 Later![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()
