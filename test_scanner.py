import unittest
import tempfile
import os
from scanner import Scanner


class TestScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = Scanner()
        self.temp_dir = tempfile.mkdtemp()

    def test_security_detection(self):
        filepath = os.path.join(self.temp_dir, 'test.py')
        with open(filepath, 'w') as f:
            f.write('query = "SELECT * FROM users"')
        findings = self.scanner.scan_file(filepath)
        security_findings = [f for f in findings if f['type'] == 'SECURITY']
        self.assertTrue(len(security_findings) > 0)

    def test_ast_import_detection(self):
        filepath = os.path.join(self.temp_dir, 'test.py')
        with open(filepath, 'w') as f:
            f.write('import os\nimport subprocess')
        findings = self.scanner.scan_file(filepath)
        perf_findings = [f for f in findings if f['type'] == 'PERFORMANCE']
        self.assertTrue(len(perf_findings) > 0)

    def test_syntax_error_handling(self):
        filepath = os.path.join(self.temp_dir, 'test.py')
        with open(filepath, 'w') as f:
            f.write('def foo(\n    print("bar")') # Syntax error
        findings = self.scanner.scan_file(filepath)
        self.assertIsInstance(findings, list)

if __name__ == '__main__':
    unittest.main()
