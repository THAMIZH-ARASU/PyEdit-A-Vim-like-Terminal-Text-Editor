from commands.command import Command
from utils.position import Position


class DeleteCommand(Command):
    def __init__(self, pos: Position, length: int):
        self.pos = pos
        self.length = length
        self.deleted_text = ""
        
    def execute(self, editor) -> None:
        self.deleted_text = editor.buffer.get_text(self.pos, self.length)
        editor.buffer.delete_text(self.pos, self.length)
        
    def undo(self, editor) -> None:
        editor.buffer.insert_text(self.pos, self.deleted_text)