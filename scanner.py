import os
import re
import ast

SECURITY_PATTERNS = {
    "eval": re.compile(r'\beval\s*\('),
    "exec": re.compile(r'\bexec\s*\('),
    "os_system": re.compile(r'os\.system\s*\('),
}

PERFORMANCE_PATTERNS = {
    "star_import": re.compile(r'from\s+\w+\s+import\s+\*'),
    "long_line": re.compile(r'^.{100,}$', re.MULTILINE),
}

STYLE_PATTERNS = {
    "print_statement": re.compile(r'\bprint\s*\('),
}

def scan_file(file_path: str, categories: list = None) -> list:
    """Scan a single file for issues."""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return [{"type": "error", "name": "read_error", "file": file_path, "error": str(e)}]

    categories = categories or ["security", "performance", "style"]

    # Regex checks
    if "security" in categories:
        for name, pattern in SECURITY_PATTERNS.items():
            if pattern.search(content):
                issues.append({"type": "security", "name": name, "file": file_path})

    if "performance" in categories:
        for name, pattern in PERFORMANCE_PATTERNS.items():
            if pattern.search(content):
                issues.append({"type": "performance", "name": name, "file": file_path})

    if "style" in categories:
        style_check = STYLE_PATTERNS["print_statement"]
        if style_check.search(content):
            issues.append({"type": "style", "name": "print_statement", "file": file_path})

    # AST checks
    if "security" in categories or "performance" in categories or "style" in categories:
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        issues.append({"type": "security", "name": "bare_except", "file": file_path, "line": node.lineno})
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == 'print':
                        issues.append({"type": "style", "name": "print_statement_ast", "file": file_path, "line": node.lineno})
        except SyntaxError:
            issues.append({"type": "error", "name": "syntax_error", "file": file_path})

    return issues
