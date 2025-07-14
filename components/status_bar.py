class StatusBar:
    """Status bar display and management"""
    
    def __init__(self, editor):
        self.editor = editor
        self.message = ""
        self.message_time = 0
        
    def set_message(self, message: str) -> None:
        self.message = message
        self.message_time = 50  # Display for 50 refresh cycles
        
    def get_status_text(self) -> str:
        if self.message_time > 0:
            self.message_time -= 1
            return self.message
            
        buffer = self.editor.buffer
        mode_text = self.editor.mode.value
        file_text = buffer.filename or "[No Name]"
        modified_text = " [+]" if buffer.modified else ""
        cursor_text = f"{buffer.cursor.row + 1},{buffer.cursor.col + 1}"
        
        return f"{mode_text} | {file_text}{modified_text} | {cursor_text}"