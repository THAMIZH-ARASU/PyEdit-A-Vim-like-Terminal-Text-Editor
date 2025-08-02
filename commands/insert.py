from commands.command import Command
from core.editor import Editor
from utils.position import Position


class InsertCommand(Command):
    def __init__(self, pos: Position, text: str):
        self.pos = pos
        self.text = text
        
    def execute(self, editor: Editor) -> None:
        editor.buffer.insert_text(self.pos, self.text)
        
    def undo(self, editor: Editor) -> None:
        editor.buffer.delete_text(self.pos, len(self.text))