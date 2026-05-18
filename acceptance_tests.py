"""Acceptance tests for Org-Wide PR Aging & Review Velocity CLI."""

import unittest
import os
import sys
import responses
import json

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitor import GitHubMonitor
from report import render_report, get_age_color, format_density


class TestGitHubMonitor(unittest.TestCase):
    """Test GitHub monitor functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        os.environ['GITHUB_TOKEN'] = 'test-token'
        self.monitor = GitHubMonitor()
        
    def test_criterion_1_fetch_repos(self):
        """Test fetching repos for an organization."""
        with responses.RequestsMock() as rsps:
            # Mock repo endpoint
            url = 'https://api.github.com/orgs/test-org/repos'
            rsps.add(
                responses.GET,
                url,
                json=[{'name': 'repo1', 'owner': {'login': 'test-org'}}],
                status=200,
                headers={'X-RateLimit-Remaining': '100'}
            )
            
            repos = self.monitor.fetch_repos('test-org')
            self.assertEqual(len(repos), 1)
            self.assertEqual(repos[0]['name'], 'repo1')
            
    def test_criterion_1_fetch_prs_with_pagination(self):
        """Test fetching PRs with pagination."""
        with responses.RequestsMock() as rsps:
            # Mock PR endpoint
            url = 'https://api.github.com/repos/test-org/repo1/pulls'
            
            # First page
            rsps.add(
                responses.GET,
                url,
                json=[{'number': 1, 'created_at': '2024-01-01T00:00:00Z', 'user': {'login': 'user1'}, 'base': {'repo': {'owner': {'login': 'test-org'}, 'name': 'repo1'}}}],
                status=200,
                headers={'X-RateLimit-Remaining': '100'}
            )
            
            # Second page (empty to stop pagination)
            rsps.add(
                responses.GET,
                url,
                json=[],
                status=200,
                headers={'X-RateLimit-Remaining': '100'}
            )
            
            prs = self.monitor.fetch_prs({'name': 'repo1', 'owner': {'login': 'test-org'}})
            self.assertEqual(len(prs), 1)
            self.assertEqual(prs[0]['number'], 1)
            
    def test_criterion_2_filter_stale_prs(self):
        """Test filtering stale PRs."""
        # Create test PRs
        prs = [
            {'created_at': '2024-01-01T00:00:00Z', 'user': {'login': 'user1'}, 'base': {'repo': {'owner': {'login': 'test-org'}, 'name': 'repo1'}}},
            {'created_at': '2024-01-05T00:00:00Z', 'user': {'login': 'user2'}, 'base': {'repo': {'owner': {'login': 'test-org'}, 'name': 'repo1'}}},
        ]
        
        # Filter with 14 day threshold
        stale = self.monitor.filter_stale_prs(prs, min_days=14)
        self.assertEqual(len(stale), 2)  # Both should be > 14 days old
        
    def test_criterion_2_calculate_review_density(self):
        """Test review density calculation."""
        pr = {
            'created_at': '2024-01-01T00:00:00Z',
            'user': {'login': 'user1'},
            'base': {'repo': {'owner': {'login': 'test-org'}, 'name': 'repo1'}}
        }
        
        # Calculate density with 100 comments over 10 days
        days = self.monitor.calculate_days_open(pr)
        density = self.monitor.calculate_review_density(pr, 100)
        
        self.assertGreater(density, 0)
        self.assertAlmostEqual(density, 100 / days, places=2)
        
    def test_criterion_3_render_table(self):
        """Test table rendering with color coding."""
        data = [
            {'repo': 'test-org/repo1', 'pr_number': 1, 'author': 'user1', 'days_open': 5, 'review_density': 2.0, 'link': 'http://test.com'},
            {'repo': 'test-org/repo1', 'pr_number': 2, 'author': 'user2', 'days_open': 10, 'review_density': 1.0, 'link': 'http://test.com'},
            {'repo': 'test-org/repo1', 'pr_number': 3, 'author': 'user3', 'days_open': 20, 'review_density': 0.5, 'link': 'http://test.com'},
        ]
        
        # Test color coding
        self.assertEqual(get_age_color(5), 'green')
        self.assertEqual(get_age_color(10), 'yellow')
        self.assertEqual(get_age_color(20), 'red')
        
        # Test density formatting
        self.assertEqual(format_density(2.5), '2.50')
        
    def test_criterion_4_handle_empty_org(self):
        """Test handling empty organization."""
        with responses.RequestsMock() as rsps:
            # Mock empty org
            url = 'https://api.github.com/orgs/empty-org/repos'
            rsps.add(
                responses.GET,
                url,
                json=[],
                status=200,
                headers={'X-RateLimit-Remaining': '100'}
            )
            
            repos = self.monitor.fetch_repos('empty-org')
            self.assertEqual(len(repos), 0)
            
    def test_criterion_4_handle_rate_limit(self):
        """Test rate limit handling."""
        with responses.RequestsMock() as rsps:
            # Mock rate limit response
            url = 'https://api.github.com/orgs/test-org/repos'
            rsps.add(
                responses.GET,
                url,
                json=[],
                status=403,
                headers={'X-RateLimit-Remaining': '0'}
            )
            
            with self.assertRaises(Exception):
                self.monitor.fetch_repos('test-org')
                
    def test_criterion_5_mock_api_calls(self):
        """Test that API calls are properly mocked."""
        with responses.RequestsMock() as rsps:
            # Mock all necessary endpoints
            url = 'https://api.github.com/orgs/test-org/repos'
            rsps.add(
                responses.GET,
                url,
                json=[{'name': 'repo1', 'owner': {'login': 'test-org'}}],
                status=200,
                headers={'X-RateLimit-Remaining': '100'}
            )
            
            # Mock PR endpoint
            url = 'https://api.github.com/repos/test-org/repo1/pulls'
            rsps.add(
                responses.GET,
                url,
                json=[],
                status=200,
                headers={'X-RateLimit-Remaining': '100'}
            )
            
            # Process org
            data = self.monitor.process_org('test-org')
            self.assertEqual(len(data), 0)


class TestReportRendering(unittest.TestCase):
    """Test report rendering."""
    
    def test_criterion_3_render_format_density(self):
        """Test density formatting."""
        self.assertEqual(format_density(0), '0.00')
        self.assertEqual(format_density(1), '1.00')
        self.assertEqual(format_density(1.5), '1.50')


if __name__ == '__main__':
    unittest.main()
