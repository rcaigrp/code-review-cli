import sys
from typing import List, Dict, Any

def generate_report(issues: List[Dict[str, Any]]):
    print("Code Review Report")
    print("==================")
    if not issues:
        print("No issues found.")
        return

    print(f"Total issues: {len(issues)}")
    print("------------------")
    for issue in issues:
        print(f"File: {issue.get('file', 'N/A')}")
        print(f"Line: {issue.get('line', 'N/A')}")
        print(f"Category: {issue.get('category', 'N/A')}")
        print(f"Severity: {issue.get('severity', 'N/A')}")
        print(f"Message: {issue.get('message', 'N/A')}")
        print(f"Suggestion: {issue.get('suggestion', 'N/A')}")
        print("------------------")
    print("End of Report")
