#!/usr/bin/env python3
"""
Rhea CLI - The Superhero Interface
Just tell Rhea what you want, she'll figure out the rest.
"""
import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def main():
    parser = argparse.ArgumentParser(
        description="Rhea - Your AI Superhero Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rhea "search for latest AI news"
  rhea "download this video: https://youtube.com/..."
  rhea "summarize this PDF" --file report.pdf
  rhea "find restaurants near me" --lat 40.7 --lng -74.0
  rhea --skills  # List all capabilities
        """
    )
    
    parser.add_argument("request", nargs="?", help="What you want Rhea to do")
    parser.add_argument("--skills", "-s", action="store_true", help="List all skills")
    parser.add_argument("--flutter", "-F", action="store_true", help="Flutter development mode")
    parser.add_argument("--route", "-r", action="store_true", help="Just route, don't execute")
    parser.add_argument("--file", "-f", help="File to process")
    parser.add_argument("--url", "-u", help="URL to process")
    parser.add_argument("--lat", type=float, help="Latitude for location")
    parser.add_argument("--lng", type=float, help="Longitude for location")
    
    args = parser.parse_args()
    
    # Import after parsing to speed up --help
    from rhea_noir.router import reflex, capabilities
    
    # List skills
    if args.skills:
        console.print(Panel("[bold cyan]Rhea's Superpowers[/bold cyan]", expand=False))
        for cap in capabilities():
            console.print(f"  [green]•[/green] [bold]{cap['skill']}[/bold]: {cap['description']}")
            triggers = ", ".join(cap['triggers'][:3])
            console.print(f"    [dim]Triggers: {triggers}...[/dim]")
        return

    # Flutter development mode
    if args.flutter:
        from rhea_noir.flutter_menu import show_flutter_menu
        show_flutter_menu(console)
        return

    # Need a request
    if not args.request:
        console.print("[yellow]Tell Rhea what you want![/yellow]")
        console.print("Example: [cyan]rhea 'search for latest AI news'[/cyan]")
        console.print("         [cyan]rhea --flutter[/cyan] for Flutter development")
        return
    
    # Build context
    context = {}
    if args.file:
        context["file"] = args.file
    if args.url:
        context["url"] = args.url
    if args.lat and args.lng:
        context["location"] = {"lat": args.lat, "lng": args.lng}
    
    # Route only
    if args.route:
        result = reflex.route(args.request, context)
        console.print(Panel(f"[cyan]Skill:[/cyan] {result.get('skill')}\n"
                           f"[cyan]Confidence:[/cyan] {result.get('confidence')}\n"
                           f"[cyan]Method:[/cyan] {result.get('method')}"))
        return
    
    # Execute!
    console.print(f"[dim]Rhea is processing...[/dim]")
    result = reflex.execute(args.request, context)
    
    if result.get("success"):
        console.print(Panel(
            f"[green]✓[/green] [bold]{result.get('skill')}[/bold] → {result.get('action', 'executed')}\n\n"
            f"{str(result.get('result', {}))[:500]}",
            title="[bold green]Success[/bold green]"
        ))
    else:
        console.print(Panel(
            f"[red]✗[/red] {result.get('error', 'Unknown error')}\n"
            f"[dim]Routing: {result.get('routing', {})}[/dim]",
            title="[bold red]Failed[/bold red]"
        ))


if __name__ == "__main__":
    main()
