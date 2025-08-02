import os
import requests
import re
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from utils.logger import log_autocomplete_action

load_dotenv()

class AIModel(ABC):
    """Abstract base class for AI models"""
    
    def __init__(self, name: str, api_key: Optional[str] = None):
        self.name = name
        self.api_key = api_key or self._get_api_key()
    
    @abstractmethod
    def _get_api_key(self) -> str:
        """Get API key from environment variables"""
        pass
    
    @abstractmethod
    def get_completion(self, prompt: str, context: str = "", **kwargs) -> str:
        """Get code completion from the model"""
        pass
    
    @abstractmethod
    def get_chat_response(self, prompt: str, context: str = "", **kwargs) -> str:
        """Get chat response from the model"""
        pass

class GroqModel(AIModel):
    """Groq API implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Groq", api_key)
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.default_model = "llama3-70b-8192"  # Updated to a more reliable model
    
    def _get_api_key(self) -> str:
        return os.environ.get("GROQ_API_KEY", "")
    
    def get_completion(self, prompt: str, context: str = "", **kwargs) -> str:
        """Get code completion from Groq"""
        log_autocomplete_action("GROQ_API_CALL_START", f"prompt_length={len(prompt)}")
        
        if not self.api_key:
            log_autocomplete_action("GROQ_API_KEY_MISSING")
            raise ValueError("Groq API key not set. Set GROQ_API_KEY environment variable.")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": kwargs.get("model", self.default_model),
            "messages": [
                {"role": "system", "content": "You are a helpful code completion engine."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": kwargs.get("max_tokens", 1024),
            "temperature": kwargs.get("temperature", 0.2)
        }
        
        log_autocomplete_action("GROQ_API_REQUEST", f"url={self.base_url}")
        response = requests.post(self.base_url, json=data, headers=headers)
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
            code = self._extract_code_from_response(raw)
            log_autocomplete_action("GROQ_API_COMPLETION_RECEIVED", code)
            return code
        
        log_autocomplete_action("GROQ_API_NO_COMPLETION")
        return ""
    
    def get_chat_response(self, prompt: str, context: str = "", **kwargs) -> str:
        """Get chat response from Groq"""
        if not self.api_key:
            raise ValueError("Groq API key not set. Set GROQ_API_KEY environment variable.")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        full_prompt = f"{prompt}\n\nCode context:\n{context}" if context else prompt
        
        data = {
            "model": kwargs.get("model", self.default_model),
            "messages": [
                {"role": "system", "content": "You are a helpful programming assistant."},
                {"role": "user", "content": full_prompt}
            ],
            "max_tokens": kwargs.get("max_tokens", 1024),
            "temperature": kwargs.get("temperature", 0.2)
        }
        
        response = requests.post(self.base_url, json=data, headers=headers)
        response.raise_for_status()
        choices = response.json().get("choices", [])
        if choices:
            return choices[0]["message"]["content"].strip()
        return ""
    
    def _extract_code_from_response(self, response_text: str) -> str:
        """Extract code from triple backticks"""
        match = re.search(r"```(?:[a-zA-Z]+)?\n?(.*?)```", response_text, re.DOTALL)
        if match:
            code = match.group(1).strip()
        else:
            code = response_text.strip()
        
        # Remove lines that look like explanations or natural language
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

class GeminiModel(AIModel):
    """Google Gemini API implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Gemini", api_key)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.default_model = "gemini-2.0-flash"
    
    def _get_api_key(self) -> str:
        return os.environ.get("GEMINI_API_KEY", "")
    
    def get_completion(self, prompt: str, context: str = "", **kwargs) -> str:
        """Get code completion from Gemini"""
        log_autocomplete_action("GEMINI_API_CALL_START", f"prompt_length={len(prompt)}")
        
        if not self.api_key:
            log_autocomplete_action("GEMINI_API_KEY_MISSING")
            raise ValueError("Gemini API key not set. Set GEMINI_API_KEY environment variable.")
        
        url = f"{self.base_url}?key={self.api_key}"
        
        data = {
            "contents": [{
                "parts": [{
                    "text": f"You are a helpful code completion engine. {prompt}"
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", 1024),
                "temperature": kwargs.get("temperature", 0.2)
            }
        }
        
        log_autocomplete_action("GEMINI_API_REQUEST", f"url={url}")
        response = requests.post(url, json=data)
        log_autocomplete_action("GEMINI_API_RESPONSE_STATUS", str(response.status_code))
        
        try:
            response.raise_for_status()
        except Exception:
            log_autocomplete_action("GEMINI_API_ERROR", response.text)
            raise
        
        log_autocomplete_action("GEMINI_API_SUCCESS")
        result = response.json()
        
        if "candidates" in result and result["candidates"]:
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            code = self._extract_code_from_response(content)
            log_autocomplete_action("GEMINI_API_COMPLETION_RECEIVED", code)
            return code
        
        log_autocomplete_action("GEMINI_API_NO_COMPLETION")
        return ""
    
    def get_chat_response(self, prompt: str, context: str = "", **kwargs) -> str:
        """Get chat response from Gemini"""
        if not self.api_key:
            raise ValueError("Gemini API key not set. Set GEMINI_API_KEY environment variable.")
        
        url = f"{self.base_url}?key={self.api_key}"
        
        full_prompt = f"{prompt}\n\nCode context:\n{context}" if context else prompt
        
        data = {
            "contents": [{
                "parts": [{
                    "text": f"You are a helpful programming assistant. {full_prompt}"
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", 1024),
                "temperature": kwargs.get("temperature", 0.2)
            }
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        
        if "candidates" in result and result["candidates"]:
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
        return ""
    
    def _extract_code_from_response(self, response_text: str) -> str:
        """Extract code from triple backticks"""
        match = re.search(r"```(?:[a-zA-Z]+)?\n?(.*?)```", response_text, re.DOTALL)
        if match:
            code = match.group(1).strip()
        else:
            code = response_text.strip()
        
        # Remove lines that look like explanations or natural language
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

class AIModelManager:
    """Manages multiple AI models and provides a unified interface"""
    
    def __init__(self):
        self.models: Dict[str, AIModel] = {}
        self.current_model = "groq"
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available models"""
        # Try to initialize Groq
        try:
            groq_key = os.environ.get("GROQ_API_KEY")
            if groq_key:
                self.models["groq"] = GroqModel(groq_key)
        except Exception as e:
            print(f"Failed to initialize Groq model: {e}")
        
        # Try to initialize Gemini
        try:
            gemini_key = os.environ.get("GEMINI_API_KEY")
            if gemini_key:
                self.models["gemini"] = GeminiModel(gemini_key)
        except Exception as e:
            print(f"Failed to initialize Gemini model: {e}")
        
        # Set default model from config or first available
        try:
            from config import config
            preferred_model = config.get_ai_model()
            if preferred_model in self.models:
                self.current_model = preferred_model
            elif self.models:
                self.current_model = list(self.models.keys())[0]
        except:
            if self.models:
                self.current_model = list(self.models.keys())[0]
    
    def get_available_models(self) -> List[str]:
        """Get list of available model names"""
        return list(self.models.keys())
    
    def get_current_model(self) -> str:
        """Get current model name"""
        return self.current_model
    
    def set_current_model(self, model_name: str) -> bool:
        """Set current model"""
        if model_name in self.models:
            self.current_model = model_name
            # Save preference to config
            try:
                from config import config
                config.set_ai_model(model_name)
            except:
                pass
            return True
        return False
    
    def get_current_model_instance(self) -> Optional[AIModel]:
        """Get current model instance"""
        return self.models.get(self.current_model)
    
    def get_completion(self, prompt: str, context: str = "", **kwargs) -> str:
        """Get completion from current model"""
        model = self.get_current_model_instance()
        if not model:
            available = self.get_available_models()
            if not available:
                raise ValueError("No AI models available. Please check your API keys (GROQ_API_KEY, GEMINI_API_KEY).")
            else:
                raise ValueError(f"No AI model available. Available models: {available}")
        return model.get_completion(prompt, context, **kwargs)
    
    def get_chat_response(self, prompt: str, context: str = "", **kwargs) -> str:
        """Get chat response from current model"""
        model = self.get_current_model_instance()
        if not model:
            available = self.get_available_models()
            if not available:
                raise ValueError("No AI models available. Please check your API keys (GROQ_API_KEY, GEMINI_API_KEY).")
            else:
                raise ValueError(f"No AI model available. Available models: {available}")
        return model.get_chat_response(prompt, context, **kwargs)

# Global model manager instance
model_manager = AIModelManager() 