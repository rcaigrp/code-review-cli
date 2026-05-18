import unittest
import os
import tempfile
from scanner import scan_file

class TestScanner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_empty_file(self):
        file_path = os.path.join(self.temp_dir, "empty.py")
        with open(file_path, 'w') as f:
            f.write("")
        issues = scan_file(file_path)
        self.assertEqual(len(issues), 0)

    def test_security_issue(self):
        file_path = os.path.join(self.temp_dir, "security.py")
        with open(file_path, 'w') as f:
            f.write("eval('test')")
        issues = scan_file(file_path)
        self.assertTrue(any(i.get("name") == "eval" for i in issues))

    def test_bare_except(self):
        file_path = os.path.join(self.temp_dir, "bare.py")
        with open(file_path, 'w') as f:
            f.write("try:\n    pass\nexcept:\n    pass")
        issues = scan_file(file_path)
        self.assertTrue(any(i.get("name") == "bare_except" for i in issues))

    def test_syntax_error(self):
        file_path = os.path.join(self.temp_dir, "bad.py")
        with open(file_path, 'w') as f:
            f.write("def foo(\n    pass")
        issues = scan_file(file_path)
        self.assertTrue(any(i.get("type") == "error" for i in issues))

    def test_print_statement(self):
        file_path = os.path.join(self.temp_dir, "print.py")
        with open(file_path, 'w') as f:
            f.write("print('hello')")
        issues = scan_file(file_path)
        self.assertTrue(any(i.get("name") == "print_statement" for i in issues))

if __name__ == "__main__":
    unittest.main()
