import curses
from utils.mode import Mode
from utils.position import Position
import os


class KeyHandler:
    """Handle key input and mode switching"""
    
    def __init__(self, editor):
        self.editor = editor
        self.key_mappings = {
            Mode.NORMAL: self._handle_normal_mode,
            Mode.INSERT: self._handle_insert_mode,
            Mode.VISUAL: self._handle_visual_mode,
            Mode.COMMAND: self._handle_command_mode,
            Mode.SEARCH: self._handle_search_mode,
            Mode.FILE_EXPLORER: self._handle_file_explorer_mode
        }
        
    def handle_key(self, key: int) -> bool:
        handler = self.key_mappings.get(self.editor.mode)
        if handler:
            return handler(key)
        return False
        
    def _handle_normal_mode(self, key: int) -> bool:
        if key == ord('i'):
            self.editor.mode = Mode.INSERT
        elif key == ord('v'):
            self.editor.mode = Mode.VISUAL
            self.editor.visual_start = Position(self.editor.cursor.row, self.editor.cursor.col)
        elif key == ord(':'):
            self.editor.mode = Mode.COMMAND
            self.editor.command_buffer = ""
        elif key == ord('/'):
            self.editor.mode = Mode.SEARCH
            self.editor.search_buffer = ""
        elif key == ord('e'):
            self.editor.mode = Mode.FILE_EXPLORER
        elif key == ord('h') or key == curses.KEY_LEFT:
            self.editor.move_cursor(-1, 0)
        elif key == ord('j') or key == curses.KEY_DOWN:
            self.editor.move_cursor(0, 1)
        elif key == ord('k') or key == curses.KEY_UP:
            self.editor.move_cursor(0, -1)
        elif key == ord('l') or key == curses.KEY_RIGHT:
            self.editor.move_cursor(1, 0)
        elif key == ord('x'):
            self.editor.delete_char()
        elif key == ord('o'):
            self.editor.insert_line_below()
        elif key == ord('O'):
            self.editor.insert_line_above()
        elif key == ord('u'):
            self.editor.undo()
        elif key == 18:  # Ctrl+R
            self.editor.redo()
        elif key == ord('q'):
            return True
        return False
        
    def _handle_insert_mode(self, key: int) -> bool:
        if key == 27:  # ESC
            self.editor.mode = Mode.NORMAL
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            self.editor.backspace()
        elif key == ord('\n') or key == ord('\r'):
            self.editor.insert_newline()
        elif key == curses.KEY_LEFT:
            self.editor.move_cursor(-1, 0)
        elif key == curses.KEY_RIGHT:
            self.editor.move_cursor(1, 0)
        elif key == curses.KEY_UP:
            self.editor.move_cursor(0, -1)
        elif key == curses.KEY_DOWN:
            self.editor.move_cursor(0, 1)
        elif key == 9:  # Tab key
            self.editor.autocomplete()
        elif 32 <= key <= 126:  # Printable characters
            self.editor.insert_char(chr(key))
        return False
        
    def _handle_visual_mode(self, key: int) -> bool:
        if key == 27:  # ESC
            self.editor.mode = Mode.NORMAL
        elif key == ord('d'):
            self.editor.delete_selection()
            self.editor.mode = Mode.NORMAL
        elif key == ord('y'):
            self.editor.copy_selection()
            self.editor.mode = Mode.NORMAL
        elif key == ord('h') or key == curses.KEY_LEFT:
            self.editor.move_cursor(-1, 0)
        elif key == ord('j') or key == curses.KEY_DOWN:
            self.editor.move_cursor(0, 1)
        elif key == ord('k') or key == curses.KEY_UP:
            self.editor.move_cursor(0, -1)
        elif key == ord('l') or key == curses.KEY_RIGHT:
            self.editor.move_cursor(1, 0)
        return False
        
    def _handle_command_mode(self, key: int) -> bool:
        if key == 27:  # ESC
            self.editor.mode = Mode.NORMAL
        elif key == ord('\n') or key == ord('\r'):
            prev_mode = self.editor.mode
            self.editor.execute_command()
            # Only set to NORMAL if not switched to another mode
            if self.editor.mode == prev_mode:
                self.editor.mode = Mode.NORMAL
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            self.editor.command_buffer = self.editor.command_buffer[:-1]
        elif 32 <= key <= 126:
            self.editor.command_buffer += chr(key)
        return False
        
    def _handle_search_mode(self, key: int) -> bool:
        if key == 27:  # ESC
            self.editor.mode = Mode.NORMAL
        elif key == ord('\n') or key == ord('\r'):
            self.editor.perform_search()
            self.editor.mode = Mode.NORMAL
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            self.editor.search_buffer = self.editor.search_buffer[:-1]
        elif 32 <= key <= 126:
            self.editor.search_buffer += chr(key)
        return False
        
    def _handle_file_explorer_mode(self, key: int) -> bool:
        fe = self.editor.file_explorer
        if key == 27 or key == ord('q'):
            self.editor.mode = Mode.NORMAL
            self.editor.refresh_display()
        elif key == ord('j') or key == curses.KEY_DOWN:
            fe.move_down()
            self.editor.refresh_display()
        elif key == ord('k') or key == curses.KEY_UP:
            fe.move_up()
            self.editor.refresh_display()
        elif key == ord('l') or key == curses.KEY_RIGHT or key == ord('\n') or key == ord('\r'):
            result = fe.enter()
            self.editor.refresh_display()
            if isinstance(result, str) and os.path.isfile(result):
                self.editor.open_file_from_explorer(result)
        elif key == ord('h') or key == curses.KEY_LEFT or key in (curses.KEY_BACKSPACE, 127, 8):
            fe.back()
            self.editor.refresh_display()
        elif key == ord('r'):
            fe.refresh()
            self.editor.refresh_display()
        return False
