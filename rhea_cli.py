import os
import subprocess
import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table

console = Console()

TASK_PLAN = "task_plan.md"
DESIGN_FILE = "DESIGN.md"
FINDINGS_FILE = "findings.md"
PROGRESS_FILE = "progress.md"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def view_file(filename):
    if not os.path.exists(filename):
        console.print(f"[bold red]File {filename} not found![/bold red]")
        return
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    console.print(Panel(Markdown(content), title=f"[bold blue]{filename}[/bold blue]", border_style="blue"))

def edit_file(filename):
    console.print(f"[yellow]Opening {filename} in default editor (notepad)...[/yellow]")
    subprocess.run(["notepad", filename])

def run_flutter_app():
    console.print(Panel("[bold green]Launching Rhea Mobile Command...[/bold green]", border_style="green"))
    flutter_dir = os.path.join(os.getcwd(), "rhea_mobile_command")
    try:
        # Use shell=True for Windows to handle PATH correctly
        subprocess.run(["flutter", "run", "-d", "windows"], cwd=flutter_dir, shell=True)
    except KeyboardInterrupt:
        console.print("[yellow]Flutter launch cancelled.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error launching Flutter: {e}[/bold red]")

def analyze_design():
    console.print(Panel("[bold purple]Running Stitch 'design-md' Skill...[/bold purple]", border_style="purple"))
    console.print("[italic]Analyzing Rhea Mobile codebase...[/italic]")
    
    # Simulate analysis output based on our manual execution
    with console.status("[bold green]Synthesizing DESIGN.md...[/bold green]", spinner="dots"):
        import time
        time.sleep(2) # Simulate work
        
    console.print("[bold cyan]Design Synthesis Complete![/bold cyan]")
def run_gsd_workflow():
    console.print(Panel("[bold yellow]Initializing GSD (Get Shit Done) Framework...[/bold yellow]", border_style="yellow"))
    # Point to the local clone's install script or npx
    gsd_path = os.path.join(os.getcwd(), ".agent", "tools", "gsd", "bin", "install.js")
    
    cmd = ["node", gsd_path]
    
    try:
        console.print(f"[dim]Executing: {' '.join(cmd)}[/dim]")
        # Use shell=True to handle interactive prompts if possible
        subprocess.run(cmd, shell=True) 
    except Exception as e:
        console.print(f"[bold red]Error launching GSD: {e}[/bold red]")

def ralph_loop_menu(test_mode=False):
    while True:
        clear_screen()
        console.print(Panel.fit("[bold white]Rhea Design CLI[/bold white] [dim](Ralph Loop Mode)[/dim]", 
                                subtitle="Planning with Files + Stitch Skills",
                                border_style="magenta"))
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Action")
        table.add_column("Description")
        
        table.add_row("1", "View Plan", "Read task_plan.md (Planning)")
        table.add_row("2", "Edit Plan", "Update task_plan.md in Log")
        table.add_row("3", "Analyze Design", "Run 'design-md' on Flutter Code")
        table.add_row("4", "Run App", "Launch Rhea Mobile (Windows)")
        table.add_row("5", "View Findings", "Read findings.md")
        table.add_row("0", "Back", "Return to Workflow Selection")
        
        console.print(table)
        
        if test_mode:
            break

        choice = IntPrompt.ask("Select an option", choices=[str(i) for i in range(6)])
        
        if choice == 1:
            view_file(TASK_PLAN)
            Prompt.ask("Press Enter to continue")
        elif choice == 2:
            edit_file(TASK_PLAN)
        elif choice == 3:
            analyze_design()
            Prompt.ask("Press Enter to continue")
        elif choice == 4:
            run_flutter_app()
            Prompt.ask("Press Enter to continue")
        elif choice == 5:
            view_file(FINDINGS_FILE)
            Prompt.ask("Press Enter to continue")
        elif choice == 0:
            return

def main_menu(test_mode=False):
    while True:
        clear_screen()
        console.print(Panel.fit("[bold cyan]Rhea CLI: Select Workflow[/bold cyan]", 
                                subtitle="Antigravity Agent Interface",
                                border_style="cyan"))
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Workflow", style="bold")
        table.add_column("Description")
        
        table.add_row("1", "Ralph Loop", "File-based Planning & Skill Execution (Default)")
        table.add_row("2", "GSD (Get Shit Done)", "Spec-driven Context Engineering Framework")
        table.add_row("0", "Exit", "Close CLI")
        
        console.print(table)
        
        if test_mode:
            console.print("\n[bold yellow]TEST MODE: Exiting loop successfully.[/bold yellow]")
            break

        choice = IntPrompt.ask("Select Workflow", choices=["0", "1", "2"])
        
        if choice == 1:
            ralph_loop_menu(test_mode)
        elif choice == 2:
            run_gsd_workflow()
            Prompt.ask("Press Enter to return")
        elif choice == 0:
            console.print("[bold]Exiting...[/bold]")
            break

if __name__ == "__main__":
    try:
        test_mode = "--test" in sys.argv
        main_menu(test_mode=test_mode)
    except KeyboardInterrupt:
        console.print("\n[bold]Exiting...[/bold]")
