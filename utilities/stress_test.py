import time
import queue
import threading
import random
from dotenv import load_dotenv

load_dotenv()
from rich.console import Console
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rhea_noir.gemini3_router import get_router, Gemini3Router
from rhea_noir.memory.long_term import BigQueryMemory
from rhea_noir.memory.short_term import ShortTermMemory

console = Console()

def run_stress_test(turns=10):
    console.print(f"[bold red]🔥 Starting Deep Stress Validation for {turns} turns...[/bold red]")
    
    # Init Components
    router = Gemini3Router()
    lt_memory = BigQueryMemory()
    lt_memory.initialize()
    st_memory = ShortTermMemory()
    
    # Metrics
    latencies = []
    errors = 0
    
    test_prompts = [
        "Who is the CEO of Google?",
        "What is the capital of France?",
        "My favorite color is simulated-blue.",
        "Tell me a short joke about AI.",
        "What is the weather in Tokyo today?",
        "Explain quantum computing in one sentence.",
        "Who won the 2024 Super Bowl?",
        "I am testing your memory system.",
        "What did I say my favorite color was?",
        "Generate a random number."
    ]

    for i in range(turns):
        prompt = random.choice(test_prompts)
        console.print(f"\n[bold cyan]Turn {i+1}/{turns}:[/bold cyan] User: {prompt}")
        
        t_start = time.time()
        try:
            # 1. Route
            routing = router.route(prompt)
            console.print(f"  Routing: {routing.model}")
            
            # 2. Store Short Term
            st_memory.store("user", prompt)
            
            # 3. Store Long Term (Simulated Extraction)
            if "favorite color" in prompt:
                lt_memory.store_fact(prompt, category="preference", source="stress_test")
                console.print("  [dim]Stored Fact via BigQuery[/dim]")

            # 4. Generate
            console.print("  Generating...", end="")
            chunks = []
            citations = 0
            for chunk in router.generate_stream(prompt, system_prompt="You are a test bot."):
                if isinstance(chunk, dict) and chunk.get("type") == "citation":
                    citations += 1
                elif isinstance(chunk, str):
                    chunks.append(chunk)

            response = "".join(chunks)
            t_end = time.time()
            duration = t_end - t_start
            latencies.append(duration)
            
            console.print(f"  [green]Success[/green] ({duration:.2f}s) | Citations: {citations}")
            
            # 5. Store Response
            st_memory.store("assistant", response)
            
        except Exception as e:
            console.print(f"  [bold red]ERROR: {e}[/bold red]")
            errors += 1
        
        time.sleep(0.5) # Rate limit kindness

    # Summary
    avg_lat = sum(latencies) / len(latencies) if latencies else 0
    console.print(f"\n[bold green]✅ Stress Test Complete[/bold green]")
    console.print(f"Total Turns: {turns}")
    console.print(f"Errors: {errors}")
    console.print(f"Avg Latency: {avg_lat:.2f}s")

if __name__ == "__main__":
    run_stress_test(turns=10) # Default to 10 for safety, easy to scale
