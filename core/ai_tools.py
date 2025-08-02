import os
from core.ai_models import model_manager
from core.autocomplete import get_ai_suggestion, get_ai_chat_response
from utils.position import Position

# Helper to call AI with a custom prompt and input
def ai_custom_prompt(buffer_lines, cursor_position, prompt, language=None):
    try:
        content = '\n'.join(buffer_lines)
        language = language or 'python'
        full_prompt = f"{prompt}\n\nCode:\n{content}\n---"
        result = get_ai_suggestion(buffer_lines, cursor_position, language, custom_prompt=full_prompt)
        if not result:
            return f"Error: No response from AI model. Please check your API keys and model configuration."
        return result
    except Exception as e:
        return f"Error in AI custom prompt: {str(e)}"

# Model switching functions
def get_available_models():
    """Get list of available AI models"""
    return model_manager.get_available_models()

def get_current_model():
    """Get current AI model name"""
    return model_manager.get_current_model()

def set_current_model(model_name):
    """Set current AI model"""
    success = model_manager.set_current_model(model_name)
    if success:
        return f"Switched to {model_name} model"
    else:
        available = model_manager.get_available_models()
        return f"Model '{model_name}' not available. Available models: {available}"

def debug_ai_status():
    """Debug AI model status"""
    try:
        available = get_available_models()
        current = get_current_model()
        return f"Available models: {available}\nCurrent model: {current}\nAPI Keys: GROQ_API_KEY={'✓' if os.environ.get('GROQ_API_KEY') else '✗'}, GEMINI_API_KEY={'✓' if os.environ.get('GEMINI_API_KEY') else '✗'}"
    except Exception as e:
        return f"Error getting AI status: {str(e)}"

# AI Tool Functions
def ai_refactor(buffer_lines, cursor_position, language=None):
    """Refactor code for readability and efficiency"""
    prompt = "Refactor this code for readability and efficiency."
    return ai_custom_prompt(buffer_lines, cursor_position, prompt, language)

def ai_doc(buffer_lines, cursor_position, language=None):
    """Generate documentation for code"""
    prompt = "Generate a Python docstring or inline comments for this code."
    return get_ai_chat_response(buffer_lines, prompt)

def ai_explain(buffer_lines, cursor_position, language=None):
    """Explain what the code does"""
    prompt = "Explain what this code does in simple terms."
    return get_ai_chat_response(buffer_lines, prompt)

def ai_testgen(buffer_lines, cursor_position, language=None):
    """Generate unit tests for code"""
    prompt = "Write a pytest unit test for this function."
    return ai_custom_prompt(buffer_lines, cursor_position, prompt, language)

def ai_review(buffer_lines, cursor_position, language=None):
    """Review code and suggest improvements"""
    prompt = "Review this code and suggest improvements or point out bugs."
    return get_ai_chat_response(buffer_lines, prompt)

def ai_nl2code(instruction, language='python'):
    """Convert natural language to code"""
    try:
        prompt = f"Write {language} code to: {instruction}"
        result = ai_custom_prompt([""], Position(0, 0), prompt, language)
        if not result:
            return f"Error: No response from AI model. Please check your API keys and model configuration."
        return result
    except Exception as e:
        return f"Error in nl2code: {str(e)}"

def ai_translate(buffer_lines, cursor_position, target_language):
    """Translate code to another language"""
    prompt = f"Translate this code to {target_language}."
    return ai_custom_prompt(buffer_lines, cursor_position, prompt, target_language)

def ai_search(query, project_files=None):
    """
    Semantic code search using current AI model. Finds all .py files, reads up to 100 lines from each, and sends the query and code context to AI.
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
    return get_ai_chat_response([], prompt)

def ai_commitmsg(diff):
    """Generate commit message from diff"""
    prompt = f"Write a concise git commit message for these changes:\n{diff}"
    return ai_custom_prompt([diff], Position(0, 0), prompt, 'text')

def ai_chat(history, user_message):
    """Interactive chat assistant"""
    prompt = f"You are a helpful programming assistant. {user_message}"
    return ai_custom_prompt([""], Position(0, 0), prompt, 'text')

def ai_snippet(description, language='python'):
    """Generate code snippet from description"""
    prompt = f"Write a code snippet for: {description} in {language}"
    return ai_custom_prompt([""], Position(0, 0), prompt, language)

# Backward compatibility functions
def groq_custom_prompt(buffer_lines, cursor_position, prompt, language=None):
    """Backward compatibility function"""
    return ai_custom_prompt(buffer_lines, cursor_position, prompt, language) 