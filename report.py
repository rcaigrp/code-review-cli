from typing import List, Dict
try:
    from rich.console import Console
    from rich.table import Table
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

def render_table(data: List[Dict]) -> str:
    if HAS_RICH:
        console = Console(force_terminal=True)
        with console.capture() as capture:
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Repo", style="dim", width=20)
            table.add_column("PR #", style="number", width=10)
            table.add_column("Author", style="bold", width=15)
            table.add_column("Days Open", style="number", width=10)
            table.add_column("Review Density", style="dim", width=15)
            table.add_column("Link", style="bold", width=30)
            
            for item in data:
                days = item.get('days_open', 0)
                color = "green" if days < 7 else ("yellow" if days <= 14 else "red")
                table.add_row(
                    item.get('repo', 'N/A'),
                    str(item.get('pr_number', 'N/A')),
                    item.get('author', 'N/A'),
                    str(days),
                    f"{item.get('review_density', 0):.2f}",
                    item.get('link', 'N/A')
                )
            console.print(table)
            return capture.get()
    else:
        output = "Repo\tPR #\tAuthor\tDays Open\tReview Density\tLink\n"
        output += "-" * 80 + "\n"
        for item in data:
            output += f"{item.get('repo', 'N/A')}\t{item.get('pr_number', 'N/A')}\t{item.get('author', 'N/A')}\t{item.get('days_open', 'N/A')}\t{item.get('review_density', 0):.2f}\t{item.get('link', 'N/A')}\n"
        return output
