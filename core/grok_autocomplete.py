import os
import requests
from dotenv import load_dotenv # type: ignore
from utils.logger import log_autocomplete_action
import re

load_dotenv()

def extract_code_from_response(response_text):
    # Extract code from triple backticks
    match = re.search(r"```(?:[a-zA-Z]+)?\n?(.*?)```", response_text, re.DOTALL)
    if match:
        code = match.group(1).strip()
    else:
        code = response_text.strip()
    # Remove lines that look like explanations or <think> or natural language
    code_lines = [
        line for line in code.splitlines()
        if line.strip() and not line.strip().startswith('<')
        and not line.strip().lower().startswith('okay')
        and not line.strip().endswith('.')
        and not line.strip().lower().startswith('first,')
        and not line.strip().lower().startswith('let me')
        and not line.strip().lower().startswith('the user')
    ]
    return '\n'.join(code_lines).strip()

def get_groq_suggestion(buffer_lines, cursor_position, language, api_key=None, custom_prompt=None):
    """
    Calls the Groq API (OpenAI-compatible) to get an autocomplete suggestion.
    buffer_lines: List[str] - lines of the current buffer
    cursor_position: Position - current cursor position (row, col)
    language: str - detected programming language
    api_key: str - Groq API key (optional, can use env var)
    custom_prompt: str - Optional custom prompt to use instead of the default
    Returns: str - suggestion text
    """
    log_autocomplete_action("GROQ_API_CALL_START", f"language={language}, cursor={cursor_position}")
    if api_key is None:
        api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        log_autocomplete_action("GROQ_API_KEY_MISSING")
        raise ValueError("Groq API key not set. Set GROQ_API_KEY environment variable or .env file.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # Split buffer at cursor and insert |CURSOR| marker
    before = '\n'.join(buffer_lines[:cursor_position.row])
    if before:
        before += '\n'
    before += buffer_lines[cursor_position.row][:cursor_position.col]
    after = buffer_lines[cursor_position.row][cursor_position.col:]
    if cursor_position.row + 1 < len(buffer_lines):
        after += '\n' + '\n'.join(buffer_lines[cursor_position.row+1:])
    content = before + '|CURSOR|' + after

    if custom_prompt:
        prompt = custom_prompt
    else:
        prompt = (
            f"Complete the following {language} code at the |CURSOR| marker.\n"
            f"Return ONLY the code that should be inserted at the cursor, inside a single code block (triple backticks). "
            f"Do NOT include any explanation, commentary, or text except code.\n"
            f"Code:\n{content}\n"
            f"---"
        )
    data = {
        "model": "mistral-saba-24b",
        "messages": [
            {"role": "system", "content": "You are a helpful code completion engine."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1024,  # Increased for multi-line completions
        "temperature": 0.2
    }
    log_autocomplete_action("GROQ_API_REQUEST", f"url={url}, data={str(data)[:200]}")
    response = requests.post(url, json=data, headers=headers)
    log_autocomplete_action("GROQ_API_RESPONSE_STATUS", str(response.status_code))
    try:
        response.raise_for_status()
    except Exception:
        log_autocomplete_action("GROQ_API_ERROR", response.text)
        raise
    log_autocomplete_action("GROQ_API_SUCCESS")
    choices = response.json().get("choices", [])
    if choices:
        raw = choices[0]["message"]["content"].strip()
        code = extract_code_from_response(raw)
        log_autocomplete_action("GROQ_API_COMPLETION_RECEIVED", code)
        return code
    log_autocomplete_action("GROQ_API_NO_COMPLETION")
    return "" 
