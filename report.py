"""Terminal report rendering using rich."""

from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()


def get_age_color(days: int) -> str:
    """Get color code based on PR age.
    
    Args:
        days: Days open
        
    Returns:
        Color string
    """
    if days < 7:
        return 'green'
    elif days <= 14:
        return 'yellow'
    else:
        return 'red'


def format_density(density: float) -> str:
    """Format review density.
    
    Args:
        density: Review density value
        
    Returns:
        Formatted string
    """
    return f'{density:.2f}'


def render_report(data: List[Dict], output_format: str = 'table') -> None:
    """Render PR data to terminal.
    
    Args:
        data: List of PR data dicts
        output_format: Output format ('table' or 'json')
    """
    if output_format == 'json':
        import json
        console.print(json.dumps(data, indent=2))
        return
        
    # Create table
    table = Table(
        title='📊 GitHub PR Aging & Review Velocity Report',
        show_header=True,
        header_style='bold blue',
        border_style='blue',
    )
    
    table.add_column('📁 Repo', style='dim', max_width=20)
    table.add_column('#', style='dim', max_width=5)
    table.add_column('👤 Author', style='dim', max_width=15)
    table.add_column('⏱️ Days Open', style='dim', max_width=10)
    table.add_column('📈 Density', style='dim', max_width=10)
    table.add_column('🔗 Link', style='dim', max_width=30)
    
    # Add rows with color coding
    for item in data:
        days = item['days_open']
        color = get_age_color(days)
        
        # Format row data
        repo = item['repo']
        pr_num = str(item['pr_number'])
        author = item['author']
        days_str = str(days)
        density_str = format_density(item['review_density'])
        link = item['link']
        
        table.add_row(
            repo,
            pr_num,
            author,
            days_str,
            density_str,
            link,
            style=color
        )
        
    console.print(table)
    
    # Print summary
    total = len(data)
    stale = sum(1 for item in data if item['days_open'] > 14)
    console.print(f'\n📈 Summary: {total} PRs tracked, {stale} stale (>14 days)')
    
    if data:
        max_days = max(item['days_open'] for item in data)
        console.print(f'⚠️  Oldest PR: {max_days} days open')
