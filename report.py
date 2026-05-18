def format_report(issues: list) -> str:
    output = "=== Code Review Report ===\n"
    if not issues:
        output += "No issues found.\n"
        return output
    
    output += f"{'Type':<15} {'Name':<20} {'File':<30} {'Line':<5}\n"
    output += "-" * 70 + "\n"
    for issue in issues:
        issue_type = issue.get("type", "error")
        name = issue.get("name", "unknown")
        file = issue.get("file", "N/A")
        line = issue.get("line", "N/A")
        output += f"{issue_type:<15} {name:<20} {file:<30} {line:<5}\n"
    return output

def print_report(issues: list):
    print(format_report(issues))
