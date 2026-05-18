from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

def render_table(data: List[Dict[str, Any]]) -> None:
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Repo", style="dim")
    table.add_column("PR #", justify="right", style="cyan")
    table.add_column("Author", style="green")
    table.add_column("Days Open", justify="right")
    table.add_column("Review Density", justify="right")
    table.add_column("Link")

    for item in data:
        days = item['days_open']
        if days < 7:
            color = "green"
        elif days <= 14:
            color = "yellow"
        else:
            color = "red"
            
        table.add_row(
            str(item['repo']),
            str(item['pr_number']),
            str(item['author']),
            Text(str(days), style=color),
            Text(f"{item['review_density']:.2f}", style="bold"),
            str(item['url'])
        )
    console.print(table)
