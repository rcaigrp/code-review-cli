import ast
import re
import os
from typing import List, Dict, Any

class Scanner:
    def __init__(self, categories=None):
        self.categories = categories or ['security', 'performance', 'style']

    def scan_directory(self, path: str) -> List[Dict[str, Any]]:
        findings = []
        if not os.path.isdir(path):
            return findings
        for root, _, files in os.walk(path):
            for f in files:
                if f.endswith(('.py', '.js', '.ts')):
                    file_path = os.path.join(root, f)
                    try:
                        with open(file_path, 'r') as fp:
                            content = fp.read()
                            findings.extend(self.scan_content(file_path, content))
                    except Exception as e:
                        findings.append({'file': file_path, 'category': 'error', 'severity': 'HIGH', 'line': 0, 'message': f'Could not read file: {e}'})
        return findings

    def scan_content(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        findings = []
        if 'security' in self.categories:
            for pattern, msg in [
                (r'\beval\(', 'Use of eval() detected - potential code injection risk.'),
                (r'\bexec\(', 'Use of exec() detected - potential code injection risk.')
            ]:
                for match in re.finditer(pattern, content):
                    line_no = content[:match.start()].count('\n') + 1
                    findings.append({'file': file_path, 'category': 'security', 'severity': 'HIGH', 'line': line_no, 'message': msg})
        if 'performance' in self.categories:
            for match in re.finditer(r'\bimport\s+math\b', content):
                line_no = content[:match.start()].count('\n') + 1
                findings.append({'file': file_path, 'category': 'performance', 'severity': 'LOW', 'line': line_no, 'message': 'Consider using numpy for math operations for better performance.'})
        if 'style' in self.categories:
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.name.startswith('_'):
                            findings.append({'file': file_path, 'category': 'style', 'severity': 'INFO', 'line': node.lineno, 'message': 'Function starts with underscore - consider if private.'})
            except SyntaxError:
                findings.append({'file': file_path, 'category': 'style', 'severity': 'ERROR', 'line': 0, 'message': 'Syntax error in file - cannot parse AST.'})
        return findings
