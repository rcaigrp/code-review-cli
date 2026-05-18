import ast
import re
import os
from typing import List, Dict, Any

class Scanner:
    def __init__(self, categories=None):
        self.categories = categories or ['security', 'performance', 'style']

    def scan_file(self, filepath: str) -> List[Dict[str, Any]]:
        findings = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            
            for cat in self.categories:
                if cat == 'security':
                    for pattern in [r'\beval\s*\(', r'\bexec\s*\(', r'\bsubprocess\.\w+\s*\(']:
                        for match in re.finditer(pattern, code):
                            line_num = code[:match.start()].count('\n') + 1
                            findings.append({'file': filepath, 'line': line_num, 'category': cat, 'severity': 'HIGH', 'message': f"Found security issue: {match.group()}"})
                elif cat == 'performance':
                    for pattern in [r'import\s+.*', r'while\s+True:']:
                        for match in re.finditer(pattern, code):
                            line_num = code[:match.start()].count('\n') + 1
                            findings.append({'file': filepath, 'line': line_num, 'category': cat, 'severity': 'MEDIUM', 'message': f"Found performance issue: {match.group()}"})
                elif cat == 'style':
                    for pattern in [r'#.*TODO', r'#.*FIXME', r'print\(\s*.*\s*\)\s*$']:
                        for match in re.finditer(pattern, code):
                            line_num = code[:match.start()].count('\n') + 1
                            findings.append({'file': filepath, 'line': line_num, 'category': cat, 'severity': 'LOW', 'message': f"Found style issue: {match.group()}"})
            
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Try):
                        for handler in node.handlers:
                            if handler.type is None:
                                findings.append({'file': filepath, 'line': node.lineno, 'category': 'security', 'severity': 'HIGH', 'message': 'Found bare except block'})
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'print':
                        found_in_loop = False
                        for parent in ast.walk(tree):
                            if isinstance(parent, (ast.For, ast.While)):
                                for child in ast.walk(parent):
                                    if child is node:
                                        found_in_loop = True
                                        break
                                if found_in_loop:
                                    break
                        if found_in_loop:
                            findings.append({'file': filepath, 'line': node.lineno, 'category': 'performance', 'severity': 'MEDIUM', 'message': 'Found print() inside loop'})
                        else:
                            findings.append({'file': filepath, 'line': node.lineno, 'category': 'style', 'severity': 'LOW', 'message': 'Found print() statement'})
            except SyntaxError:
                pass
        except Exception as e:
            findings.append({'file': filepath, 'line': 0, 'category': 'error', 'severity': 'CRITICAL', 'message': f'Could not scan file: {e}'})
        return findings

    def scan_directory(self, dirpath: str) -> List[Dict[str, Any]]:
        all_findings = []
        if not os.path.isdir(dirpath):
            return all_findings
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                if file.endswith(('.py', '.js', '.ts')):
                    filepath = os.path.join(root, file)
                    all_findings.extend(self.scan_file(filepath))
        return all_findings
