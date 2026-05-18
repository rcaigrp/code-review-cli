import os
import re
import ast
from typing import List, Dict


class Scanner:
    def __init__(self):
        self.security_patterns = {
            'sql_injection': re.compile(r'["\'].*(%s|SELECT|INSERT|UPDATE|DELETE|DROP|EXEC).*["\']'),
            'xss': re.compile(r'["\'].*<(script|img|iframe).*["\']'),
            'hardcoded_secret': re.compile(r'(?:password|secret|api_key|token)\s*=\s*["\'][^"\']{5,}["\']')
        }
        self.performance_patterns = {
            'subprocess_import': re.compile(r'import\s+subprocess'),
            'os_import': re.compile(r'import\s+os'),
            'string_concat': re.compile(r'\w+\s*\+\s*["\']')
        }
        self.style_patterns = {
            'long_line': re.compile(r'^.{80,}$'),
            'missing_docstring': None # Handled via AST
        }

    def scan_file(self, filepath: str) -> List[Dict]:
        findings = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
                for i, line in enumerate(lines, 1):
                    for pattern_name, pattern in self.security_patterns.items():
                        if pattern.search(line):
                            findings.append({'file': filepath, 'line': i, 'type': 'SECURITY', 'severity': 'HIGH', 'pattern': pattern_name})
                    for pattern_name, pattern in self.performance_patterns.items():
                        if pattern.search(line):
                            findings.append({'file': filepath, 'line': i, 'type': 'PERFORMANCE', 'severity': 'MEDIUM', 'pattern': pattern_name})
                    if self.style_patterns['long_line'].search(line):
                        findings.append({'file': filepath, 'line': i, 'type': 'STYLE', 'severity': 'LOW', 'pattern': 'long_line'})
            
            # AST Parsing
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name == 'os' or alias.name == 'subprocess':
                                line_num = node.lineno
                                findings.append({'file': filepath, 'line': line_num, 'type': 'PERFORMANCE', 'severity': 'MEDIUM', 'pattern': f'import_{alias.name}'})
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if not ast.get_docstring(node):
                            findings.append({'file': filepath, 'line': node.lineno, 'type': 'STYLE', 'severity': 'LOW', 'pattern': 'missing_docstring'})
            except SyntaxError:
                pass
        except Exception:
            pass
        return findings

    def scan_directory(self, path: str) -> List[Dict]:
        findings = []
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith('.py'):
                    full_path = os.path.join(root, f)
                    findings.extend(self.scan_file(full_path))
        return findings
