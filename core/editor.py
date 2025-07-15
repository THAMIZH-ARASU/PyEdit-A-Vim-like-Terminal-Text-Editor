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
from core.grok_autocomplete import get_groq_suggestion # type: ignore
from core.search_engine import SearchEngine
from utils.language import detect_language # type: ignore
from utils.mode import Mode
from utils.position import Position
from utils.logger import log_autocomplete_action
import core.ai_tools as ai_tools


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
    
    home_text = r"""
                                                       
    ██████╗ ██╗   ██╗     ███████╗██████╗ ██╗███████╗  
    ██╔══██╗╚██╗ ██╔╝     ██╔════╝██╔══██╗██║  ██╔══╝  
    ██████╔╝ ╚████╔╝█████╗█████╗  ██   ██║██║  ██║     
    ██╔═══╝   ╚██╔╝ ╚════╝██╔══╝  ██   ██║██║  ██║     
    ██║        ██║        ███████╗██████╔╝██║  ██║     
    ╚═╝        ╚═╝        ╚══════╝╚═════╝ ╚═╝  ╚═╝     

    Welcome to PyEdit - A Modern, Vim-inspired Terminal Text Editor

    • Modal editing (Normal, Insert, Visual, Command, Search, Explorer)
    • Fast, lightweight, and extensible
    • File explorer, search, undo/redo, and more
    • AI-powered autocomplete (Tab in insert mode)
    • Familiar Vim keybindings

    :q      Quit      :w      Save      :e <file>  Open file
    :help   Manual    :explorer Toggle file explorer   :home   Toggle home

    PyEdit is open source. See README.md for more info.
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
        self.show_home_page = True
        
        # Initialize curses
        curses.curs_set(1)  # Make cursor visible and blinking
        curses.cbreak()     # React to keys instantly
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
        
        if getattr(self, 'show_home_page', False):
            self.show_home(height, width)
        else:
            # Calculate layout
            explorer_width = self.explorer_width if self.mode == Mode.FILE_EXPLORER else 0
            text_width = width - explorer_width
            text_height = height - 1  # Reserve space for status bar

            # Draw file explorer
            if self.mode == Mode.FILE_EXPLORER:
                self._draw_file_explorer(height - 1, width)
            else:
                self._draw_text_area(text_height, text_width, explorer_width)

            # Draw status bar
            self._draw_status_bar(height - 1, width)

            # Position cursor
            self._position_cursor(explorer_width)

        self.stdscr.refresh()
        
    def _draw_file_explorer(self, height: int, width: int) -> None:
        """Draw file explorer sidebar with fixed-width navigation (30 cols) and wide preview."""
        if width <= 0:
            return
        nav_width = min(30, width - 1) if width > 30 else width
        preview_width = max(10, width - nav_width)  # Minimum preview width of 10
        explorer = self.file_explorer
        y = 0
        
        # Draw navigation pane
        for depth, (dir_path, items, sel_idx) in enumerate(zip(explorer.dir_stack, explorer.items, explorer.selected_indices)):
            if y >= height:
                break
            dir_name = os.path.basename(dir_path) or dir_path
            self.stdscr.addstr(y, 0, f"[{dir_name}]".ljust(nav_width)[:nav_width])
            y += 1
            for i, item in enumerate(items):
                if y >= height:
                    break
                prefix = '>' if i == sel_idx else ' '
                line = f"{prefix} {item}"
                if i == sel_idx:
                    self.stdscr.attron(curses.A_REVERSE)
                self.stdscr.addstr(y, 0, line.ljust(nav_width)[:nav_width])
                if i == sel_idx:
                    self.stdscr.attroff(curses.A_REVERSE)
                y += 1
        
        # Draw preview pane (moved outside the loop)
        selected_path = explorer.get_selected_path()
        print(f"[DEBUG] Previewing: {selected_path} | isfile: {os.path.isfile(selected_path)}")
        if preview_width >= 10:
            if selected_path and os.path.isfile(selected_path):
                try:
                    with open(selected_path, 'r', encoding='utf-8') as f:
                        lines = [line.rstrip('\n') for _, line in zip(range(height), f)]
                    if lines:
                        for i, line in enumerate(lines):
                            if i >= height:
                                break
                            try:
                                self.stdscr.addstr(i, nav_width, line[:preview_width])
                            except curses.error:
                                pass
                    else:
                        try:
                            self.stdscr.addstr(0, nav_width, "[Empty file]"[:preview_width])
                        except curses.error:
                            pass
                except Exception:
                    try:
                        self.stdscr.addstr(0, nav_width, "[Preview unavailable]"[:preview_width])
                    except curses.error:
                        pass
            else:
                try:
                    self.stdscr.addstr(0, nav_width, "Select a file to preview"[:preview_width])
                except curses.error:
                    pass
        else:
            try:
                self.stdscr.addstr(0, nav_width, "[Window too narrow for preview]"[:width - nav_width])
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
        explorer_width = self.explorer_width if self.mode == Mode.FILE_EXPLORER else 0
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
            self.show_home_page = False
            self.mode = Mode.FILE_EXPLORER
        elif cmd == "help":
            self.show_help()
        elif cmd == "home":
            self.show_home_page = not getattr(self, 'show_home_page', False)
        elif cmd.startswith(":ai") or cmd.startswith("ai ") or cmd.startswith("ai:") or cmd.startswith("ai_") or cmd.startswith("ai.") or cmd.startswith("ai/") or cmd.startswith("ai-") or cmd.startswith("ai"):
            # Parse :ai <action> [args]
            parts = cmd.split()
            if len(parts) < 2:
                self.status_bar.set_message("Usage: :ai <action> [args]")
                return
            action = parts[1].lower()
            args = parts[2:]
            buffer_lines = self.buffer.lines
            cursor_position = self.buffer.cursor
            language = None
            result = None
            try:
                code_actions = ["refactor", "nl2code", "translate", "snippet", "testgen"]
                if action == "refactor":
                    result = ai_tools.ai_refactor(buffer_lines, cursor_position, language)
                elif action == "doc":
                    result = ai_tools.ai_doc(buffer_lines, cursor_position, language)
                elif action == "explain":
                    result = ai_tools.ai_explain(buffer_lines, cursor_position, language)
                elif action == "testgen":
                    result = ai_tools.ai_testgen(buffer_lines, cursor_position, language)
                elif action == "review":
                    result = ai_tools.ai_review(buffer_lines, cursor_position, language)
                elif action == "nl2code":
                    instruction = ' '.join(args)
                    result = ai_tools.ai_nl2code(instruction)
                elif action == "translate":
                    target_language = args[0] if args else "python"
                    result = ai_tools.ai_translate(buffer_lines, cursor_position, target_language)
                elif action == "search":
                    query = ' '.join(args)
                    result = ai_tools.ai_search(query, [])
                elif action == "commitmsg":
                    # For now, use the buffer as the diff
                    diff = '\n'.join(buffer_lines)
                    result = ai_tools.ai_commitmsg(diff)
                elif action == "chat":
                    user_message = ' '.join(args)
                    result = ai_tools.ai_chat([], user_message)
                elif action == "snippet":
                    description = ' '.join(args)
                    result = ai_tools.ai_snippet(description)
                else:
                    self.status_bar.set_message(f"Unknown AI action: {action}")
                    return
                # If the action is code-producing, update the buffer
                if action in code_actions and result:
                    # Replace buffer content with AI result
                    self.buffer.lines = result.split('\n')
                    self.buffer.cursor = Position(0, 0)
                    self.scroll_offset = Position(0, 0)
                    self.status_bar.set_message(f"Buffer updated by AI: {action}")
                    self.refresh_display()
                # Always show popup for doc, explain, review, search, commitmsg, chat
                elif action in ["doc", "explain", "review", "search", "commitmsg", "chat"] and result:
                    self._show_ai_popup(result)
                # Fallback: show in status bar
                else:
                    self.status_bar.set_message(result or "No AI response.")
            except Exception as e:
                self.status_bar.set_message(f"AI error: {e}")
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
            
    def open_file_from_explorer(self, filepath: str):
        if self.buffer.load_file(filepath):
            self.buffer.cursor = Position(0, 0)
            self.scroll_offset = Position(0, 0)
            self.status_bar.set_message(f"Opened {filepath}")
        else:
            self.status_bar.set_message(f"Error opening file: {filepath}")
        self.mode = Mode.NORMAL

    def autocomplete(self):
        """Trigger Groq autocomplete, insert suggestion at cursor, and show in status bar."""
        try:
            filename = self.buffer.filename or ""
            language = detect_language(filename)
            buffer_lines = self.buffer.lines
            cursor_position = self.buffer.cursor
            log_autocomplete_action("START", f"filename={filename}, language={language}, cursor={cursor_position}")
            suggestion = get_groq_suggestion(buffer_lines, cursor_position, language)
            if suggestion:
                # Insert suggestion at cursor, handling multi-line completions
                lines = suggestion.split('\n')
                row, col = cursor_position.row, cursor_position.col
                # Insert first line at cursor
                cmd = InsertCommand(Position(row, col), lines[0])
                self._execute_command(cmd)
                # Insert subsequent lines as new lines
                for i, line in enumerate(lines[1:], 1):
                    # Insert newline after previous line
                    self.buffer.insert_newline(Position(row + i - 1, len(self.buffer.get_line(row + i - 1))))
                    cmd = InsertCommand(Position(row + i, 0), line)
                    self._execute_command(cmd)
                # Move cursor to end of last inserted line
                self.buffer.cursor.row = row + len(lines) - 1
                self.buffer.cursor.col = len(lines[-1])
                self.status_bar.set_message(f"Autocomplete: {suggestion}")
                log_autocomplete_action("SUGGESTION", suggestion)
            else:
                self.status_bar.set_message("No suggestion.")
                log_autocomplete_action("NO_SUGGESTION")
        except Exception as e:
            self.status_bar.set_message(f"Autocomplete error: {e}")
            log_autocomplete_action("ERROR", str(e))

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

    def show_home(self, height, width):
        lines = self.home_text.strip('\n').split('\n')
        start_y = max((height - len(lines)) // 2, 0)
        for i, line in enumerate(lines):
            x = max((width - len(line)) // 2, 0)
            try:
                self.stdscr.addstr(start_y + i, x, line)
            except Exception:
                pass
        # Draw status bar at the bottom
        self._draw_status_bar(height - 1, width)

    def _show_ai_popup(self, text):
        # Show a scrollable popup window for long AI responses
        lines = text.strip().split('\n')
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
