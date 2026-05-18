import ast
import os
import re
from typing import List, Dict, Any, Optional

PATTERNS = {
    'security': [
        (r'\beval\(', 'Use of eval() detected'),
        (r'\bexec\(', 'Use of exec() detected'),
    ],
    'performance': [
        (r'\bimport\s+\w+', 'Import statement detected'),
        (r'\.append\(', 'List append method detected'),
    ],
    'style': [
        (r'\bprint\(', 'Use of print() detected'),
        (r'\bassert\s+.*$', 'Assertion without message'),
    ]
}

def analyze_ast(tree: ast.AST, filepath: str) -> List[Dict[str, Any]]:
    issues = []
    if isinstance(tree, ast.Module):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for subnode in ast.walk(node):
                    if isinstance(subnode, (ast.Import, ast.ImportFrom)):
                        issues.append({
                            'file': filepath,
                            'line': subnode.lineno,
                            'type': 'performance',
                            'severity': 'Medium',
                            'message': 'Import inside function',
                            'suggestion': 'Move imports to module level'
                        })
    return issues

def scan_directory(directory: str, severity_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    issues = []
    exts = ('.py', '.js', '.ts')
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(exts):
                filepath = os.path.join(root, f)
                try:
                    with open(filepath, 'r') as fh:
                        content = fh.read()
                    for issue_type, patterns in PATTERNS.items():
                        for pattern, msg in patterns:
                            for match in re.finditer(pattern, content):
                                line_no = content[:match.start()].count('\n') + 1
                                issues.append({
                                    'file': filepath,
                                    'line': line_no,
                                    'type': issue_type,
                                    'severity': 'High' if issue_type == 'security' else ('Medium' if issue_type == 'performance' else 'Low'),
                                    'message': msg,
                                    'suggestion': f'Consider refactoring: {msg}'
                                })
                    try:
                        tree = ast.parse(content)
                        ast_issues = analyze_ast(tree, filepath)
                        issues.extend(ast_issues)
                    except SyntaxError:
                        issues.append({
                            'file': filepath,
                            'line': 0,
                            'type': 'style',
                            'severity': 'Low',
                            'message': 'Syntax error in file',
                            'suggestion': 'Fix syntax errors before scanning'
                        })
                except Exception:
                    pass
                if severity_filter:
                    issues = [i for i in issues if i.get('severity') == severity_filter]
    return issues
