import argparse
import sys
from scanner import Scanner
from report import print_report

def main():
    parser = argparse.ArgumentParser(description='Code Review CLI')
    parser.add_argument('directory', help='Path to directory to scan')
    parser.add_argument('--category', choices=['security', 'performance', 'style'], 
                        nargs='+', default=None, help='Categories to scan for')
    
    args = parser.parse_args()
    
    scanner = Scanner(categories=args.category)
    try:
        issues = scanner.scan_directory(args.directory)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    print_report(issues)

if __name__ == '__main__':
    main()
