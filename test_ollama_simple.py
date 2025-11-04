#!/usr/bin/env python3
"""Simple test for Ollama connection and basic translation."""

import sys
import logging
from pathlib import Path
import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config_loader import config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ollama_connection():
    """Test direct connection to Ollama."""
    try:
        host = config.get('ollama.host', 'localhost')
        port = config.get('ollama.port', 11434)
        base_url = f"http://{host}:{port}"
        
        print(f"Testing connection to {base_url}")
        
        # Test connection
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        print(f"Connection status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            print(f"Available models: {models}")
        
        # Test simple generate request
        model = config.get('ollama.lmodel', 'llama3.1:latest')
        print(f"\nTesting simple generation with model: {model}")
        
        payload = {
            'model': model,
            'prompt': 'Translate "Hello" to Hindi. Only provide the translation.',
            'stream': False,
            'options': {
                'temperature': 0.3,
                'num_predict': 50
            }
        }
        
        print("Sending request...")
        response = requests.post(
            f"{base_url}/api/generate",
            json=payload,
            timeout=30  # Short timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            translated = result.get('response', '').strip()
            print(f"Translation result: '{translated}'")
        else:
            print(f"Request failed: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.ConnectionError:
        print("Connection error - Ollama may not be running")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ollama_connection()