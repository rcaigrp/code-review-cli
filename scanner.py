import ast
import os
import re
from typing import List, Dict

SECURITY_PATTERNS = [
    (r"eval\(", "Use of eval() detected - potential code injection risk."),
    (r"exec\(", "Use of exec() detected - potential code injection risk."),
    (r"pickle\.loads\(", "Use of pickle.loads() - potential deserialization vulnerability."),
    (r"subprocess\.call\(", "Use of subprocess.call() - consider using subprocess.run() for better security."),
]

PERFORMANCE_PATTERNS = [
    (r"for\s+_\s+in\s+range\(.*\):", "Inefficient loop using range() without optimization."),
    (r"\.count\(.*\)", "Use of str.count() in a loop may be inefficient."),
    (r"import\s+json", "Consider lazy loading or caching for json imports."),
]

STYLE_PATTERNS = [
    (r"^\s*TODO", "TODO found - consider addressing."),
    (r"^\s*FIXME", "FIXME found - consider addressing."),
    (r"^\s*assert\s+False", "Assert False found - likely a bug or placeholder."),
]

PATTERNS = {
    "security": SECURITY_PATTERNS,
    "performance": PERFORMANCE_PATTERNS,
    "style": STYLE_PATTERNS,
}

def scan_file(filepath: str, categories: List[str]) -> List[Dict]:
    findings = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        for cat in categories:
            if cat in PATTERNS:
                for pattern, msg in PATTERNS[cat]:
                    for match in re.finditer(pattern, content):
                        line_no = content[:match.start()].count('\n') + 1
                        findings.append({
                            "file": filepath,
                            "line": line_no,
                            "category": cat,
                            "severity": "HIGH" if cat == "security" else ("MEDIUM" if cat == "performance" else "LOW"),
                            "message": msg,
                            "code": match.group()
                        })
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id == 'eval':
                        if not any(f['category'] == 'security' and 'eval' in f['message'] for f in findings):
                            findings.append({
                                "file": filepath,
                                "line": node.lineno,
                                "category": "security",
                                "severity": "HIGH",
                                "message": "AST detected eval() call.",
                                "code": "eval()"
                            })
                    elif node.func.id == 'exec':
                        if not any(f['category'] == 'security' and 'exec' in f['message'] for f in findings):
                            findings.append({
                                "file": filepath,
                                "line": node.lineno,
                                "category": "security",
                                "severity": "HIGH",
                                "message": "AST detected exec() call.",
                                "code": "exec()"
                            })
        except SyntaxError:
            pass
            
    except Exception as e:
        findings.append({
            "file": filepath,
            "line": 0,
            "category": "error",
            "severity": "LOW",
            "message": f"Could not read file: {e}",
            "code": ""
        })
        
    return findings

def scan_directory(dirpath: str, categories: List[str]) -> List[Dict]:
    all_findings = []
    if not os.path.isdir(dirpath):
        return all_findings
    for root, _, files in os.walk(dirpath):
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.java', '.c', '.cpp', '.h')):
                filepath = os.path.join(root, file)
                all_findings.extend(scan_file(filepath, categories))
    return all_findings
