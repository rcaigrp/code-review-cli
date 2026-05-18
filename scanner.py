import ast
import re
import os
from typing import List, Dict, Any

SECURITY_PATTERNS = [
    (re.compile(r'\beval\((.*)\)'), 'Use of eval() detected - potential code injection risk.'),
    (re.compile(r'\bexec\((.*)\)'), 'Use of exec() detected - potential code injection risk.'),
    (re.compile(r'\bpickle\.loads\((.*)\)'), 'Use of pickle.loads() detected - potential deserialization attack.'),
]

PERFORMANCE_PATTERNS = [
    (re.compile(r'\bfor\s+.*\s+in\s+range\(len\(.*\))'), 'Consider using enumerate() instead of indexing in a loop over range(len(...)).'),
]

STYLE_PATTERNS = [
    (re.compile(r'^#\s*$', re.MULTILINE), 'Empty comment line detected.'),
]

def scan_file(filepath: str, categories: List[str]) -> List[Dict[str, Any]]:
    findings = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception:
        return []
    
    # AST parsing for syntax errors
    try:
        ast.parse(code)
    except SyntaxError:
        findings.append({
            'file': filepath,
            'category': 'style',
            'severity': 'MEDIUM',
            'line': 0,
            'message': 'Syntax error detected - file cannot be parsed.'
        })
    
    for category in categories:
        patterns = {'security': SECURITY_PATTERNS, 'performance': PERFORMANCE_PATTERNS, 'style': STYLE_PATTERNS}
        for pattern, message in patterns.get(category, []):
            for match in pattern.finditer(code):
                line_num = code[:match.start()].count('\n') + 1
                findings.append({
                    'file': filepath,
                    'category': category,
                    'severity': 'HIGH' if category == 'security' else ('MEDIUM' if category == 'performance' else 'LOW'),
                    'line': line_num,
                    'message': message
                })
    return findings

def scan_directory(dirpath: str, categories: List[str]) -> List[Dict[str, Any]]:
    all_findings = []
    for root, _, files in os.walk(dirpath):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                all_findings.extend(scan_file(filepath, categories))
    return all_findings
