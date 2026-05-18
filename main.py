import argparse
import os
from scanner import scan_file
from report import print_report

def main():
    parser = argparse.ArgumentParser(description="Code Review CLI")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--category", nargs='+', choices=['security', 'performance', 'style'], default=['security', 'performance', 'style'])
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a valid directory.")
        return

    all_issues = []
    for root, dirs, files in os.walk(args.directory):
        for file in files:
            if file.endswith(('.py', '.js', '.ts')):
                file_path = os.path.join(root, file)
                issues = scan_file(file_path, args.category)
                all_issues.extend(issues)

    print_report(all_issues)

if __name__ == "__main__":
    main()
