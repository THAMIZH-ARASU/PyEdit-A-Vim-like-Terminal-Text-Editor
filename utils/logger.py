import os
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'autocomplete.log')

def log_autocomplete_action(action: str, details: str = ""):
    """Append a timestamped log entry for autocomplete actions."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {action}: {details}\n") 