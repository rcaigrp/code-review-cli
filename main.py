import argparse
import sys
from scanner import Scanner


def main():
    parser = argparse.ArgumentParser(description='Code Review CLI')
    parser.add_argument('path', help='Directory to scan')
    parser.add_argument('--severity', choices=['HIGH', 'MEDIUM', 'LOW'], help='Filter by severity')
    args = parser.parse_args()

    scanner = Scanner()
    findings = scanner.scan_directory(args.path)

    if args.severity:
        findings = [f for f in findings if f['severity'] == args.severity]

    print(f"Scan Results for: {args.path}")
    print("=" * 50)
    for f in findings:
        print(f"[{f['type']}] {f['file']}:{f['line']} - {f['pattern']} ({f['severity'].lower()})")


if __name__ == '__main__':
    main()
