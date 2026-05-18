from typing import List
from scanner import Issue

def print_report(issues: List[Issue]):
    print("=" * 50)
    print("Code Review Report")
    print("=" * 50)
    print(f"Total Issues Found: {len(issues)}")
    print("-" * 50)
    for issue in issues:
        print(f"[{issue.category.upper()}] {issue.file}:{issue.line}")
        print(f"  Message: {issue.message}")
        print(f"  Suggestion: {issue.suggestion}")
        print("-" * 50)
    if not issues:
        print("No issues found.")
