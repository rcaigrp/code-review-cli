import unittest
import subprocess
import tempfile
import os

class TestAcceptance(unittest.TestCase):
    def test_cli_arg_parsing(self):
        result = subprocess.run(['python', '/workspace/projects/Code-Review-CLI/main.py', '/tmp'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)

    def test_regex_ast_error_handling(self):
        temp_dir = tempfile.mkdtemp()
        with open(os.path.join(temp_dir, 'bad.py'), 'w') as f:
            f.write('def foo(unclosed')
        result = subprocess.run(['python', '/workspace/projects/Code-Review-CLI/main.py', temp_dir], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)

    def test_stdout_report_output(self):
        result = subprocess.run(['python', '/workspace/projects/Code-Review-CLI/main.py', '/tmp'], capture_output=True, text=True)
        self.assertIn('Code Review Report', result.stdout)

if __name__ == '__main__':
    unittest.main()
