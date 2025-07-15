import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_groq_suggestion(buffer_lines, cursor_position, language, api_key=None):
    """
    Calls the Groq API (OpenAI-compatible) to get an autocomplete suggestion.
    buffer_lines: List[str] - lines of the current buffer
    cursor_position: Position - current cursor position (row, col)
    language: str - detected programming language
    api_key: str - Groq API key (optional, can use env var)
    Returns: str - suggestion text
    """
    print("[Groq] Preparing API call...")
    if api_key is None:
        api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        print("[Groq] API key not found.")
        raise ValueError("Groq API key not set. Set GROQ_API_KEY environment variable or .env file.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    content = "\n".join(buffer_lines)
    char_offset = sum(len(line) + 1 for line in buffer_lines[:cursor_position.row]) + cursor_position.col
    prompt = (
        f"You are a code completion engine. Given the following code and cursor position, suggest the next code completion. "
        f"Language: {language}\n"
        f"Cursor offset: {char_offset}\n"
        f"Code:\n{content}\n"
        f"---\n"
        f"Provide only the code completion, no explanations."
    )
    data = {
        "model": "deepseek-r1-distill-llama-70b",
        "messages": [
            {"role": "system", "content": "You are a helpful code completion engine."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 64,
        "temperature": 0.2
    }
    print("[Groq] Sending request to API...")
    response = requests.post(url, json=data, headers=headers)
    print(f"[Groq] Response status code: {response.status_code}")
    try:
        response.raise_for_status()
    except Exception:
        print("[Groq] API error response:", response.text)
        raise
    print("[Groq] API call successful. Parsing response...")
    choices = response.json().get("choices", [])
    if choices:
        print("[Groq] Completion received.")
        return choices[0]["message"]["content"].strip()
    print("[Groq] No completion found in response.")
    return "" 