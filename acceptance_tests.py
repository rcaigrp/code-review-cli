import unittest
import responses
import datetime
import time
import os
from unittest.mock import patch
from monitor import GitHubMonitor
from report import render_table
from main import main

class TestGitHubMonitor(unittest.TestCase):
    @responses.activate
    @patch('time.sleep')
    def test_fetch_repos_pagination(self, mock_sleep):
        monitor = GitHubMonitor('token', 'test-org')
        responses.add(responses.GET, 'https://api.github.com/orgs/test-org/repos', json=[{'full_name': 'test-org/repo1'}], status=200)
        responses.add(responses.GET, 'https://api.github.com/orgs/test-org/repos', json=[], status=200)
        repos = monitor.fetch_repos()
        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0]['full_name'], 'test-org/repo1')

    @responses.activate
    @patch('time.sleep')
    def test_fetch_prs_pagination(self, mock_sleep):
        monitor = GitHubMonitor('token', 'test-org')
        repo = {'full_name': 'test-org/repo1'}
        responses.add(responses.GET, 'https://api.github.com/repos/test-org/repo1/pulls', json=[{'number': 1, 'comments': 2, 'updated_at': '2023-01-01T00:00:00Z', 'user': {'login': 'user1'}, 'html_url': 'http://test.com'}], status=200)
        responses.add(responses.GET, 'https://api.github.com/repos/test-org/repo1/pulls', json=[], status=200)
        prs = monitor.fetch_prs(repo)
        self.assertEqual(len(prs), 1)

    @responses.activate
    @patch('time.sleep')
    def test_rate_limit_handling(self, mock_sleep):
        monitor = GitHubMonitor('token', 'test-org')
        responses.add(responses.GET, 'https://api.github.com/orgs/test-org/repos', json=[], status=403, headers={'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset': '1700000000'})
        repos = monitor.fetch_repos()
        self.assertEqual(repos, [])

    @responses.activate
    @patch('time.sleep')
    def test_empty_org(self, mock_sleep):
        monitor = GitHubMonitor('token', 'test-org')
        responses.add(responses.GET, 'https://api.github.com/orgs/test-org/repos', json=[], status=200)
        repos = monitor.fetch_repos()
        self.assertEqual(repos, [])

class TestMainLogic(unittest.TestCase):
    @responses.activate
    @patch('time.sleep')
    def test_stale_filtering(self, mock_sleep):
        monitor = GitHubMonitor('token', 'test-org')
        repo = {'full_name': 'test-org/repo1'}
        old_pr = {'number': 1, 'comments': 5, 'updated_at': '2023-01-01T00:00:00Z', 'user': {'login': 'user1'}, 'html_url': 'http://test.com'}
        responses.add(responses.GET, 'https://api.github.com/repos/test-org/repo1/pulls', json=[old_pr], status=200)
        responses.add(responses.GET, 'https://api.github.com/repos/test-org/repo1/pulls', json=[], status=200)
        prs = monitor.fetch_prs(repo)
        self.assertEqual(len(prs), 1)

    @patch('os.environ')
    def test_missing_token(self, mock_env):
        mock_env.get.return_value = None
        main()

class TestReport(unittest.TestCase):
    def test_render_table(self):
        data = [
            {'repo': 'r1', 'pr_number': 1, 'author': 'u1', 'days_open': 10, 'review_density': 0.5, 'url': 'http://x.com'}
        ]
        render_table(data)

if __name__ == '__main__':
    unittest.main()
