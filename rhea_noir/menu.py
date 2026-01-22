"""
Rhea Noir Interactive Menu - Keyboard-navigable help and menus
"""

from typing import List, Optional, Dict, Any

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.styles import Style
except ImportError:
    PromptSession = None
    KeyBindings = None
    HTML = None
    Style = None

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
except ImportError:
    Console = None
    Panel = None
    Table = None
    box = None


class InteractiveMenu:
    """Interactive menu with keyboard navigation"""

    def __init__(self, console: Console):
        self.console = console
        self.style = Style.from_dict({
            'selected': 'bg:#FF00FF #FFFFFF bold',
            'option': '#FFFFFF',
            'hint': '#888888 italic',
        })

    def select(
        self,
        title: str,
        options: List[Dict[str, Any]],
        allow_cancel: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Display interactive selection menu.

        Args:
            title: Menu title
            options: List of dicts with 'label', 'value', 'description'
            allow_cancel: Allow ESC to cancel

        Returns:
            Selected option dict or None if cancelled
        """
        selected_index = 0

        kb = KeyBindings()

        @kb.add('up')
        @kb.add('k')
        def move_up(event):
            nonlocal selected_index
            selected_index = (selected_index - 1) % len(options)

        @kb.add('down')
        @kb.add('j')
        def move_down(event):
            nonlocal selected_index
            selected_index = (selected_index + 1) % len(options)

        result = [None]  # Use list to allow mutation in closure

        @kb.add('enter')
        def select_option(event):
            result[0] = options[selected_index]
            event.app.exit()

        @kb.add('escape')
        @kb.add('q')
        def cancel(event):
            if allow_cancel:
                event.app.exit()

        # Create session with key bindings
        session = PromptSession(key_bindings=kb)

        def get_prompt():
            lines = [f"\n[bold bright_magenta]{title}[/bold bright_magenta]\n"]
            lines.append("[dim]Use ↑/↓ or j/k to navigate, Enter to select, ESC to cancel[/dim]\n")

            for i, opt in enumerate(options):
                if i == selected_index:
                    lines.append(f"  [bold bright_magenta]❯[/bold bright_magenta] [bold]{opt['label']}[/bold]")
                    if opt.get('description'):
                        lines.append(f"    [dim]{opt['description']}[/dim]")
                else:
                    lines.append(f"    {opt['label']}")

            return '\n'.join(lines)

        # Display and wait for input
        self.console.print(get_prompt())

        try:
            session.prompt(
                HTML('<ansibrightmagenta>❯</ansibrightmagenta> '),
                refresh_interval=0.5,
            )
        except (EOFError, KeyboardInterrupt):
            pass

        return result[0]


def show_interactive_help(console: Console) -> None:
    """Display interactive help menu"""

    categories = [
        {
            "label": "💬 Chat Commands",
            "value": "chat",
            "description": "Conversation and messaging",
            "commands": [
                ("/help", "Show this help menu"),
                ("/clear", "Clear screen and history"),
                ("/history", "View conversation history"),
                ("/exit", "Exit Rhea Noir"),
            ]
        },
        {
            "label": "💾 Memory Commands",
            "value": "memory",
            "description": "Memory and recall",
            "commands": [
                ("/recall <query>", "Search your memories"),
                ("/memory", "Show memory statistics"),
                ("/sync", "Force sync to cloud"),
            ]
        },
        {
            "label": "🔍 Search Commands",
            "value": "search",
            "description": "Knowledge and web search",
            "commands": [
                ("/search <query>", "Search knowledge base"),
                ("/web <query>", "Search with Google grounding"),
            ]
        },
        {
            "label": "⚡ Task Commands",
            "value": "tasks",
            "description": "Long-running tasks",
            "commands": [
                ("/task <desc>", "Start a long-running task"),
                ("/tasks", "List all tasks"),
                ("/task-status <id>", "Check task status"),
            ]
        },
        {
            "label": "🧠 Model Commands",
            "value": "model",
            "description": "Model selection and routing",
            "commands": [
                ("/model", "Show current model"),
                ("/model lite|flash|pro|elite", "Set model tier"),
            ]
        },
        {
            "label": "📊 Status Commands",
            "value": "status",
            "description": "System status and info",
            "commands": [
                ("/status", "Show system status"),
                ("/preferences", "Show learned preferences"),
            ]
        },
    ]

    # Show category selection
    console.print()
    console.print(Panel(
        "[bold bright_magenta]🌙 Rhea Noir Help[/bold bright_magenta]\n\n"
        "[dim]Select a category to see commands:[/dim]",
        border_style="bright_magenta",
        box=box.ROUNDED,
    ))

    # Display all categories as expandable sections
    for cat in categories:
        table = Table(
            title=cat["label"],
            box=box.ROUNDED,
            border_style="bright_magenta",
            show_header=True,
            header_style="bold bright_red",
            expand=False,
        )
        table.add_column("Command", style="bright_red", width=25)
        table.add_column("Description", style="white")

        for cmd, desc in cat["commands"]:
            table.add_row(cmd, desc)

        console.print(table)
        console.print()

    # Navigation hint
    console.print(
        "[dim]Tip: Use ↑/↓ arrows to navigate command history[/dim]"
    )
    console.print()
