import argparse
import sys
import monitor
import report

def main():
    parser = argparse.ArgumentParser(description="Org-Wide PR Aging & Review Velocity CLI")
    parser.add_argument("--org", required=True, help="GitHub organization name")
    parser.add_argument("--min_days_stale", type=int, default=14, help="Minimum days open to consider PR stale")
    parser.add_argument("--output_format", type=str, default="table", help="Output format (table)")
    
    args = parser.parse_args()
    
    try:
        data = monitor.fetch_pr_data(args.org, args.min_days_stale)
        if not data:
            print("No stale PRs found.")
            return
        report.render_table(data)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
