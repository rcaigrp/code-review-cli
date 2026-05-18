import unittest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestCodeReviewCLI(unittest.TestCase):
    def test_criterion_1_cli_entry_point(self):
        from main import main
        with patch('sys.argv', ['main.py', '/tmp/test_dir']):
            with patch('scanner.scan_directory') as mock_scan:
                mock_scan.return_value = []
                with patch('report.generate_report'):
                    main()
                mock_scan.assert_called_once_with('/tmp/test_dir', ['security', 'performance', 'style'])

    def test_criterion_2_scanner_regex_ast(self):
        from scanner import scan_directory
        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [('/tmp', [], ['test.py'])]
            mock_file = MagicMock()
            mock_file.read.return_value = "import os\nos.system('rm -rf /')\n"
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=None)
            with patch('builtins.open', MagicMock(return_value=mock_file)):
                issues = scan_directory('/tmp', ['security'])
                assert len(issues) > 0
                assert any(i['category'] == 'security' for i in issues)

    def test_criterion_3_report_module(self):
        from report import generate_report
        issues = [{'file': 'test.py', 'line': 1, 'severity': 'High', 'message': 'Test'}]
        with patch('sys.stdout', MagicMock()) as mock_stdout:
            generate_report(issues)
            mock_stdout.write.assert_called()

    def test_criterion_4_scanner_error_handling(self):
        from scanner import scan_directory
        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [('/tmp', [], ['bad.py'])]
            mock_file = MagicMock()
            mock_file.read.return_value = "def bad(\n" # Syntax error
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=None)
            with patch('builtins.open', MagicMock(return_value=mock_file)):
                issues = scan_directory('/tmp', ['security'])
                assert len(issues) > 0
                assert any(i['severity'] == 'Info' for i in issues)

    def test_criterion_5_edge_cases(self):
        from scanner import scan_directory
        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [] # Empty dir
            issues = scan_directory('/tmp', ['security'])
            assert issues == []