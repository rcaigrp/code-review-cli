import os
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta

BASE_URL = "https://api.github.com"

def get_org_repos(org: str, token: str) -> List[Dict]:
    headers = {"Authorization": f"Bearer {token}"}
    repos = []
    url = f"{BASE_URL}/orgs/{org}/repos"
    page = 1
    while True:
        params = {"per_page": 100, "page": page}
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 403:
            wait = int(resp.headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {wait} seconds...")
            time.sleep(wait)
            continue
        if resp.status_code != 200:
            raise ValueError(f"Failed to fetch repos: {resp.status_code}")
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def get_prs_for_repo(repo: Dict, token: str) -> List[Dict]:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/repos/{repo['name']}/pulls"
    params = {"per_page": 100, "state": "open"}
    prs = []
    page = 1
    while True:
        resp = requests.get(url, headers=headers, params={**params, "page": page})
        if resp.status_code == 403:
            wait = int(resp.headers.get('Retry-After', 60))
            time.sleep(wait)
            continue
        if resp.status_code != 200:
            break
        data = resp.json()
        if not data:
            break
        prs.extend(data)
        page += 1
    return prs

def calculate_review_density(pr: Dict, token: str) -> float:
    url = f"{BASE_URL}/repos/{pr['base']['repo']['owner']['login']}/{pr['base']['repo']['name']}/pulls/{pr['number']}/comments"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 404:
            pr_comments = 0
        else:
            pr_comments = len(resp.json())
    except:
        pr_comments = 0
    
    issue_comments_url = f"{BASE_URL}/repos/{pr['base']['repo']['owner']['login']}/{pr['base']['repo']['name']}/issues/{pr['number']}/comments"
    resp = requests.get(issue_comments_url, headers=headers)
    issue_comments = len(resp.json()) if resp.status_code == 200 else 0
    
    total_comments = pr_comments + issue_comments
    
    updated_at = datetime.strptime(pr['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
    days_open = (datetime.now() - updated_at).days
    if days_open == 0:
        days_open = 1
    return total_comments / days_open

def fetch_pr_data(org: str, min_days_stale: int = 14) -> List[Dict]:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is not set")
    
    repos = get_org_repos(org, token)
    pr_data = []
    
    for repo in repos:
        prs = get_prs_for_repo(repo, token)
        for pr in prs:
            updated_at = datetime.strptime(pr['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
            days_open = (datetime.now() - updated_at).days
            if days_open > min_days_stale:
                density = calculate_review_density(pr, token)
                pr_data.append({
                    "repo": repo['name'],
                    "pr_number": pr['number'],
                    "author": pr['user']['login'],
                    "days_open": days_open,
                    "review_density": round(density, 2),
                    "link": pr['html_url']
                })
    return pr_data
