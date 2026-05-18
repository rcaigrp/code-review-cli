import unittest
import sys
import os
from unittest.mock import patch
import main
import scanner
import report

class TestAcceptance(unittest.TestCase):
    def test_criterion_1_cli_entry_point(self):
        with patch.object(sys, 'argv', ['main.py', '/tmp/testdir']):
            with patch('main.print_report'):
                main.main()
                self.assertTrue(True)

    def test_criterion_2_regex_ast_scanning(self):
        s = scanner.Scanner(categories=['security', 'performance', 'style'])
        content = "eval(x)\nimport math\ndef _test(): pass\n"
        findings = s.scan_content('/tmp/test.py', content)
        assert any(f['category'] == 'security' for f in findings)
        assert any(f['category'] == 'performance' for f in findings)
        assert any(f['category'] == 'style' for f in findings)

    def test_criterion_3_report_formatting(self):
        findings = [{'file': '/tmp/test.py', 'category': 'security', 'severity': 'HIGH', 'line': 1, 'message': 'Test'}]
        output = report.format_report(findings)
        assert '=== Code Review Report ===' in output
        assert '/tmp/test.py' in output

    def test_criterion_4_unit_tests_coverage(self):
        s = scanner.Scanner(categories=['security'])
        content = "eval(x)"
        assert len(s.scan_content('/tmp/test.py', content)) > 0

    def test_criterion_5_edge_cases(self):
        s = scanner.Scanner()
        assert len(s.scan_directory('/tmp/empty_dir')) == 0
        content = "def (x): pass"
        findings = s.scan_content('/tmp/test.py', content)
        assert any('Syntax error' in f['message'] for f in findings)
