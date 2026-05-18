import sys

def generate_report(issues):
    if not issues:
        print("No issues found.")
        return
    
    print(f"\nFound {len(issues)} issues:\n")
    print(f"{'File':<30} {'Line':<6} {'Severity':<10} {'Message'}")
    print("-" * 80)
    for issue in issues:
        print(f"{issue['file']:<30} {issue['line']:<6} {issue['severity']:<10} {issue['message']}")
    print()