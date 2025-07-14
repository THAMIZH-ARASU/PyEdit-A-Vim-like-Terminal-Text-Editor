#!/usr/bin/env python3
"""
Terminal Text Editor - A complete vim-like text editor implementation
"""

import curses
import sys
from core.editor import Editor

def main(stdscr):
    """Main function for curses application"""
    editor = Editor(stdscr)
    
    # Load file if provided as argument
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if editor.buffer.load_file(filename):
            editor.status_bar.set_message(f"Loaded {filename}")
        else:
            editor.status_bar.set_message(f"New file: {filename}")
            editor.buffer.filename = filename
            
    editor.run()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nEditor closed.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()