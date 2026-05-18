import os
import time
import requests
import datetime
from typing import List, Dict, Any, Optional

class GitHubMonitor:
    def __init__(self, token: str, org: str):
        self.token = token
        self.org = org
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {token}'})
        
    def fetch_repos(self) -> List[Dict[str, Any]]:
        repos = []
        url = f'https://api.github.com/orgs/{self.org}/repos'
        while True:
            resp = self.session.get(url)
            if resp.status_code == 404:
                return []
            if resp.status_code == 403:
                rate_limit = resp.headers.get('X-RateLimit-Remaining')
                if rate_limit and int(rate_limit) == 0:
                    reset = int(resp.headers.get('X-RateLimit-Reset', 0))
                    wait = max(0, reset - int(time.time()))
                    print(f"Rate limited. Waiting {wait} seconds...")
                    time.sleep(wait)
                    continue
            data = resp.json()
            if not data:
                break
            repos.extend(data)
            url = resp.links.get('next', {}).get('url')
            if not url:
                break
        return repos

    def fetch_prs(self, repo: Dict[str, Any]) -> List[Dict[str, Any]]:
        prs = []
        url = f"https://api.github.com/repos/{repo['full_name']}/pulls"
        while True:
            resp = self.session.get(url, params={'per_page': 100})
            if resp.status_code == 403:
                time.sleep(10)
                continue
            data = resp.json()
            if not data:
                break
            prs.extend(data)
            url = resp.links.get('next', {}).get('url')
            if not url:
                break
        return prs
