import os
import json
from pathlib import Path

class Config:
    """Configuration management for PyEdit"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".pyedit"
        self.config_file = self.config_dir / "config.json"
        self.default_config = {
            "ai_model": "groq",
            "theme": "default",
            "auto_save": False,
            "tab_size": 4,
            "show_line_numbers": True,
            "show_status_bar": True
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with default config to ensure all keys exist
                merged_config = self.default_config.copy()
                merged_config.update(config)
                return merged_config
            else:
                # Create config directory and file
                self.config_dir.mkdir(exist_ok=True)
                self.save_config(self.default_config)
                return self.default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            self.config_dir.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
    
    def get_ai_model(self):
        """Get current AI model preference"""
        return self.get("ai_model", "groq")
    
    def set_ai_model(self, model_name):
        """Set AI model preference"""
        self.set("ai_model", model_name)

# Global config instance
config = Config() 