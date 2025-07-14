 # PyEdit - Vim-like Terminal Text Editor

PyEdit is a terminal-based text editor inspired by Vim, implemented in Python. It provides a modal editing experience, file explorer, search, undo/redo, and more, all within your terminal. PyEdit is designed for speed, efficiency, and extensibility, making it a great choice for developers who love working in the terminal.

---

## Features

- **Modal Editing:** Supports Normal, Insert, Visual, Command, Search, and File Explorer modes.
- **Vim-like Keybindings:** Familiar navigation and editing keys (h/j/k/l, i, v, :, /, etc.).
- **File Explorer Sidebar:** Browse and open files and directories from within the editor.
- **Search:** Powerful in-buffer and file search with regex support.
- **Undo/Redo:** Full undo/redo support for editing operations.
- **Status Bar:** Displays mode, file name, modification status, and cursor position.
- **Command Mode:** Save, quit, open files, and more with :commands.
- **Visual Mode:** Select, copy, and delete text visually.
- **Lightweight & Fast:** Minimal dependencies, runs in any terminal with Python and curses.

---

## Installation

### Requirements
- Python 3.7+
- Unix-like terminal (Linux, macOS, or Windows with WSL/compatible terminal)
- Python `curses` module (pre-installed on most Unix systems; for Windows, install `windows-curses` via pip)

### Setup
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd neovim_clone
   ```
2. **(Windows only) Install curses:**
   ```bash
   pip install windows-curses
   ```

---

## Usage

Run the editor from your terminal:

```bash
python main.py [filename]
```
- If `[filename]` is provided, it will open or create that file.
- If not, a new buffer is opened.

---

## Keybindings & Modes

### Modes
- **NORMAL:** Navigation, commands (default)
- **INSERT:** Text input (press `i`)
- **VISUAL:** Select text (press `v`)
- **COMMAND:** Type :commands (press `:`)
- **SEARCH:** Search text (press `/`)
- **FILE EXPLORER:** File browser (press `e` or `:explorer`)

### Normal Mode Keys
| Key         | Action                        |
|-------------|------------------------------|
| h/j/k/l     | Move left/down/up/right      |
| i           | Enter insert mode            |
| v           | Enter visual mode            |
| :           | Enter command mode           |
| /           | Enter search mode            |
| e           | Open file explorer           |
| x           | Delete character             |
| o / O       | Insert line below/above      |
| u           | Undo                         |
| Ctrl+R      | Redo                         |
| q           | Quit                         |

### Insert Mode
| Key         | Action                        |
|-------------|------------------------------|
| ESC         | Return to normal mode        |
| Enter       | New line                     |
| Backspace   | Delete                       |

### Visual Mode
| Key         | Action                        |
|-------------|------------------------------|
| d           | Delete selection             |
| y           | Copy selection               |
| ESC         | Return to normal mode        |

### Command Mode (`:`)
| Command         | Action                        |
|-----------------|------------------------------|
| w               | Save file                    |
| wq              | Save and quit                |
| q               | Quit                         |
| e <file>        | Open file                    |
| w <file>        | Save as file                 |
| explorer        | Toggle file explorer         |
| help            | Show help manual             |

### Search Mode (`/`)
- Type pattern, Enter to search, ESC to cancel

## File Explorer (Ranger/Yazi-Style)

The file explorer is a two-pane sidebar:
- **Left pane:** Shows the directory stack and contents. Navigate with your keyboard.
- **Right pane:** Instantly previews the selected file (first 20 lines).
- **Toggle the explorer:**
  - Press `e` in normal mode
  - Or type `:explorer` in command mode (works from any mode)

### Explorer Navigation Keys
| Key         | Action                                 |
|-------------|----------------------------------------|
| j / Down    | Move down                              |
| k / Up      | Move up                                |
| l / Right / Enter | Enter directory or open file      |
| h / Left / Backspace | Go up to parent directory      |
| r           | Refresh file list                      |
| q / ESC     | Exit file explorer                     |

- When you select a file and press Enter/l/right, it opens in the editor and exits explorer mode.
- When you select a directory and press Enter/l/right, it enters that directory.
- You can also use `:explorer` at any time to open the explorer.

---

## Screenshots

<p align="center">
  <img src="images/1.png" alt="sample_output">
</p>

<p align="center">
  <img src="images/2.png" alt="sample_output">
</p>

<p align="center">
  <img src="images/3.png" alt="sample_output">
</p>

<p align="center">
  <img src="images/4.png" alt="sample_output">
</p>

---

## Contribution

Contributions are welcome! Please open issues or submit pull requests for bug fixes, new features, or improvements.

---

## Credits

- Inspired by Vim and other modal editors.

---

## License

This project is licensed under the MIT License.