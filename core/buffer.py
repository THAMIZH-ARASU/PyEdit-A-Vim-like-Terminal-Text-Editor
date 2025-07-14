from typing import List
from utils.position import Position


class Buffer:
    """Text buffer with editing operations"""
    
    def __init__(self, filename: str = ""):
        self.filename = filename
        self.lines: List[str] = [""]
        self.modified = False
        self.cursor = Position(0, 0)
        
    def load_file(self, filename: str) -> bool:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.lines = f.read().splitlines()
                if not self.lines:
                    self.lines = [""]
            self.filename = filename
            self.modified = False
            return True
        except Exception:
            return False
            
    def save_file(self, filename: str = "") -> bool:
        try:
            save_name = filename or self.filename
            with open(save_name, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.lines))
            self.filename = save_name
            self.modified = False
            return True
        except Exception:
            return False
            
    def insert_text(self, pos: Position, text: str) -> None:
        if pos.row >= len(self.lines):
            self.lines.extend([""] * (pos.row - len(self.lines) + 1))
            
        line = self.lines[pos.row]
        self.lines[pos.row] = line[:pos.col] + text + line[pos.col:]
        self.modified = True
        
    def delete_text(self, pos: Position, length: int) -> None:
        if pos.row >= len(self.lines):
            return
            
        line = self.lines[pos.row]
        if pos.col + length <= len(line):
            self.lines[pos.row] = line[:pos.col] + line[pos.col + length:]
        self.modified = True
        
    def get_text(self, pos: Position, length: int) -> str:
        if pos.row >= len(self.lines):
            return ""
        line = self.lines[pos.row]
        return line[pos.col:pos.col + length]
        
    def insert_newline(self, pos: Position) -> None:
        if pos.row >= len(self.lines):
            self.lines.extend([""] * (pos.row - len(self.lines) + 1))
            
        line = self.lines[pos.row]
        self.lines[pos.row] = line[:pos.col]
        self.lines.insert(pos.row + 1, line[pos.col:])
        self.modified = True
        
    def delete_line(self, row: int) -> None:
        if 0 <= row < len(self.lines):
            if len(self.lines) > 1:
                self.lines.pop(row)
            else:
                self.lines[0] = ""
        self.modified = True
        
    def get_line_count(self) -> int:
        return len(self.lines)
        
    def get_line(self, row: int) -> str:
        if 0 <= row < len(self.lines):
            return self.lines[row]
        return ""
