import argparse
import os
import sys
from scanner import scan_directory
from report import generate_report

def main():
    parser = argparse.ArgumentParser(description="Code Review CLI - Scans code files for common issues.")
    parser.add_argument("path", help="Path to directory to scan")
    parser.add_argument("--category", nargs="+", choices=["security", "performance", "style"], default=["security", "performance", "style"], help="Categories to check")
    args = parser.parse_args()
    
    if not os.path.isdir(args.path):
        print(f"Error: Path '{args.path}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)
        
    findings = scan_directory(args.path, args.category)
    generate_report(findings)

if __name__ == "__main__":
    main()
