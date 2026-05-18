import ast
import re
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Issue:
    file: str
    line: int
    category: str
    severity: str
    message: str
    suggestion: str

class Scanner:
    def __init__(self, categories: List[str] = None):
        self.categories = categories or ['security', 'performance', 'style']
        self.regex_patterns = {
            'security': [
                (r'eval\s*\(', 'Use ast.literal_eval or a safer alternative instead of eval.'),
                (r'exec\s*\(', 'Avoid exec; use safer alternatives for dynamic code execution.'),
                (r'os\.system\s*\(', 'Use subprocess.run or subprocess.Popen instead of os.system.'),
                (r'pickle\.loads?\s*\(', 'Use json or yaml for safer deserialization instead of pickle.'),
            ],
            'performance': [
                (r'import\s+time\s*;\s*time\.sleep\s*\(\s*0\.5\s*\)', 'Consider using a more efficient sleep mechanism or batching.'),
                (r'while\s+True\s*:', 'Ensure the loop has a clear break condition to avoid infinite loops.'),
            ],
            'style': [
                (r'#\s*FIXME', 'Address the FIXME comment or mark it as resolved.'),
                (r'#\s*TODO', 'Address the TODO comment or mark it as resolved.'),
                (r'^\s*#\s*$', 'Remove empty comments.'),
            ]
        }

    def scan_file(self, filepath: str) -> List[Issue]:
        issues = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                ast.parse(content)
                
                for category in self.categories:
                    if category in self.regex_patterns:
                        for pattern, suggestion in self.regex_patterns[category]:
                            for i, line in enumerate(lines, 1):
                                if re.search(pattern, line):
                                    issues.append(Issue(
                                        file=filepath,
                                        line=i,
                                        category=category,
                                        severity='medium' if category == 'style' else 'high',
                                        message=f'Found {pattern} in line {i}',
                                        suggestion=suggestion
                                    ))
        except SyntaxError:
            pass
        except Exception:
            pass
        return issues

    def scan_directory(self, directory: str) -> List[Issue]:
        issues = []
        dir_path = Path(directory)
        if dir_path.is_dir():
            for filepath in dir_path.rglob('*.py'):
                issues.extend(self.scan_file(str(filepath)))
        return issues
