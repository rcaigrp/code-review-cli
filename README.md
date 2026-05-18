# Code-Review-CLI

A Python CLI tool that scans code files for common issues (security, performance, style) using regex and AST parsing. It generates a formatted report with severity levels and suggestions. No external dependencies required.

## Usage
```bash
python main.py /path/to/dir --categories security performance style
```

## Setup
```bash
# No external dependencies required.
```

## Tests
```bash
cd /workspace/projects/Code-Review-CLI && python -m pytest acceptance_tests.py -v
```
