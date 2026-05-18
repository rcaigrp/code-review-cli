import ast
import os
import re
from typing import List, Dict, Any

class Scanner:
    def __init__(self, categories: List[str] = None):
        self.categories = categories or ['security', 'performance', 'style']

    def scan_directory(self, directory: str) -> List[Dict[str, Any]]:
        issues = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.go', '.java')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            issues.extend(self.scan_file(filepath, content))
                    except Exception as e:
                        issues.append({
                            'file': filepath,
                            'line': 0,
                            'category': 'error',
                            'severity': 'critical',
                            'message': f'Could not read file: {e}',
                            'suggestion': 'Check file permissions or encoding.'
                        })
        return issues

    def scan_file(self, filepath: str, content: str) -> List[Dict[str, Any]]:
        issues = []
        issues.extend(self._regex_checks(filepath, content))
        issues.extend(self._ast_checks(filepath, content))
        return issues

    def _regex_checks(self, filepath: str, content: str) -> List[Dict[str, Any]]:
        issues = []
        for i, line in enumerate(content.split('\n'), 1):
            if re.search(r'\beval\(.*\)', line):
                issues.append({
                    'file': filepath,
                    'line': i,
                    'category': 'security',
                    'severity': 'high',
                    'message': 'Use of eval() detected.',
                    'suggestion': 'Use JSON parsing or safe alternatives.'
                })
            if re.search(r'\bassert\b', line):
                issues.append({
                    'file': filepath,
                    'line': i,
                    'category': 'style',
                    'severity': 'low',
                    'message': 'Use of assert detected.',
                    'suggestion': 'Use proper exception handling.'
                })
            if re.search(r'\[\s*.*\s*\]', line):
                issues.append({
                    'file': filepath,
                    'line': i,
                    'category': 'performance',
                    'severity': 'medium',
                    'message': 'List comprehension detected.',
                    'suggestion': 'Consider using generator expressions.'
                })
        return issues

    def _ast_checks(self, filepath: str, content: str) -> List[Dict[str, Any]]:
        issues = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id == 'print':
                        issues.append({
                            'file': filepath,
                            'line': node.lineno,
                            'category': 'style',
                            'severity': 'low',
                            'message': 'Use of print() detected.',
                            'suggestion': 'Use logging module for production code.'
                        })
                    elif node.func.id == 'eval':
                        issues.append({
                            'file': filepath,
                            'line': node.lineno,
                            'category': 'security',
                            'severity': 'high',
                            'message': 'AST detected use of eval().',
                            'suggestion': 'Use JSON parsing or safe alternatives.'
                        })
            elif isinstance(node, ast.For):
                issues.append({
                    'file': filepath,
                    'line': node.lineno,
                    'category': 'performance',
                    'severity': 'medium',
                    'message': 'Loop detected.',
                    'suggestion': 'Consider vectorized operations or map/reduce.'
                })
        return issues
