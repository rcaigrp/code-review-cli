import sys
from typing import List, Dict

def generate_report(findings: List[Dict]) -> None:
    if not findings:
        print("No findings found.")
        return
    
    print("\n=== Code Review Report ===\n")
    print(f"{'File':<30} {'Category':<12} {'Severity':<8} {'Line':<6} {'Message'}")
    print("-" * 100)
    for f in findings:
        print(f"{f['file']:<30} {f['category']:<12} {f['severity']:<8} {f['line']:<6} {f['message']}")
    print("\n==========================\n")
