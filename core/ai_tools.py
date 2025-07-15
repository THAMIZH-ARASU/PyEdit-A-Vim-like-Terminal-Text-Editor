import os
from core.grok_autocomplete import get_groq_suggestion
from utils.position import Position

# Helper to call Groq API with a custom prompt and input

def groq_custom_prompt(buffer_lines, cursor_position, prompt, language=None):
    # Use the same API as autocomplete, but with a custom prompt
    # For now, just join the buffer lines and insert the prompt
    # (You may want to use a more advanced API for chat-style prompts)
    content = '\n'.join(buffer_lines)
    # If language is not provided, default to 'python'
    language = language or 'python'
    # Compose the prompt for Groq
    full_prompt = f"{prompt}\n\nCode:\n{content}\n---"
    # Use get_groq_suggestion as a base (replace with chat API if needed)
    return get_groq_suggestion(buffer_lines, cursor_position, language, custom_prompt=full_prompt)

# 1. Refactor code

def ai_refactor(buffer_lines, cursor_position, language=None):
    prompt = "Refactor this code for readability and efficiency."
    return groq_custom_prompt(buffer_lines, cursor_position, prompt, language)

# 2. Generate documentation

def ai_doc(buffer_lines, cursor_position, language=None):
    prompt = "Generate a Python docstring or inline comments for this code."
    return groq_custom_prompt(buffer_lines, cursor_position, prompt, language)

# 3. Explain code

def ai_explain(buffer_lines, cursor_position, language=None):
    prompt = "Explain what this code does in simple terms."
    return groq_custom_prompt(buffer_lines, cursor_position, prompt, language)

# 4. Generate unit tests

def ai_testgen(buffer_lines, cursor_position, language=None):
    prompt = "Write a pytest unit test for this function."
    return groq_custom_prompt(buffer_lines, cursor_position, prompt, language)

# 5. Code review

def ai_review(buffer_lines, cursor_position, language=None):
    prompt = "Review this code and suggest improvements or point out bugs."
    return groq_custom_prompt(buffer_lines, cursor_position, prompt, language)

# 6. Natural language to code

def ai_nl2code(instruction, language='python'):
    prompt = f"Write {language} code to: {instruction}"
    return groq_custom_prompt([""], Position(0, 0), prompt, language)

# 7. Code translation

def ai_translate(buffer_lines, cursor_position, target_language):
    prompt = f"Translate this code to {target_language}."
    return groq_custom_prompt(buffer_lines, cursor_position, prompt, target_language)

# 8. Smart code search (semantic)

def ai_search(query, project_files):
    # This would require sending the query and some project context
    prompt = f"Find all code related to: {query}"
    # For now, just return a placeholder
    return "[AI search is not yet implemented: would search project files for semantic matches]"

# 9. Commit message generation

def ai_commitmsg(diff):
    prompt = f"Write a concise git commit message for these changes:\n{diff}"
    return groq_custom_prompt([diff], Position(0, 0), prompt, 'text')

# 10. Interactive chat assistant

def ai_chat(history, user_message):
    # For a real chat, you would keep a history and use a chat endpoint
    prompt = f"You are a helpful programming assistant. {user_message}"
    return groq_custom_prompt([""], Position(0, 0), prompt, 'text')

# 11. AI-powered snippet insertion

def ai_snippet(description, language='python'):
    prompt = f"Write a code snippet for: {description} in {language}"
    return groq_custom_prompt([""], Position(0, 0), prompt, language) 