import ast
import os
import re

SECURITY_PATTERNS = [
    (r"os\.system\(", "High", "Use of os.system() is a security risk"),
    (r"subprocess\.call\(", "High", "Use of subprocess.call() is a security risk"),
    (r"eval\(", "High", "Use of eval() is a security risk"),
    (r"exec\(", "Medium", "Use of exec() is a security risk"),
]

PERFORMANCE_PATTERNS = [
    (r"for\s+in\s+range\(\s*len\(", "Medium", "Iterating by index instead of enumerate()"),
    (r"import\s+re\s*$", "Low", "Consider using string methods instead of regex"),
]

STYLE_PATTERNS = [
    (r"^\s*#.*$", "Info", "Comment without docstring"),
    (r"^def\s+\w+\([^)]*\):$", "Low", "Function with no parameters"),
]

def scan_file(filepath, categories):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except Exception:
        return []

    issues = []
    try:
        tree = ast.parse(content)
    except SyntaxError:
        issues.append({'file': filepath, 'line': 0, 'severity': 'Info', 'message': 'Syntax error in file', 'category': 'security'})
        return issues

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'eval':
                if 'security' in categories:
                    issues.append({'file': filepath, 'line': node.lineno, 'severity': 'High', 'message': 'Use of eval() is a security risk', 'category': 'security'})
            if isinstance(node.func, ast.Name) and node.func.id == 'exec':
                if 'security' in categories:
                    issues.append({'file': filepath, 'line': node.lineno, 'severity': 'Medium', 'message': 'Use of exec() is a security risk', 'category': 'security'})
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == 'system':
                    if 'security' in categories:
                        issues.append({'file': filepath, 'line': node.lineno, 'severity': 'High', 'message': 'Use of os.system() is a security risk', 'category': 'security'})
                if node.func.attr == 'call':
                    if 'security' in categories:
                        issues.append({'file': filepath, 'line': node.lineno, 'severity': 'High', 'message': 'Use of subprocess.call() is a security risk', 'category': 'security'})

    lines = content.split('\n')
    for cat, patterns in [('security', SECURITY_PATTERNS), ('performance', PERFORMANCE_PATTERNS), ('style', STYLE_PATTERNS)]:
        if cat in categories:
            for pattern, severity, msg in patterns:
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        issues.append({'file': filepath, 'line': i, 'severity': severity, 'message': msg, 'category': cat})
    return issues

def scan_directory(dirpath, categories):
    issues = []
    for root, _, files in os.walk(dirpath):
        for f in files:
            if f.endswith('.py'):
                filepath = os.path.join(root, f)
                issues.extend(scan_file(filepath, categories))
    return issues