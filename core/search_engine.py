import os
import re
from typing import List, Tuple

from core.buffer import Buffer


class SearchEngine:
    """File content search functionality"""
    
    def __init__(self):
        self.last_search = ""
        self.results: List[Tuple[str, int, str]] = []
        
    def search_in_files(self, pattern: str, directory: str = ".") -> List[Tuple[str, int, str]]:
        results = []
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(('.py', '.txt', '.md', '.js', '.html', '.css', '.c', '.cpp', '.h')):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                for line_num, line in enumerate(f, 1):
                                    if re.search(pattern, line, re.IGNORECASE):
                                        results.append((filepath, line_num, line.strip()))
                        except Exception:
                            continue
        except Exception:
            pass
        return results
        
    def search_in_buffer(self, buffer: Buffer, pattern: str) -> List[Tuple[int, int]]:
        results = []
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            for row, line in enumerate(buffer.lines):
                for match in regex.finditer(line):
                    results.append((row, match.start()))
        except Exception:
            pass
        return results