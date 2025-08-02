import os
from core.ai_models import model_manager
from utils.logger import log_autocomplete_action
from utils.position import Position

def get_ai_suggestion(buffer_lines, cursor_position, language, custom_prompt=None):
    """
    Get AI suggestion using the current model.
    buffer_lines: List[str] - lines of the current buffer
    cursor_position: Position - current cursor position (row, col)
    language: str - detected programming language
    custom_prompt: str - Optional custom prompt to use instead of the default
    Returns: str - suggestion text
    """
    try:
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
        
        result = model_manager.get_completion(prompt, content)
        if not result:
            log_autocomplete_action("AI_SUGGESTION_NO_RESPONSE", "Empty response from model")
            return "Error: No response from AI model. Please check your API keys and model configuration."
        return result
    except Exception as e:
        log_autocomplete_action("AI_SUGGESTION_ERROR", str(e))
        return f"Error: {str(e)}"

def get_ai_chat_response(buffer_lines, user_prompt):
    """
    Get AI chat response using the current model.
    buffer_lines: List[str] - lines of the current buffer (context)
    user_prompt: str - The user instruction/question
    Returns: str - AI's natural language response
    """
    try:
        context = '\n'.join(buffer_lines)
        result = model_manager.get_chat_response(user_prompt, context)
        if not result:
            log_autocomplete_action("AI_CHAT_NO_RESPONSE", "Empty response from model")
            return "Error: No response from AI model. Please check your API keys and model configuration."
        return result
    except Exception as e:
        log_autocomplete_action("AI_CHAT_ERROR", str(e))
        return f"Error: {str(e)}"

# Backward compatibility functions
def get_groq_suggestion(buffer_lines, cursor_position, language, custom_prompt=None):
    """Backward compatibility function - redirects to new system"""
    return get_ai_suggestion(buffer_lines, cursor_position, language, custom_prompt)

def get_groq_chat_response(buffer_lines, user_prompt):
    """Backward compatibility function - redirects to new system"""
    return get_ai_chat_response(buffer_lines, user_prompt) 
