import sys
from typing import List, Dict, Any

def render_report(findings: List[Dict[str, Any]]):
    print('Code Review Report')
    print('-' * 80)
    for f in findings:
        print(f"{f['file']}:{f['line']} [{f['category'].upper()}] {f['severity']}: {f['message']}")
    print('-' * 80)
    print(f"Total findings: {len(findings)}")
