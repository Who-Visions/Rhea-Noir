"""
Flutter Vibe Interactive Menu - Rich CLI for Flutter development
Provides an interactive menu for all FlutterVibeSkill actions.
"""

from typing import Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.markdown import Markdown
    from rich import box
except ImportError:
    Console = None
    Panel = None


FLUTTER_ACTIONS = [
    {
        "label": "🚀 Scaffold New App",
        "value": "scaffold_app",
        "description": "Create a new Vibe-Coded Flutter project structure",
        "prompts": [
            {"key": "name", "prompt": "App name", "default": "vibe_app"},
            {"key": "description", "prompt": "Description", "default": None},
        ],
    },
    {
        "label": "🧩 Generate Widget",
        "value": "generate_widget",
        "description": "Create a premium reusable widget",
        "prompts": [
            {"key": "prompt", "prompt": "Describe the widget", "default": None},
            {"key": "name", "prompt": "Widget name", "default": "CustomWidget"},
        ],
    },
    {
        "label": "📦 Generate Feature",
        "value": "generate_feature",
        "description": "Create a full feature slice (domain, data, presentation)",
        "prompts": [
            {"key": "name", "prompt": "Feature name", "default": None},
            {"key": "requirements", "prompt": "Requirements", "default": "CRUD operations"},
        ],
    },
    {
        "label": "📱 Generate Screen",
        "value": "generate_screen",
        "description": "Create a complete screen with state management",
        "prompts": [
            {"key": "name", "prompt": "Screen name", "default": None},
            {"key": "description", "prompt": "Description", "default": None},
            {"key": "feature", "prompt": "Feature folder", "default": "home"},
        ],
    },
    {
        "label": "🔍 Explain Code",
        "value": "explain_code",
        "description": "Mentor-style analysis with Vibe standards verification",
        "prompts": [
            {"key": "code", "prompt": "Paste your Dart code", "default": None, "multiline": True},
        ],
    },
    {
        "label": "✅ Review Code",
        "value": "review_code",
        "description": "Compliance score (0-100) with specific fixes",
        "prompts": [
            {"key": "code", "prompt": "Paste your Dart code", "default": None, "multiline": True},
        ],
    },
    {
        "label": "🤖 Ralph Mode",
        "value": "ralph_mode",
        "description": "Autonomous verified development loop (Generator -> Verifier -> Refiner)",
        "prompts": [
            {"key": "goal", "prompt": "What is the goal? (e.g. Create a glassmorphic login screen)", "default": None},
            {"key": "context_code", "prompt": "Starting code (optional)", "default": None, "multiline": True},
        ],
    },
]


def show_flutter_menu(console: Optional[Console] = None) -> None:
    """Display interactive Flutter action menu."""
    if console is None:
        console = Console()

    # Header
    console.print()
    console.print(Panel(
        "[bold bright_magenta]🌙 Flutter Vibe Studio[/bold bright_magenta]\n\n"
        "[dim]Premium Flutter Development with Vibe-Coded Standards[/dim]\n"
        "[dim cyan]Riverpod • GoRouter • Material 3 • Deep Space Theme[/dim]",
        border_style="bright_magenta",
        box=box.DOUBLE,
    ))

    # Action table
    table = Table(
        title="[bold]Available Actions[/bold]",
        box=box.ROUNDED,
        border_style="bright_magenta",
        show_header=True,
        header_style="bold bright_red",
    )
    table.add_column("#", style="bright_magenta", width=3)
    table.add_column("Action", style="bold white")
    table.add_column("Description", style="dim")

    for i, action in enumerate(FLUTTER_ACTIONS, 1):
        table.add_row(str(i), action["label"], action["description"])

    console.print(table)
    console.print()

    # Selection
    choice = Prompt.ask(
        "[bright_magenta]Select action[/bright_magenta]",
        choices=[str(i) for i in range(1, len(FLUTTER_ACTIONS) + 1)] + ["q", "quit"],
        default="q",
    )

    if choice in ("q", "quit"):
        console.print("[dim]Exiting Flutter Vibe Studio[/dim]")
        return

    action = FLUTTER_ACTIONS[int(choice) - 1]
    console.print(f"\n[bold bright_magenta]▶ {action['label']}[/bold bright_magenta]\n")

    # Collect prompts
    params = {}
    for prompt_config in action.get("prompts", []):
        if prompt_config.get("multiline"):
            console.print(f"[cyan]{prompt_config['prompt']}[/cyan] (paste code, then Ctrl+D or empty line to finish):")
            lines = []
            try:
                while True:
                    line = input()
                    if line == "":
                        break
                    lines.append(line)
            except EOFError:
                pass
            params[prompt_config["key"]] = "\n".join(lines)
        else:
            value = Prompt.ask(
                f"[cyan]{prompt_config['prompt']}[/cyan]",
                default=prompt_config.get("default"),
            )
            if value:
                params[prompt_config["key"]] = value

    # Execute
    console.print("\n[dim]Generating with Gemini 2.5 Flash...[/dim]\n")

    try:
        from rhea_noir.skills.flutter_vibe.actions import skill as flutter_skill
        result = flutter_skill.execute(action["value"], **params)

        if result.get("success"):
            console.print(Panel(
                Markdown(result.get("result", "")),
                title=f"[bold green]✓ {action['label']}[/bold green]",
                border_style="green",
            ))
        else:
            console.print(Panel(
                f"[red]{result.get('error', 'Unknown error')}[/red]",
                title="[bold red]✗ Error[/bold red]",
                border_style="red",
            ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def quick_scaffold(name: str, description: Optional[str] = None, console: Optional[Console] = None) -> dict:
    """Quick scaffold without interactive menu."""
    if console is None:
        console = Console()

    console.print(f"[dim]Scaffolding {name}...[/dim]")

    from rhea_noir.skills.flutter_vibe.actions import skill as flutter_skill
    result = flutter_skill.execute("scaffold_app", name=name, description=description)

    if result.get("success") and console:
        console.print(Panel(
            Markdown(result.get("result", "")),
            title=f"[bold green]✓ Scaffolded {name}[/bold green]",
            border_style="green",
        ))

    return result


if __name__ == "__main__":
    show_flutter_menu()
