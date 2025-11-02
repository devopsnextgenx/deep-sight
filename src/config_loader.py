"""Configuration loader for Deep Sight."""
import os
import yaml
from pathlib import Path
from typing import Any, Dict


class ConfigLoader:
    """Load and manage application configuration."""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self.load_config()
    
    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if config_path is None:
            # Default config path
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "config.yml"
        
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        
        # Resolve relative paths
        self._resolve_paths()
        return self._config
    
    def _resolve_paths(self):
        """Resolve relative paths in configuration."""
        base_dir = Path(__file__).parent.parent
        
        # Storage paths
        storage = self._config.get('storage', {})
        for key in ['data_folder', 'logs_folder', 'tensor_folder']:
            if key in storage:
                path = storage[key]
                if not os.path.isabs(path):
                    storage[key] = str(base_dir / path)
        
        # TensorFlow model path
        tf_config = self._config.get('tensorflow', {})
        if 'model_path' in tf_config:
            path = tf_config['model_path']
            if not os.path.isabs(path):
                tf_config['model_path'] = str(base_dir / path)
        
        # LLM schema file
        llm_config = self._config.get('llm', {})
        if 'schema_file' in llm_config:
            path = llm_config['schema_file']
            if not os.path.isabs(path):
                llm_config['schema_file'] = str(base_dir / path)
        
        # Logging file
        logging_config = self._config.get('logging', {})
        if 'file' in logging_config:
            path = logging_config['file']
            if not os.path.isabs(path):
                logging_config['file'] = str(base_dir / path)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration."""
        return self._config


# Singleton instance
config = ConfigLoader()
