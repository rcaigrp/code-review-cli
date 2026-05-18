import argparse
import sys
from scanner import Scanner
from report import print_report

def main():
    parser = argparse.ArgumentParser(description='Code Review CLI')
    parser.add_argument('path', help='Directory path to scan')
    parser.add_argument('--category', nargs='+', choices=['security', 'performance', 'style'], default=['security', 'performance', 'style'])
    args = parser.parse_args()

    scanner = Scanner(categories=args.category)
    findings = scanner.scan_directory(args.path)
    print_report(findings)

if __name__ == '__main__':
    main()
