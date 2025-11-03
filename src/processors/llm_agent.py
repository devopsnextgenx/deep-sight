"""LLM Agent for image description and text translation."""
import json
import logging
import base64
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import requests
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.config_loader import config

logger = logging.getLogger(__name__)


class LLMAgent:
    """Agent for interacting with Ollama LLM for image and text processing."""
    
    def __init__(self, model):
        """Initialize LLM agent with configuration."""
        self.host = config.get('ollama.host', 'localhost')
        self.port = config.get('ollama.port', 11434)
        self.model = model
        self.temperature = config.get('ollama.temperature', 0.7)
        self.max_tokens = config.get('ollama.max_tokens', 2048)
        self.timeout = config.get('ollama.timeout', 120)
        self.base_url = f"http://{self.host}:{self.port}"
        
        # Load schemas
        self.schemas = self._load_schemas()
    
    def _load_schemas(self) -> Dict[str, Any]:
        """Load LLM response schemas from config."""
        try:
            schema_file = config.get('llm.schema_file')
            with open(schema_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading schemas: {e}")
            return {}
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        try:
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            raise
    
    def describe_image(self, image_path: str) -> Dict[str, Any]:
        """
        Generate description for an image using LLM.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with description and metadata
        """
        try:
            prompt = config.get('llm.description_prompt', 
                              'Describe this image in detail, including objects, scene, colors, and context.')
            
            # Encode image
            image_base64 = self._encode_image(image_path)
            
            # Prepare request
            payload = {
                'model': self.model,
                'prompt': prompt,
                'images': [image_base64],
                'stream': False,
                'options': {
                    'temperature': self.temperature,
                    'num_predict': self.max_tokens
                }
            }
            
            # Make request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                description = result.get('response', '').strip()
                
                logger.info(f"Generated description: {len(description)} characters")
                
                return {
                    'description': description,
                    'model': self.model,
                    'success': True
                }
            else:
                logger.error(f"LLM request failed: {response.status_code} - {response.text}")
                return {
                    'description': '',
                    'model': self.model,
                    'success': False,
                    'error': f"Status code: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error describing image: {e}")
            return {
                'description': '',
                'model': self.model,
                'success': False,
                'error': str(e)
            }
    
    def translate_text(self, text: str, target_language: str) -> Dict[str, Any]:
        """
        Translate text to target language using LLM.
        
        Args:
            text: Text to translate
            target_language: Target language (e.g., 'hindi', 'english')
            
        Returns:
            Dictionary with translated text and metadata
        """
        try:
            if not text or not text.strip():
                return {
                    'original_text': text,
                    'translated_text': '',
                    'target_language': target_language,
                    'success': True
                }
            
            prompt = f"""Translate the following text to {target_language}. 
Only provide the translation, no explanations or additional text.

Text to translate:
{text}

Translation:"""
            
            # Prepare request
            payload = {
                'model': self.model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.3,  # Lower temperature for translation
                    'num_predict': self.max_tokens
                }
            }
            
            # Make request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result.get('response', '').strip()
                
                logger.info(f"Translated text to {target_language}: {len(translated_text)} characters")
                
                return {
                    'original_text': text,
                    'translated_text': translated_text,
                    'target_language': target_language,
                    'model': self.model,
                    'success': True
                }
            else:
                logger.error(f"Translation request failed: {response.status_code}")
                return {
                    'original_text': text,
                    'translated_text': text,  # Fallback to original
                    'target_language': target_language,
                    'model': self.model,
                    'success': False,
                    'error': f"Status code: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return {
                'original_text': text,
                'translated_text': text,  # Fallback to original
                'target_language': target_language,
                'model': self.model,
                'success': False,
                'error': str(e)
            }
    
    def check_connection(self) -> bool:
        """
        Check if Ollama service is available.
        
        Returns:
            True if service is available, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection check failed: {e}")
            return False
