import argparse
import sys
from scanner import Scanner
from report import generate_report

def main():
    parser = argparse.ArgumentParser(description='Code Review CLI')
    parser.add_argument('directory', help='Directory to scan')
    parser.add_argument('--category', nargs='+', default=['security', 'performance', 'style'],
                        help='Categories to check')
    args = parser.parse_args()

    scanner = Scanner(args.category)
    issues = scanner.scan_directory(args.directory)
    generate_report(issues)

if __name__ == '__main__':
    main()
