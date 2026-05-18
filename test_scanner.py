import unittest
import os
import tempfile
from scanner import Scanner

class TestScanner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.scanner = Scanner()

    def test_regex_eval(self):
        filepath = os.path.join(self.temp_dir, 'test.py')
        with open(filepath, 'w') as f:
            f.write('x = eval("1+1")')
        issues = self.scanner.scan_file(filepath, 'x = eval("1+1")')
        assert any(i['category'] == 'security' and 'eval' in i['message'] for i in issues)

    def test_ast_print(self):
        filepath = os.path.join(self.temp_dir, 'test.py')
        content = 'print("hello")'
        issues = self.scanner.scan_file(filepath, content)
        assert any(i['category'] == 'style' and 'print' in i['message'] for i in issues)

    def test_syntax_error_handling(self):
        filepath = os.path.join(self.temp_dir, 'test.py')
        content = 'def foo(unclosed'
        issues = self.scanner.scan_file(filepath, content)
        assert isinstance(issues, list)

    def test_empty_directory(self):
        issues = self.scanner.scan_directory(self.temp_dir)
        assert issues == []

if __name__ == '__main__':
    unittest.main()
