import argparse
import sys
from scanner import scan_directory
from report import generate_report

def main():
    parser = argparse.ArgumentParser(description='Code Review CLI')
    parser.add_argument('directory', help='Directory to scan')
    parser.add_argument('--category', nargs='+', choices=['security', 'performance', 'style'], default=['security', 'performance', 'style'])
    args = parser.parse_args()
    
    issues = scan_directory(args.directory, args.category)
    generate_report(issues)

if __name__ == '__main__':
    main()