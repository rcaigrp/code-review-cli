import unittest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock
from scanner import Scanner, Issue
from report import print_report

class TestScanner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.scanner = Scanner(categories=['security', 'performance', 'style'])

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_scan_file_security_regex(self):
        filepath = os.path.join(self.temp_dir, 'test.py')
        with open(filepath, 'w') as f:
            f.write('eval("code")\n')
        
        issues = self.scanner.scan_file(filepath)
        self.assertTrue(len(issues) > 0)
        self.assertEqual(issues[0].category, 'security')

    def test_scan_file_style_regex(self):
        filepath = os.path.join(self.temp_dir, 'test.py')
        with open(filepath, 'w') as f:
            f.write('# TODO: fix this\n')
        
        issues = self.scanner.scan_file(filepath)
        self.assertTrue(len(issues) > 0)
        self.assertEqual(issues[0].category, 'style')

    def test_scan_file_syntax_error(self):
        filepath = os.path.join(self.temp_dir, 'bad.py')
        with open(filepath, 'w') as f:
            f.write('def foo(\n')
        
        issues = self.scanner.scan_file(filepath)
        self.assertEqual(len(issues), 0)

    def test_scan_directory(self):
        filepath = os.path.join(self.temp_dir, 'test.py')
        with open(filepath, 'w') as f:
            f.write('eval("code")\n')
        
        issues = self.scanner.scan_directory(self.temp_dir)
        self.assertTrue(len(issues) > 0)

    def test_scan_empty_directory(self):
        issues = self.scanner.scan_directory(self.temp_dir)
        self.assertEqual(len(issues), 0)

class TestReport(unittest.TestCase):
    @patch('builtins.print')
    def test_print_report(self, mock_print):
        issues = [Issue(file='test.py', line=1, category='security', severity='high', message='eval()', suggestion='Use literal_eval')]
        print_report(issues)
        mock_print.assert_called()

    @patch('builtins.print')
    def test_print_report_no_issues(self, mock_print):
        print_report([])
        mock_print.assert_called()

class TestCLI(unittest.TestCase):
    @patch('sys.argv', ['main.py', '/tmp/test_dir'])
    @patch('scanner.Scanner')
    @patch('report.print_report')
    def test_main_cli(self, mock_report, mock_scanner_class, mock_scanner):
        mock_scanner_class.return_value = mock_scanner
        mock_scanner.scan_directory.return_value = []
        
        from main import main
        main()
        
        mock_scanner_class.assert_called_once_with(categories=None)
        mock_scanner.scan_directory.assert_called_once_with('/tmp/test_dir')
        mock_report.assert_called_once_with([])

if __name__ == '__main__':
    unittest.main()
