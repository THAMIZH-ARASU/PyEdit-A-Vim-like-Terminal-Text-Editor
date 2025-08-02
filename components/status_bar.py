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
        
        # Get current AI model
        try:
            from core.ai_models import model_manager
            current_model = model_manager.get_current_model()
            model_text = f" | AI: {current_model}"
        except:
            model_text = ""
        
        return f"{mode_text} | {file_text}{modified_text} | {cursor_text}{model_text}"