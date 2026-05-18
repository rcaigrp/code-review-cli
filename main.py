import argparse
import os
import datetime
import time
from monitor import GitHubMonitor
from report import render_table

def main():
    parser = argparse.ArgumentParser(description="Org-Wide PR Aging & Review Velocity CLI")
    parser.add_argument('--org', required=True, help="GitHub organization name")
    parser.add_argument('--min_days_stale', type=int, default=14, help="Minimum days to consider PR stale")
    args = parser.parse_args()
    
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable is required.")
        return
        
    monitor = GitHubMonitor(token, args.org)
    
    repos = monitor.fetch_repos()
    all_prs = []
    
    for repo in repos:
        prs = monitor.fetch_prs(repo)
        for pr in prs:
            try:
                updated = datetime.datetime.fromisoformat(pr['updated_at'].replace('Z', '+00:00'))
                now = datetime.datetime.now(datetime.timezone.utc)
                days_open = (now - updated).days
                
                if days_open < args.min_days_stale:
                    continue
                    
                comments = pr.get('comments', 0)
                review_density = comments / days_open if days_open > 0 else 0
                
                all_prs.append({
                    'repo': repo['full_name'],
                    'pr_number': pr['number'],
                    'author': pr['user']['login'] if pr.get('user') else 'N/A',
                    'days_open': days_open,
                    'review_density': review_density,
                    'url': pr['html_url']
                })
            except Exception:
                continue
            
    all_prs.sort(key=lambda x: x['days_open'], reverse=True)
    render_table(all_prs)

if __name__ == '__main__':
    main()
