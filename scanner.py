import os
import re
import ast
from typing import List, Dict, Optional

SECURITY_PATTERNS = [
    (r'eval\(', 'eval() call'),
    (r'exec\(', 'exec() call'),
    (r'pickle\.load', 'pickle.load() call'),
]

PERFORMANCE_PATTERNS = [
    (r'\.append\(.*\)', 'List append in loop'),
    (r'list\(.*\)', 'list() conversion'),
]

STYLE_PATTERNS = [
    (r'^#\s*$', 'Empty comment'),
    (r'^#.*$', 'Comment without code'),
]

def scan_file(filepath: str, categories: Optional[List[str]] = None) -> List[Dict]:
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            ast.parse(content)
        except SyntaxError:
            issues.append({
                'file': filepath,
                'category': 'style',
                'severity': 'high',
                'issue': 'SyntaxError: Invalid Python syntax',
                'line': 0
            })
        
        if categories is None:
            categories = ['security', 'performance', 'style']
            
        for cat in categories:
            if cat == 'security':
                patterns = SECURITY_PATTERNS
            elif cat == 'performance':
                patterns = PERFORMANCE_PATTERNS
            elif cat == 'style':
                patterns = STYLE_PATTERNS
            else:
                continue
                
            for pattern, desc in patterns:
                for i, line in enumerate(content.splitlines(), 1):
                    if re.search(pattern, line):
                        issues.append({
                            'file': filepath,
                            'category': cat,
                            'severity': 'high' if cat == 'security' else 'medium',
                            'issue': desc,
                            'line': i
                        })
    except Exception as e:
        issues.append({
            'file': filepath,
            'category': 'style',
            'severity': 'low',
            'issue': f'Error reading file: {str(e)}',
            'line': 0
        })
    return issues

def scan_directory(dir_path: str, categories: Optional[List[str]] = None) -> List[Dict]:
    all_issues = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                issues = scan_file(filepath, categories)
                all_issues.extend(issues)
    return all_issues
