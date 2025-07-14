from dataclasses import dataclass


@dataclass
class Position:
    row: int
    col: int
    
    def __post_init__(self):
        self.row = max(0, self.row)
        self.col = max(0, self.col)