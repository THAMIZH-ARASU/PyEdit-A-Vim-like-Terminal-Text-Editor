from abc import ABC, abstractmethod


class Command(ABC):
    """Command pattern for undo/redo functionality"""
    
    @abstractmethod
    def execute(self, editor) -> None:
        pass
    
    @abstractmethod
    def undo(self, editor) -> None:
        pass