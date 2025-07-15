import os
from core.grok_autocomplete import get_groq_suggestion, get_groq_chat_response
from utils.position import Position

# Helper to call Groq API with a custom prompt and input

def groq_custom_prompt(buffer_lines, cursor_position, prompt, language=None):
    content = '\n'.join(buffer_lines)
    language = language or 'python'
    full_prompt = f"{prompt}\n\nCode:\n{content}\n---"
    return get_groq_suggestion(buffer_lines, cursor_position, language, custom_prompt=full_prompt)

# 1. Refactor code

def ai_refactor(buffer_lines, cursor_position, language=None):
    prompt = "Refactor this code for readability and efficiency."
    return groq_custom_prompt(buffer_lines, cursor_position, prompt, language)

# 2. Generate documentation

def ai_doc(buffer_lines, cursor_position, language=None):
    prompt = "Generate a Python docstring or inline comments for this code."
    return get_groq_chat_response(buffer_lines, prompt)

# 3. Explain code

def ai_explain(buffer_lines, cursor_position, language=None):
    prompt = "Explain what this code does in simple terms."
    return get_groq_chat_response(buffer_lines, prompt)

# 4. Generate unit tests

def ai_testgen(buffer_lines, cursor_position, language=None):
    prompt = "Write a pytest unit test for this function."
    return groq_custom_prompt(buffer_lines, cursor_position, prompt, language)

# 5. Code review

def ai_review(buffer_lines, cursor_position, language=None):
    prompt = "Review this code and suggest improvements or point out bugs."
    return get_groq_chat_response(buffer_lines, prompt)

# 6. Natural language to code

def ai_nl2code(instruction, language='python'):
    prompt = f"Write {language} code to: {instruction}"
    return groq_custom_prompt([""], Position(0, 0), prompt, language)

# 7. Code translation

def ai_translate(buffer_lines, cursor_position, target_language):
    prompt = f"Translate this code to {target_language}."
    return groq_custom_prompt(buffer_lines, cursor_position, prompt, target_language)

# 8. Smart code search (semantic)

def ai_search(query, project_files=None):
    """
    Semantic code search using Groq. Finds all .py files, reads up to 100 lines from each, and sends the query and code context to Groq.
    """
    if project_files is None:
        # Recursively find all .py files in the project
        project_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):  # skip hidden files
                    project_files.append(os.path.join(root, file))
    # Read up to 100 lines from each file
    code_context = []
    for path in project_files:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:100]
            code_context.append(f"File: {path}\n" + ''.join(lines))
        except Exception:
            continue
    # Compose the prompt
    prompt = f"Find all code related to: {query}\n\nProject files:\n" + '\n'.join(code_context)
    # Use chat response for natural language output
    return get_groq_chat_response([], prompt)

# 9. Commit message generation

def ai_commitmsg(diff):
    prompt = f"Write a concise git commit message for these changes:\n{diff}"
    return groq_custom_prompt([diff], Position(0, 0), prompt, 'text')

# 10. Interactive chat assistant

def ai_chat(history, user_message):
    prompt = f"You are a helpful programming assistant. {user_message}"
    return groq_custom_prompt([""], Position(0, 0), prompt, 'text')

# 11. AI-powered snippet insertion

def ai_snippet(description, language='python'):
    prompt = f"Write a code snippet for: {description} in {language}"
    return groq_custom_prompt([""], Position(0, 0), prompt, language) 