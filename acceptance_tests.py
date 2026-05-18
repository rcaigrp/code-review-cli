import unittest
import responses
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import monitor

class TestAcceptanceCriteria(unittest.TestCase):
    @responses.activate
    def test_criterion_1_fetch_repos(self):
        token = "mock"
        os.environ["GITHUB_TOKEN"] = token
        
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos?per_page=100&page=1",
            json=[{"name": "repo1", "owner": {"login": "test-org"}}],
            status=200
        )
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos?per_page=100&page=2",
            json=[],
            status=200
        )
        
        responses.add(
            responses.GET,
            "https://api.github.com/repos/repo1/pulls?per_page=100&state=open&page=1",
            json=[{"number": 1, "updated_at": "2023-01-01T00:00:00Z", "user": {"login": "user1"}, "base": {"repo": {"name": "repo1", "owner": {"login": "test-org"}}}}],
            status=200
        )
        responses.add(
            responses.GET,
            "https://api.github.com/repos/repo1/pulls?per_page=100&state=open&page=2",
            json=[],
            status=200
        )
        
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/pulls/1/comments",
            json=[],
            status=200
        )
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/issues/1/comments",
            json=[],
            status=200
        )
        
        data = monitor.fetch_pr_data("test-org", 14)
        assert len(data) == 1
        assert data[0]['repo'] == 'repo1'

    @responses.activate
    def test_criterion_2_filter_stale(self):
        token = "mock"
        os.environ["GITHUB_TOKEN"] = token
        
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos?per_page=100&page=1",
            json=[{"name": "repo1", "owner": {"login": "test-org"}}],
            status=200
        )
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos?per_page=100&page=2",
            json=[],
            status=200
        )
        
        responses.add(
            responses.GET,
            "https://api.github.com/repos/repo1/pulls?per_page=100&state=open&page=1",
            json=[{"number": 1, "updated_at": "2023-01-01T00:00:00Z", "user": {"login": "user1"}, "base": {"repo": {"name": "repo1", "owner": {"login": "test-org"}}}}],
            status=200
        )
        responses.add(
            responses.GET,
            "https://api.github.com/repos/repo1/pulls?per_page=100&state=open&page=2",
            json=[],
            status=200
        )
        
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/pulls/1/comments",
            json=[],
            status=200
        )
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/issues/1/comments",
            json=[],
            status=200
        )
        
        data = monitor.fetch_pr_data("test-org", 14)
        assert len(data) == 1
        assert data[0]['days_open'] > 14

    @responses.activate
    def test_criterion_3_density_calculation(self):
        token = "mock"
        os.environ["GITHUB_TOKEN"] = token
        
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos?per_page=100&page=1",
            json=[{"name": "repo1", "owner": {"login": "test-org"}}],
            status=200
        )
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos?per_page=100&page=2",
            json=[],
            status=200
        )
        
        responses.add(
            responses.GET,
            "https://api.github.com/repos/repo1/pulls?per_page=100&state=open&page=1",
            json=[{"number": 1, "updated_at": "2023-01-01T00:00:00Z", "user": {"login": "user1"}, "base": {"repo": {"name": "repo1", "owner": {"login": "test-org"}}}}],
            status=200
        )
        responses.add(
            responses.GET,
            "https://api.github.com/repos/repo1/pulls?per_page=100&state=open&page=2",
            json=[],
            status=200
        )
        
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/pulls/1/comments",
            json=[{"id": 1}],
            status=200
        )
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test-org/repo1/issues/1/comments",
            json=[{"id": 2}],
            status=200
        )
        
        data = monitor.fetch_pr_data("test-org", 14)
        assert len(data) == 1
        assert data[0]['review_density'] > 0

    @responses.activate
    def test_criterion_4_edge_cases(self):
        token = "mock"
        os.environ["GITHUB_TOKEN"] = token
        
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos?per_page=100&page=1",
            json=[],
            status=200
        )
        
        data = monitor.fetch_pr_data("test-org", 14)
        assert len(data) == 0

    @responses.activate
    def test_criterion_5_rate_limits(self):
        token = "mock"
        os.environ["GITHUB_TOKEN"] = token
        
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos?per_page=100&page=1",
            json=[{"name": "repo1", "owner": {"login": "test-org"}}],
            status=200
        )
        responses.add(
            responses.GET,
            "https://api.github.com/orgs/test-org/repos?per_page=100&page=2",
            json=[],
            status=200
        )
        
        responses.add(
            responses.GET,
            "https://api.github.com/repos/repo1/pulls?per_page=100&state=open&page=1",
            json=[],
            status=200
        )
        responses.add(
            responses.GET,
            "https://api.github.com/repos/repo1/pulls?per_page=100&state=open&page=2",
            json=[],
            status=200
        )

        data = monitor.fetch_pr_data("test-org", 14)
        assert len(data) == 0
