import curses
import os
from typing import List

from commands.command import Command
from commands.delete import DeleteCommand
from commands.insert import InsertCommand
from components.key_handler import KeyHandler
from components.status_bar import StatusBar
from core.buffer import Buffer
from core.file_explorer import FileExplorer
from core.search_engine import SearchEngine
from utils.mode import Mode
from utils.position import Position


class Editor:
    """Main editor class coordinating all components"""
    help_text = """
PyEdit - Vim-like Terminal Editor Manual

MODES:
  NORMAL:   Navigation, commands (default)
  INSERT:   Text input (press i)
  VISUAL:   Select text (press v)
  COMMAND:  Type : commands (press :)
  SEARCH:   Search text (press /)
  FILE_EXPLORER: File browser (press e or :explorer)

NORMAL MODE KEYS:
  h/j/k/l   Move left/down/up/right
  i         Enter insert mode
  v         Enter visual mode
  :         Enter command mode
  /         Enter search mode
  e         Open file explorer
  x         Delete character
  o/O       Insert line below/above
  u         Undo
  Ctrl+R    Redo
  q         Quit

INSERT MODE:
  ESC       Return to normal mode
  Enter     New line
  Backspace Delete

VISUAL MODE:
  d         Delete selection
  y         Copy selection
  ESC       Return to normal mode

COMMANDS (type : then command):
  w         Save file
  wq        Save and quit
  q         Quit
  e <file>  Open file
  w <file>  Save as file
  explorer  Toggle file explorer
  help      Show this help

SEARCH (press /):
  Type pattern, Enter to search, ESC to cancel

FILE EXPLORER:
  Open:     Press 'e' in normal mode, or use :explorer
  j/k       Move down/up
  Enter     Open file or enter directory
  ..        Go up to parent directory
  r         Refresh file list
  ESC       Return to normal mode/editor
  (Sidebar can be toggled with :explorer or 'e')

HELP:
  q or ESC  Close help
"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.mode = Mode.NORMAL
        self.buffer = Buffer()
        self.scroll_offset = Position(0, 0)
        self.visual_start = Position(0, 0)
        self.visual_end = Position(0, 0)  # Track end of visual selection
        
        # Components
        self.file_explorer = FileExplorer()
        self.search_engine = SearchEngine()
        self.key_handler = KeyHandler(self)
        self.status_bar = StatusBar(self)
        
        # State
        self.command_buffer = ""
        self.search_buffer = ""
        self.clipboard = ""
        self.command_history: List[Command] = []
        self.undo_index = -1
        self.quit_requested = False
        
        # Display settings
        self.show_file_explorer = False
        self.explorer_width = 30
        
        # Initialize curses
        curses.curs_set(1)
        self.stdscr.keypad(True)
        self.stdscr.timeout(100)
        
    def run(self) -> None:
        """Main editor loop"""
        while not self.quit_requested:
            self.refresh_display()
            try:
                key = self.stdscr.getch()
                if key != -1:
                    if self.key_handler.handle_key(key):
                        break
            except KeyboardInterrupt:
                break
                
    def refresh_display(self) -> None:
        """Refresh the entire display"""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        
        # Calculate layout
        explorer_width = self.explorer_width if self.show_file_explorer else 0
        text_width = width - explorer_width
        text_height = height - 1  # Reserve space for status bar
        
        # Draw file explorer
        if self.show_file_explorer or self.mode == Mode.FILE_EXPLORER:
            self._draw_file_explorer(height - 1, explorer_width)
            
        # Draw main text area
        self._draw_text_area(text_height, text_width, explorer_width)
        
        # Draw status bar
        self._draw_status_bar(height - 1, width)
        
        # Position cursor
        self._position_cursor(explorer_width)
        
        self.stdscr.refresh()
        
    def _draw_file_explorer(self, height: int, width: int) -> None:
        """Draw file explorer sidebar"""
        if width <= 0:
            return
            
        # Draw border
        for i in range(height):
            if i < len(self.file_explorer.items):
                item = self.file_explorer.items[i]
                if i == self.file_explorer.selected_index:
                    self.stdscr.attron(curses.A_REVERSE)
                    
                display_text = item[:width-1]
                self.stdscr.addstr(i, 0, display_text.ljust(width-1))
                
                if i == self.file_explorer.selected_index:
                    self.stdscr.attroff(curses.A_REVERSE)
            else:
                self.stdscr.addstr(i, 0, " " * (width-1))
                
        # Draw vertical separator
        for i in range(height):
            try:
                self.stdscr.addstr(i, width-1, "|")
            except curses.error:
                pass
                
    def _draw_text_area(self, height: int, width: int, offset_x: int) -> None:
        """Draw main text editing area with horizontal scrolling for long lines"""
        line_count = self.buffer.get_line_count()
        for i in range(height):
            line_num = i + self.scroll_offset.row
            if line_num < line_count:
                line = self.buffer.get_line(line_num)
                display_line = line[self.scroll_offset.col:self.scroll_offset.col + width]
                # Highlight visual selection (single-line only)
                if self.mode == Mode.VISUAL and line_num == self.buffer.cursor.row:
                    start = min(self.visual_start.col, self.buffer.cursor.col) - self.scroll_offset.col
                    end = max(self.visual_start.col, self.buffer.cursor.col) - self.scroll_offset.col
                    start = max(0, start)
                    end = min(width, end)
                    if start < end:
                        try:
                            self.stdscr.addstr(i, offset_x, display_line[:start])
                            self.stdscr.attron(curses.A_REVERSE)
                            self.stdscr.addstr(i, offset_x + start, display_line[start:end])
                            self.stdscr.attroff(curses.A_REVERSE)
                            self.stdscr.addstr(i, offset_x + end, display_line[end:])
                        except curses.error:
                            pass
                        continue
                try:
                    self.stdscr.addstr(i, offset_x, display_line)
                except curses.error:
                    pass
            else:
                # Only draw ~ for lines after the buffer, up to the visible area
                try:
                    self.stdscr.addstr(i, offset_x, "~".ljust(width))
                except curses.error:
                    pass
                    
    def _draw_status_bar(self, row: int, width: int) -> None:
        """Draw status bar at bottom"""
        status_text = self.status_bar.get_status_text()
        
        if self.mode == Mode.COMMAND:
            status_text = f":{self.command_buffer}"
        elif self.mode == Mode.SEARCH:
            status_text = f"/{self.search_buffer}"
            
        try:
            self.stdscr.attron(curses.A_REVERSE)
            self.stdscr.addstr(row, 0, status_text.ljust(width))
            self.stdscr.attroff(curses.A_REVERSE)
        except curses.error:
            pass
            
    def _highlight_selection(self, line: str, line_num: int, display_row: int) -> str:
        # No-op, handled in _draw_text_area now
        return line
        
    def _position_cursor(self, offset_x: int) -> None:
        """Position the cursor correctly"""
        if self.mode in [Mode.COMMAND, Mode.SEARCH]:
            cursor_x = len(self.command_buffer if self.mode == Mode.COMMAND else self.search_buffer) + 1
            cursor_y = self.stdscr.getmaxyx()[0] - 1
            try:
                self.stdscr.move(cursor_y, cursor_x)
            except curses.error:
                pass
        else:
            cursor_x = self.buffer.cursor.col - self.scroll_offset.col + offset_x
            cursor_y = self.buffer.cursor.row - self.scroll_offset.row
            try:
                self.stdscr.move(cursor_y, cursor_x)
            except curses.error:
                pass
                
    def move_cursor(self, dx: int, dy: int) -> None:
        """Move cursor with bounds checking"""
        new_row = max(0, min(self.buffer.get_line_count() - 1, self.buffer.cursor.row + dy))
        line = self.buffer.get_line(new_row)
        new_col = max(0, min(len(line), self.buffer.cursor.col + dx))
        
        self.buffer.cursor = Position(new_row, new_col)
        self._adjust_scroll()
        
    def _adjust_scroll(self) -> None:
        """Adjust scroll to keep cursor visible"""
        height, width = self.stdscr.getmaxyx()
        text_height = height - 1
        
        # Vertical scrolling
        if self.buffer.cursor.row < self.scroll_offset.row:
            self.scroll_offset.row = self.buffer.cursor.row
        elif self.buffer.cursor.row >= self.scroll_offset.row + text_height:
            self.scroll_offset.row = self.buffer.cursor.row - text_height + 1
            
        # Horizontal scrolling
        explorer_width = self.explorer_width if self.show_file_explorer else 0
        text_width = width - explorer_width
        
        if self.buffer.cursor.col < self.scroll_offset.col:
            self.scroll_offset.col = self.buffer.cursor.col
        elif self.buffer.cursor.col >= self.scroll_offset.col + text_width:
            self.scroll_offset.col = self.buffer.cursor.col - text_width + 1
            
    def insert_char(self, char: str) -> None:
        """Insert character at cursor position"""
        cmd = InsertCommand(self.buffer.cursor, char)
        self._execute_command(cmd)
        self.buffer.cursor.col += 1
        
    def delete_char(self) -> None:
        """Delete character at cursor position"""
        if self.buffer.cursor.col < len(self.buffer.get_line(self.buffer.cursor.row)):
            cmd = DeleteCommand(self.buffer.cursor, 1)
            self._execute_command(cmd)
            
    def backspace(self) -> None:
        """Handle backspace with undo support"""
        if self.buffer.cursor.col > 0:
            self.buffer.cursor.col -= 1
            cmd = DeleteCommand(Position(self.buffer.cursor.row, self.buffer.cursor.col), 1)
            self._execute_command(cmd)
        elif self.buffer.cursor.row > 0:
            # Join with previous line (undoable)
            prev_line = self.buffer.get_line(self.buffer.cursor.row - 1)
            curr_line = self.buffer.get_line(self.buffer.cursor.row)
            pos = Position(self.buffer.cursor.row - 1, len(prev_line))
            cmd = InsertCommand(pos, curr_line)
            self._execute_command(cmd)
            self.buffer.lines.pop(self.buffer.cursor.row)
            self.buffer.cursor.row -= 1
            self.buffer.cursor.col = len(prev_line)
            self.buffer.modified = True
            
    def insert_newline(self) -> None:
        """Insert newline at cursor position with undo support"""
        pos = Position(self.buffer.cursor.row, self.buffer.cursor.col)
        line = self.buffer.get_line(self.buffer.cursor.row)
        after = line[self.buffer.cursor.col:]
        cmd = InsertCommand(Position(self.buffer.cursor.row + 1, 0), after)
        self._execute_command(cmd)
        self.buffer.insert_newline(self.buffer.cursor)
        self.buffer.cursor.row += 1
        self.buffer.cursor.col = 0
        
    def insert_line_below(self) -> None:
        """Insert line below cursor and enter insert mode"""
        line = self.buffer.get_line(self.buffer.cursor.row)
        self.buffer.cursor.col = len(line)
        self.insert_newline()
        self.mode = Mode.INSERT
        
    def insert_line_above(self) -> None:
        """Insert line above cursor and enter insert mode"""
        self.buffer.lines.insert(self.buffer.cursor.row, "")
        self.buffer.cursor.col = 0
        self.buffer.modified = True
        self.mode = Mode.INSERT
        
    def delete_selection(self) -> None:
        """Delete visual selection (basic single-line)"""
        if self.mode == Mode.VISUAL:
            start = min(self.visual_start.col, self.buffer.cursor.col)
            end = max(self.visual_start.col, self.buffer.cursor.col)
            row = self.buffer.cursor.row
            cmd = DeleteCommand(Position(row, start), end - start)
            self._execute_command(cmd)
            self.buffer.cursor.col = start
            self.mode = Mode.NORMAL
            self.status_bar.set_message("Selection deleted")
            
    def copy_selection(self) -> None:
        """Copy visual selection to clipboard (basic single-line)"""
        if self.mode == Mode.VISUAL:
            start = min(self.visual_start.col, self.buffer.cursor.col)
            end = max(self.visual_start.col, self.buffer.cursor.col)
            row = self.buffer.cursor.row
            self.clipboard = self.buffer.get_line(row)[start:end]
            self.mode = Mode.NORMAL
            self.status_bar.set_message("Selection copied")
            
    def execute_command(self) -> None:
        """Execute command mode command with improved error messages"""
        cmd = self.command_buffer.strip()
        if cmd == "q":
            self.quit_requested = True
        elif cmd == "w":
            if self.buffer.save_file():
                self.status_bar.set_message("File saved")
            else:
                self.status_bar.set_message(f"Error saving file: {self.buffer.filename}")
        elif cmd == "wq":
            if self.buffer.save_file():
                self.quit_requested = True
            else:
                self.status_bar.set_message(f"Error saving file: {self.buffer.filename}")
        elif cmd.startswith("w "):
            filename = cmd[2:].strip()
            if self.buffer.save_file(filename):
                self.status_bar.set_message(f"File saved as {filename}")
            else:
                self.status_bar.set_message(f"Error saving file: {filename}")
        elif cmd.startswith("e "):
            filename = cmd[2:].strip()
            if self.buffer.load_file(filename):
                self.buffer.cursor = Position(0, 0)
                self.scroll_offset = Position(0, 0)
                self.status_bar.set_message(f"Loaded {filename}")
            else:
                self.status_bar.set_message(f"Error loading file: {filename}")
        elif cmd == "explorer":
            self.show_file_explorer = not self.show_file_explorer
        elif cmd == "help":
            self.show_help()
        else:
            self.status_bar.set_message(f"Unknown command: {cmd}")
            
    def perform_search(self) -> None:
        """Perform search in current buffer"""
        if self.search_buffer:
            results = self.search_engine.search_in_buffer(self.buffer, self.search_buffer)
            if results:
                # Jump to first result
                self.buffer.cursor = Position(results[0][0], results[0][1])
                self._adjust_scroll()
                self.status_bar.set_message(f"Found {len(results)} matches")
            else:
                self.status_bar.set_message("No matches found")
                
    def open_selected_file(self) -> None:
        """Open selected file from file explorer"""
        selected_path = self.file_explorer.get_selected_path()
        if os.path.isfile(selected_path):
            if self.buffer.load_file(selected_path):
                self.buffer.cursor = Position(0, 0)
                self.scroll_offset = Position(0, 0)
                self.mode = Mode.NORMAL
                self.status_bar.set_message(f"Opened {selected_path}")
            else:
                self.status_bar.set_message(f"Error opening file: {selected_path}")
        elif os.path.isdir(selected_path):
            self.file_explorer.navigate_to(selected_path)
            
    def _execute_command(self, command: Command) -> None:
        """Execute command and add to history"""
        command.execute(self)
        # Truncate history if we're not at the end
        if self.undo_index < len(self.command_history) - 1:
            self.command_history = self.command_history[:self.undo_index + 1]
        self.command_history.append(command)
        self.undo_index = len(self.command_history) - 1
        
    def undo(self) -> None:
        """Undo last command"""
        if self.undo_index >= 0:
            self.command_history[self.undo_index].undo(self)
            self.undo_index -= 1
            self.status_bar.set_message("Undone")
            
    def redo(self) -> None:
        """Redo last undone command"""
        if self.undo_index < len(self.command_history) - 1:
            self.undo_index += 1
            self.command_history[self.undo_index].execute(self)
            self.status_bar.set_message("Redone")

    def show_help(self):
        """Display the help manual in a scrollable window"""
        lines = self.help_text.strip().split('\n')
        maxy, maxx = self.stdscr.getmaxyx()
        win_height = min(len(lines) + 2, maxy - 2)
        win_width = min(max(len(line) for line in lines) + 4, maxx - 2)
        win = curses.newwin(win_height, win_width, (maxy - win_height) // 2, (maxx - win_width) // 2)
        win.keypad(True)
        scroll = 0
        while True:
            win.clear()
            win.box()
            for i in range(win_height - 2):
                idx = i + scroll
                if idx < len(lines):
                    win.addstr(i + 1, 2, lines[idx][:win_width - 4])
            win.refresh()
            key = win.getch()
            if key in (ord('q'), 27):  # q or ESC
                break
            elif key == curses.KEY_DOWN and scroll < len(lines) - (win_height - 2):
                scroll += 1
            elif key == curses.KEY_UP and scroll > 0:
                scroll -= 1
        del win
        self.refresh_display()
