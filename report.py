import sys
from typing import List, Dict, Any

def format_report(findings: List[Dict[str, Any]]) -> str:
    output = "=== Code Review Report ===\n\n"
    output += f"{'File':<30} {'Category':<12} {'Severity':<10} {'Line':<6} {'Message'}\n"
    output += "-" * 72 + "\n"
    for f in findings:
        output += f"{f['file']:<30} {f['category']:<12} {f['severity']:<10} {f['line']:<6} {f['message']}\n"
    output += "\n==========================\n"
    return output

def print_report(findings: List[Dict[str, Any]]):
    sys.stdout.write(format_report(findings))
