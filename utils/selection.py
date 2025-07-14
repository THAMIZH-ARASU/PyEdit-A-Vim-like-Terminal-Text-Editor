from dataclasses import dataclass
from utils.position import Position


@dataclass
class Selection:
    start: Position
    end: Position
