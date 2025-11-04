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
        self.model = model
        self.host = config.get('ollama.host', 'localhost')
        self.port = config.get('ollama.port', 11434)
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
    
    def _fallback_describe_image(self, image_base64: str) -> Dict[str, Any]:
        """
        Fallback method to get description without JSON format.
        
        Args:
            image_base64: Base64 encoded image
            
        Returns:
            Dictionary with structured description data
        """
        try:
            # Simpler prompt without JSON format requirement
            prompt = """Analyze this image and provide the following information:

1. TEXT: Any readable text found in the image (write "None" if no text visible)
2. DESCRIPTION: Detailed description of the image content and visual elements
3. SCENE: Overall scene or setting (e.g., indoor, outdoor, office, street, etc.)
4. CONTEXT: Context or situation depicted (e.g., business meeting, advertisement, etc.)

Please provide clear, concise answers for each category."""
            
            # Prepare request without JSON format
            payload = {
                'model': self.model,
                'prompt': prompt,
                'images': [image_base64],
                'stream': False,
                'options': {
                    'temperature': self.temperature,
                    'num_predict': min(self.max_tokens, 1024)  # Reduce token limit for faster response
                }
            }
            
            # Use shorter timeout for fallback
            timeout = min(self.timeout, 250)
            
            logger.info(f"Making fallback request with {timeout}s timeout")
            
            # Make request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result.get('response', '').strip()
                
                if llm_response:
                    # Parse the structured text response
                    parsed_data = self._parse_text_response(llm_response)
                    
                    logger.info("Generated description using fallback method")
                    
                    return {
                        **parsed_data,
                        'model': self.model,
                        'success': True,
                        'raw_response': llm_response,
                        'method': 'fallback'
                    }
                else:
                    logger.warning("Empty response from fallback method")
                    return self._create_empty_response("Empty response from LLM")
            else:
                logger.error(f"Fallback request failed: {response.status_code}")
                return self._create_empty_response(f"HTTP {response.status_code}: {response.text}")
            
        except requests.exceptions.Timeout:
            logger.error(f"Fallback method timed out after {timeout}s")
            return self._create_empty_response("Request timed out")
        except Exception as e:
            logger.error(f"Error in fallback describe image: {e}")
            return self._create_empty_response(f"Fallback error: {str(e)}")
    
    def _parse_text_response(self, response: str) -> Dict[str, str]:
        """
        Parse text response to extract structured data.
        
        Args:
            response: Raw text response from LLM
            
        Returns:
            Dictionary with extracted data
        """
        data = {
            'text': '',
            'description': '',
            'scene': '',
            'context': ''
        }
        
        # Split response into lines and look for patterns
        lines = response.split('\n')
        current_key = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for section headers
            if line.upper().startswith('1. TEXT:') or line.upper().startswith('TEXT:'):
                if current_key and current_content:
                    data[current_key] = ' '.join(current_content).strip()
                current_key = 'text'
                current_content = [line.split(':', 1)[1].strip() if ':' in line else '']
            elif line.upper().startswith('2. DESCRIPTION:') or line.upper().startswith('DESCRIPTION:'):
                if current_key and current_content:
                    data[current_key] = ' '.join(current_content).strip()
                current_key = 'description'
                current_content = [line.split(':', 1)[1].strip() if ':' in line else '']
            elif line.upper().startswith('3. SCENE:') or line.upper().startswith('SCENE:'):
                if current_key and current_content:
                    data[current_key] = ' '.join(current_content).strip()
                current_key = 'scene'
                current_content = [line.split(':', 1)[1].strip() if ':' in line else '']
            elif line.upper().startswith('4. CONTEXT:') or line.upper().startswith('CONTEXT:'):
                if current_key and current_content:
                    data[current_key] = ' '.join(current_content).strip()
                current_key = 'context'
                current_content = [line.split(':', 1)[1].strip() if ':' in line else '']
            elif current_key:
                # Continue previous section
                current_content.append(line)
        
        # Don't forget the last section
        if current_key and current_content:
            data[current_key] = ' '.join(current_content).strip()
        
        # Clean up "None" responses
        for key, value in data.items():
            if value.lower() in ['none', 'n/a', 'not applicable', 'no text', 'no text visible']:
                data[key] = ''
        
        # If parsing failed, put everything in description
        if not any(data.values()) and response:
            data['description'] = response
        
        return data
    
    def _create_empty_response(self, error_msg: str) -> Dict[str, Any]:
        """
        Create empty response structure for error cases.
        
        Args:
            error_msg: Error message to include
            
        Returns:
            Empty response dictionary
        """
        return {
            'text': '',
            'description': '',
            'scene': '',
            'context': '',
            'model': self.model,
            'success': False,
            'error': error_msg
        }

    def _validate_description_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize description response data.
        
        Args:
            data: Raw data to validate
            
        Returns:
            Validated and normalized data
        """
        required_keys = ['text', 'description', 'scene', 'context']
        validated_data = {}
        
        for key in required_keys:
            value = data.get(key, '')
            # Ensure string type and handle None values
            if value is None:
                value = ''
            elif not isinstance(value, str):
                value = str(value)
            validated_data[key] = value.strip()
        
        return validated_data
    
    def describe_image(self, image_path: str) -> Dict[str, Any]:
        """
        Generate structured description for an image using LLM.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with structured description containing text, description, scene, and context
        """
        try:
            # Check connection first
            if not self.check_connection():
                logger.error("Ollama service not available")
                return self._create_empty_response("Ollama service not available")
            
            # Encode image
            image_base64 = self._encode_image(image_path)
            
            logger.info(f"Requesting structured description for image with model {self.model}")
            
            # Use the fallback method directly as it's more reliable
            # The JSON format parameter seems to cause issues with some models
            return self._fallback_describe_image(image_base64)
                
        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            return self._create_empty_response("Request timed out")
        except requests.exceptions.ConnectionError:
            logger.error("Connection error - Ollama service may not be running")
            return self._create_empty_response("Connection error - Ollama service may not be running")
        except Exception as e:
            logger.error(f"Error describing image: {e}")
            return self._create_empty_response(str(e))
    
    def describe_image_x(self, image_path: str) -> Dict[str, Any]:
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
    
    def translate_text(self, target_language: str, text: str, text_context: str, scene: str) -> Dict[str, Any]:
        """
        Translate text to target language using LLM. Test might be in English alphabets but phonatically in another language.
        So translation should consider that. If text is in different script, translate accordingly.
        Target language can be 'hindi', 'english', etc. and its script should be considered to produce accurate translation.
        
        Args:
            text: Text to translate
            target_language: Target language (e.g., 'hindi', 'english')
            
        Returns:
            Dictionary with translated text and metadata
        """
        try:
            logger.info(f"Starting translation to {target_language} for text: {len(text) if text else 0} characters")
            
            # Check connection first
            if not self.check_connection():
                logger.error("Ollama service not available for translation")
                return {
                    'original_text': text,
                    'translated_text': text,  # Fallback to original
                    'target_language': target_language,
                    'model': self.model,
                    'success': False,
                    'error': "Ollama service not available"
                }
            
            if not text or not text.strip():
                logger.info(f"Empty text provided for translation to {target_language}")
                return {
                    'original_text': text,
                    'translated_text': '',
                    'target_language': target_language,
                    'success': True
                }
            
            prompt = f"""Translate the following text to {target_language}. 
Only provide the translation, no explanations or additional text.

Context:
{text_context}

Scene:
{scene}

Text to translate:
{text}

Translation:"""
            
            logger.info(f"Requesting translation to {target_language} with model {self.model}")
            
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
                
        except requests.exceptions.Timeout:
            logger.error(f"Translation request timed out after {self.timeout}s for {target_language}")
            return {
                'original_text': text,
                'translated_text': text,  # Fallback to original
                'target_language': target_language,
                'model': self.model,
                'success': False,
                'error': "Request timed out"
            }
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error during translation to {target_language} - Ollama service may not be running")
            return {
                'original_text': text,
                'translated_text': text,  # Fallback to original
                'target_language': target_language,
                'model': self.model,
                'success': False,
                'error': "Connection error"
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
