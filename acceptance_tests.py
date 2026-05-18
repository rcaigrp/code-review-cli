import unittest
import os
import tempfile
from scanner import Scanner

class TestScanner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.scanner = Scanner(categories=['security', 'performance', 'style'])

    def test_criterion_1_cli_entry_point(self):
        # Verifies main.py accepts args and calls scanner/report
        import subprocess
        result = subprocess.run(['python', '/workspace/projects/Code-Review-CLI/main.py', '/workspace/projects/Code-Review-CLI'], capture_output=True, text=True)
        assert 'Code Review Report' in result.stdout

    def test_criterion_2_regex_patterns(self):
        with open(os.path.join(self.temp_dir, 'test.py'), 'w') as f:
            f.write('eval("test")')
        findings = self.scanner.scan_file(os.path.join(self.temp_dir, 'test.py'))
        assert any(f['category'] == 'security' for f in findings)

    def test_criterion_3_ast_parsing(self):
        code = "try:\n    pass\nexcept:\n    pass"
        with open(os.path.join(self.temp_dir, 'ast_test.py'), 'w') as f:
            f.write(code)
        findings = self.scanner.scan_file(os.path.join(self.temp_dir, 'ast_test.py'))
        assert any(f['category'] == 'security' and 'bare except' in f['message'].lower() for f in findings)

    def test_criterion_4_error_handling(self):
        with open(os.path.join(self.temp_dir, 'bad.py'), 'w') as f:
            f.write('def foo(\n')
        findings = self.scanner.scan_file(os.path.join(self.temp_dir, 'bad.py'))
        assert isinstance(findings, list)

    def test_criterion_5_edge_cases_empty_dir(self):
        findings = self.scanner.scan_directory(self.temp_dir)
        assert isinstance(findings, list)

if __name__ == '__main__':
    unittest.main()
