import argparse
import sys
from scanner import Scanner
from report import render_report

def main():
    parser = argparse.ArgumentParser(description='Code Review CLI')
    parser.add_argument('directory', help='Directory to scan')
    parser.add_argument('--category', choices=['security', 'performance', 'style', 'all'], default='all')
    args = parser.parse_args()
    
    scanner = Scanner(categories=None if args.category == 'all' else [args.category])
    findings = scanner.scan_directory(args.directory)
    render_report(findings)

if __name__ == '__main__':
    main()
