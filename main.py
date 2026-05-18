"""CLI entry point for Org-Wide PR Aging & Review Velocity."""

import argparse
import os
import sys
from monitor import GitHubMonitor
from report import render_report


def parse_args(args=None):
    """Parse command line arguments.
    
    Args:
        args: Command line arguments
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Track PR age, review activity, and tech debt across GitHub orgs'
    )
    parser.add_argument('--org', required=True, help='GitHub organization name')
    parser.add_argument('--min-days-stale', type=int, default=14, help='Minimum days to consider stale')
    parser.add_argument('--output-format', choices=['table', 'json'], default='table', help='Output format')
    
    return parser.parse_args(args)


def main():
    """Main entry point."""
    args = parse_args()
    
    # Get token from env
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print('❌ Error: GITHUB_TOKEN environment variable not set')
        sys.exit(1)
        
    # Create monitor
    try:
        monitor = GitHubMonitor(token)
    except ValueError as e:
        print(f'❌ Error: {e}')
        sys.exit(1)
        
    try:
        # Process org
        data = monitor.process_org(args.org, args.min_days_stale)
        
        # Render report
        render_report(data, args.output_format)
        
    except Exception as e:
        print(f'❌ Error: {e}')
        sys.exit(1)
    finally:
        monitor.close()


if __name__ == '__main__':
    main()
