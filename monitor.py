"""Core logic for GitHub PR monitoring, filtering, and scoring."""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from typing import Union


class GitHubMonitor:
    """Monitors GitHub organization PRs for aging and review velocity."""
    
    BASE_URL = "https://api.github.com"
    DEFAULT_STALE_DAYS = 14
    MAX_RETRIES = 3
    RATE_LIMIT_BACKOFF = 5  # seconds
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub monitor.
        
        Args:
            token: GitHub API token. If None, tries GITHUB_TOKEN env var.
        """
        self.token = token or os.environ.get('GITHUB_TOKEN')
        if not self.token:
            raise ValueError('GitHub token not provided. Set GITHUB_TOKEN env var.')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/vnd.github.v3+json',
        })
        
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Tuple[Dict, Dict]:
        """Make a request with rate limit handling.
        
        Args:
            url: Request URL
            params: Query parameters
            
        Returns:
            Tuple of (response_data, headers)
            
        Raises:
            requests.HTTPError: On HTTP errors
            ValueError: On invalid responses
        """
        params = params or {}
        retries = self.MAX_RETRIES
        
        while retries > 0:
            response = self.session.get(url, params=params)
            
            # Check rate limit
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            if remaining < 10:
                print(f'⚠️  Rate limit low: {remaining} requests remaining')
                import time
                time.sleep(self.RATE_LIMIT_BACKOFF)
                retries -= 1
                continue
            
            # Handle errors
            if response.status_code == 403:
                raise requests.HTTPError(f'Rate limit exceeded: {response.text}')
            elif response.status_code == 404:
                raise requests.HTTPError(f'Not found: {response.text}')
            elif response.status_code >= 400:
                raise requests.HTTPError(f'HTTP error {response.status_code}: {response.text}')
                
            # Try to parse JSON
            try:
                data = response.json()
            except ValueError:
                raise ValueError(f'Invalid JSON response from {url}')
                
            return data, dict(response.headers)
            
        raise requests.HTTPError('Max retries exceeded')
        
    def fetch_repos(self, org: str) -> List[Dict]:
        """Fetch all repositories for an organization.
        
        Args:
            org: Organization name
            
        Returns:
            List of repo dicts
            
        Raises:
            requests.HTTPError: On API errors
        """
        repos = []
        url = f'{self.BASE_URL}/orgs/{org}/repos'
        params = {'per_page': 100}
        
        while True:
            data, headers = self._make_request(url, params)
            repos.extend(data)
            
            # Check for pagination
            next_url = headers.get('Link', '')
            if 'rel="next"' in next_url:
                params = {'per_page': 100}
                url = next_url.split('&')[0]  # Get base URL
            else:
                break
                
        return repos
        
    def fetch_prs(self, repo: Dict) -> List[Dict]:
        """Fetch all PRs for a repository.
        
        Args:
            repo: Repository dict with name and owner
            
        Returns:
            List of PR dicts
        """
        prs = []
        owner = repo['owner']['login']
        name = repo['name']
        url = f'{self.BASE_URL}/repos/{owner}/{name}/pulls'
        params = {'per_page': 100, 'state': 'all'}
        
        while True:
            data, headers = self._make_request(url, params)
            prs.extend(data)
            
            # Check for pagination
            next_url = headers.get('Link', '')
            if 'rel="next"' in next_url:
                params = {'per_page': 100}
                url = next_url.split('&')[0]
            else:
                break
                
        return prs
        
    def fetch_pr_comments(self, pr: Dict) -> int:
        """Fetch comments for a PR.
        
        Args:
            pr: Pull request dict
            
        Returns:
            Number of comments
        """
        url = f'{self.BASE_URL}/repos/{pr['base']['repo']['owner']['login']}/{pr['base']['repo']['name']}/issues/{pr['number']}/comments'
        params = {'per_page': 100}
        count = 0
        
        while True:
            data, headers = self._make_request(url, params)
            count += len(data)
            
            next_url = headers.get('Link', '')
            if 'rel="next"' in next_url:
                params = {'per_page': 100}
                url = next_url.split('&')[0]
            else:
                break
                
        return count
        
    def fetch_issue_comments(self, pr: Dict) -> int:
        """Fetch comments for the associated issue.
        
        Args:
            pr: Pull request dict
            
        Returns:
            Number of comments
        """
        url = f'{self.BASE_URL}/repos/{pr['base']['repo']['owner']['login']}/{pr['base']['repo']['name']}/issues/{pr['number']}/comments'
        params = {'per_page': 100}
        count = 0
        
        while True:
            data, headers = self._make_request(url, params)
            count += len(data)
            
            next_url = headers.get('Link', '')
            if 'rel="next"' in next_url:
                params = {'per_page': 100}
                url = next_url.split('&')[0]
            else:
                break
                
        return count
        
    def calculate_days_open(self, pr: Dict) -> int:
        """Calculate days a PR has been open.
        
        Args:
            pr: Pull request dict
            
        Returns:
            Days open as integer
        """
        try:
            created = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return 0
            
        now = datetime.utcnow()
        delta = now - created
        return delta.days
        
    def calculate_review_density(self, pr: Dict, comments: int) -> float:
        """Calculate review density.
        
        Args:
            pr: Pull request dict
            comments: Number of comments
            
        Returns:
            Review density (comments per day)
        """
        days = self.calculate_days_open(pr)
        if days == 0:
            return 0.0
        return comments / days
        
    def filter_stale_prs(self, prs: List[Dict], min_days: int = None) -> List[Dict]:
        """Filter PRs that are older than min_days.
        
        Args:
            prs: List of PR dicts
            min_days: Minimum days to consider stale
            
        Returns:
            Filtered list of PR dicts
        """
        min_days = min_days or self.DEFAULT_STALE_DAYS
        result = []
        
        for pr in prs:
            days = self.calculate_days_open(pr)
            if days > min_days:
                pr['days_open'] = days
                result.append(pr)
                
        return result
        
    def enrich_pr_data(self, pr: Dict) -> Dict:
        """Enrich PR data with calculated fields.
        
        Args:
            pr: Pull request dict
            
        Returns:
            Enriched PR dict
        """
        pr['days_open'] = self.calculate_days_open(pr)
        pr['review_density'] = self.calculate_review_density(pr, 0)
        return pr
        
    def get_pr_data(self, pr: Dict) -> Dict:
        """Get complete PR data with comments and metadata.
        
        Args:
            pr: Pull request dict
            
        Returns:
            Complete PR data dict
        """
        owner = pr['base']['repo']['owner']['login']
        repo_name = pr['base']['repo']['name']
        pr_number = pr['number']
        
        # Fetch comments
        url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/issues/{pr_number}/comments'
        params = {'per_page': 100}
        comment_count = 0
        
        while True:
            data, headers = self._make_request(url, params)
            comment_count += len(data)
            
            next_url = headers.get('Link', '')
            if 'rel="next"' in next_url:
                params = {'per_page': 100}
                url = next_url.split('&')[0]
            else:
                break
                
        days = self.calculate_days_open(pr)
        density = comment_count / days if days > 0 else 0.0
        
        return {
            'repo': f"{owner}/{repo_name}",
            'pr_number': pr_number,
            'author': pr['user']['login'],
            'days_open': days,
            'review_density': round(density, 2),
            'link': pr['html_url'],
            'title': pr['title'],
            'state': pr['state'],
        }
        
    def process_org(self, org: str, min_days: int = None) -> List[Dict]:
        """Process an entire GitHub organization.
        
        Args:
            org: Organization name
            min_days: Minimum days for stale filtering
            
        Returns:
            List of enriched PR data dicts
        """
        repos = self.fetch_repos(org)
        all_prs = []
        
        for repo in repos:
            prs = self.fetch_prs(repo)
            all_prs.extend(prs)
            
        # Filter stale PRs
        stale_prs = self.filter_stale_prs(all_prs, min_days)
        
        # Enrich with comment data
        enriched = []
        for pr in stale_prs:
            try:
                data = self.get_pr_data(pr)
                enriched.append(data)
            except Exception as e:
                print(f'⚠️  Error processing PR {pr.get("number")}: {e}')
                continue
                
        # Sort by days open descending
        enriched.sort(key=lambda x: x['days_open'], reverse=True)
        
        return enriched
        
    def close(self):
        """Close the session."""
        self.session.close()


# Convenience function
def get_pr_data_from_org(org: str, min_days: int = None) -> List[Dict]:
    """Get PR data for an organization.
    
    Args:
        org: Organization name
        min_days: Minimum days for stale filtering
        
    Returns:
        List of enriched PR data dicts
    """
    monitor = GitHubMonitor()
    try:
        return monitor.process_org(org, min_days)
    finally:
        monitor.close()
