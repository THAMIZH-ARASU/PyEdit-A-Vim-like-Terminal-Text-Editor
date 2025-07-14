import os
from typing import List


class FileExplorer:
    """File explorer sidebar functionality"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = os.path.abspath(root_path)
        self.current_path = self.root_path
        self.selected_index = 0
        self.items: List[str] = []
        self.expanded_dirs: set = set()
        self.refresh()
        
    def refresh(self) -> None:
        try:
            items = []
            if self.current_path != self.root_path:
                items.append("..")
                
            entries = sorted(os.listdir(self.current_path))
            for entry in entries:
                if not entry.startswith('.'):
                    items.append(entry)
                    
            self.items = items
            self.selected_index = min(self.selected_index, len(self.items) - 1)
        except Exception:
            self.items = []
            
    def get_selected_path(self) -> str:
        if not self.items or self.selected_index >= len(self.items):
            return ""
        item = self.items[self.selected_index]
        if item == "..":
            return os.path.dirname(self.current_path)
        return os.path.join(self.current_path, item)
        
    def navigate_to(self, path: str) -> bool:
        if os.path.isdir(path):
            self.current_path = os.path.abspath(path)
            self.selected_index = 0
            self.refresh()
            return True
        return False
        
    def move_up(self) -> None:
        self.selected_index = max(0, self.selected_index - 1)
        
    def move_down(self) -> None:
        self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
