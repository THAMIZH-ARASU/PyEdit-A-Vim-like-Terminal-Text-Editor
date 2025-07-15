 # PyEdit - Vim-like Terminal Text Editor

PyEdit is a terminal-based text editor inspired by Vim, implemented in Python. It provides a modal editing experience, file explorer with live preview, search, undo/redo, and more—all within your terminal. PyEdit is designed for speed, efficiency, and extensibility, making it a great choice for developers who love working in the terminal.

---

## Features

- **Modal Editing:** Normal, Insert, Visual, Command, Search, and File Explorer modes.
- **Vim-like Keybindings:** Familiar navigation and editing keys (`h/j/k/l`, `i`, `v`, `:`, `/`, etc.).
- **File Explorer Sidebar:** Browse and open files and directories, with a live preview pane that resizes with your terminal.
- **Search:** Powerful in-buffer and file search with regex support.
- **Undo/Redo:** Full undo/redo support for editing operations.
- **Status Bar:** Displays mode, file name, modification status, and cursor position.
- **Command Mode:** Save, quit, open files, and more with `:commands`.
- **Visual Mode:** Select, copy, and delete text visually.
- **AI Autocomplete:** (Optional) Press Tab in insert mode for AI-powered code suggestions (requires configuration).
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
python py_edit.py [filename]
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
<table>
  <tr>
    <th style="text-align:center;">Key</th>
    <th style="text-align:center;">Action</th>
  </tr>
  <tr>
    <td style="text-align:center;">h/j/k/l</td>
    <td style="text-align:center;">Move left/down/up/right</td>
  </tr>
  <tr>
    <td style="text-align:center;">i</td>
    <td style="text-align:center;">Enter insert mode</td>
  </tr>
  <tr>
    <td style="text-align:center;">v</td>
    <td style="text-align:center;">Enter visual mode</td>
  </tr>
  <tr>
    <td style="text-align:center;">:</td>
    <td style="text-align:center;">Enter command mode</td>
  </tr>
  <tr>
    <td style="text-align:center;">/</td>
    <td style="text-align:center;">Enter search mode</td>
  </tr>
  <tr>
    <td style="text-align:center;">e</td>
    <td style="text-align:center;">Open file explorer</td>
  </tr>
  <tr>
    <td style="text-align:center;">x</td>
    <td style="text-align:center;">Delete character</td>
  </tr>
  <tr>
    <td style="text-align:center;">o / O</td>
    <td style="text-align:center;">Insert line below/above</td>
  </tr>
  <tr>
    <td style="text-align:center;">u</td>
    <td style="text-align:center;">Undo</td>
  </tr>
  <tr>
    <td style="text-align:center;">Ctrl+R</td>
    <td style="text-align:center;">Redo</td>
  </tr>
  <tr>
    <td style="text-align:center;">q</td>
    <td style="text-align:center;">Quit</td>
  </tr>
</table>

### Insert Mode
<table>
  <tr>
    <th style="text-align:center;">Key</th>
    <th style="text-align:center;">Action</th>
  </tr>
  <tr>
    <td style="text-align:center;">ESC</td>
    <td style="text-align:center;">Return to normal mode</td>
  </tr>
  <tr>
    <td style="text-align:center;">Enter</td>
    <td style="text-align:center;">New line</td>
  </tr>
  <tr>
    <td style="text-align:center;">Backspace</td>
    <td style="text-align:center;">Delete</td>
  </tr>
  <tr>
    <td style="text-align:center;">Tab</td>
    <td style="text-align:center;">AI autocomplete (if enabled)</td>
  </tr>
</table>

### Visual Mode
<table>
  <tr>
    <th style="text-align:center;">Key</th>
    <th style="text-align:center;">Action</th>
  </tr>
  <tr>
    <td style="text-align:center;">d</td>
    <td style="text-align:center;">Delete selection</td>
  </tr>
  <tr>
    <td style="text-align:center;">y</td>
    <td style="text-align:center;">Copy selection</td>
  </tr>
  <tr>
    <td style="text-align:center;">ESC</td>
    <td style="text-align:center;">Return to normal mode</td>
  </tr>
</table>

### Command Mode (`:`)
<table>
  <tr>
    <th style="text-align:center;">Command</th>
    <th style="text-align:center;">Action</th>
  </tr>
  <tr>
    <td style="text-align:center;">w</td>
    <td style="text-align:center;">Save file</td>
  </tr>
  <tr>
    <td style="text-align:center;">wq</td>
    <td style="text-align:center;">Save and quit</td>
  </tr>
  <tr>
    <td style="text-align:center;">q</td>
    <td style="text-align:center;">Quit</td>
  </tr>
  <tr>
    <td style="text-align:center;">e &lt;file&gt;</td>
    <td style="text-align:center;">Open file</td>
  </tr>
  <tr>
    <td style="text-align:center;">w &lt;file&gt;</td>
    <td style="text-align:center;">Save as file</td>
  </tr>
  <tr>
    <td style="text-align:center;">explorer</td>
    <td style="text-align:center;">Toggle file explorer</td>
  </tr>
  <tr>
    <td style="text-align:center;">help</td>
    <td style="text-align:center;">Show help manual</td>
  </tr>
</table>

### Search Mode (`/`)
- Type pattern, Enter to search, ESC to cancel

## File Explorer (Ranger/Yazi-Style)

The file explorer is a two-pane sidebar:
- **Left pane:** Shows the directory stack and contents. Navigate with your keyboard.
- **Right pane:** Instantly previews the selected file (up to the full width of your terminal).
- **Toggle the explorer:**
  - Press `e` in normal mode
  - Or type `:explorer` in command mode (works from any mode)

### Explorer Navigation Keys
<table>
  <tr>
    <th style="text-align:center;">Key</th>
    <th style="text-align:center;">Action</th>
  </tr>
  <tr>
    <td style="text-align:center;">j / Down</td>
    <td style="text-align:center;">Move down</td>
  </tr>
  <tr>
    <td style="text-align:center;">k / Up</td>
    <td style="text-align:center;">Move up</td>
  </tr>
  <tr>
    <td style="text-align:center;">l / Right / Enter</td>
    <td style="text-align:center;">Enter directory or open file</td>
  </tr>
  <tr>
    <td style="text-align:center;">h / Left / Backspace</td>
    <td style="text-align:center;">Go up to parent directory</td>
  </tr>
  <tr>
    <td style="text-align:center;">r</td>
    <td style="text-align:center;">Refresh file list</td>
  </tr>
  <tr>
    <td style="text-align:center;">q / ESC</td>
    <td style="text-align:center;">Exit file explorer</td>
  </tr>
</table>

- When you select a file and press Enter/l/right, it opens in the editor and exits explorer mode.
- When you select a directory and press Enter/l/right, it enters that directory.
- You can also use `:explorer` at any time to open the explorer.

---

## Screenshots

<p align="center">
  <img src="images/0.png" alt="sample_output">
</p>

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