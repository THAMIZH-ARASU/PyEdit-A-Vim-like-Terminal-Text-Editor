import os
from typing import List, Optional


class FileExplorer:
    """Ranger/Yazi-like two-pane file explorer"""
    def __init__(self, root_path: str = "."):
        self.root_path = os.path.abspath(root_path)
        self.dir_stack: List[str] = [self.root_path]  # Stack of directories for left pane
        self.selected_indices: List[int] = [0]        # Selected index for each pane
        self.items: List[List[str]] = []              # Items for each pane
        self.refresh_all()

    def refresh_all(self):
        self.items = []
        for d in self.dir_stack:
            try:
                entries = [".."] if d != self.root_path else []
                entries += sorted([e for e in os.listdir(d) if not e.startswith('.')])
                self.items.append(entries)
            except Exception:
                self.items.append([])
        # Clamp selected indices
        for i in range(len(self.selected_indices)):
            if self.items[i]:
                self.selected_indices[i] = min(self.selected_indices[i], len(self.items[i]) - 1)
            else:
                self.selected_indices[i] = 0

    def current_dir(self) -> str:
        return self.dir_stack[-1]

    def current_items(self) -> List[str]:
        return self.items[-1] if self.items else []

    def current_selected_index(self) -> int:
        return self.selected_indices[-1]

    def get_selected_path(self) -> str:
        items = self.current_items()
        idx = self.current_selected_index()
        if not items or idx >= len(items):
            return ""
        item = items[idx]
        if item == "..":
            return os.path.dirname(self.current_dir())
        return os.path.join(self.current_dir(), item)

    def move_up(self):
        if self.selected_indices[-1] > 0:
            self.selected_indices[-1] -= 1

    def move_down(self):
        if self.selected_indices[-1] < len(self.current_items()) - 1:
            self.selected_indices[-1] += 1

    def enter(self):
        path = self.get_selected_path()
        if os.path.isdir(path):
            self.dir_stack.append(path)
            self.selected_indices.append(0)
            self.refresh_all()
        elif os.path.isfile(path):
            return path  # For preview/open
        return None

    def back(self):
        if len(self.dir_stack) > 1:
            self.dir_stack.pop()
            self.selected_indices.pop()
            self.refresh_all()

    def refresh(self):
        self.refresh_all()

    def get_preview(self, max_lines=20) -> Optional[List[str]]:
        path = self.get_selected_path()
        if os.path.isfile(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return [line.rstrip('\n') for _, line in zip(range(max_lines), f)]
            except Exception:
                return ["[Preview unavailable]"]
        return None
