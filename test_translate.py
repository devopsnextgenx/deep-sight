#!/usr/bin/env python3
"""Quick test for translation function with improved logging."""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.processors.llm_agent import LLMAgent
from src.config_loader import config

# Set up logging to see all messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_translation():
    """Test the translation function."""
    try:
        # Initialize LLM agent
        llm_agent = LLMAgent(config.get('ollama.lmodel', 'llama3.1:latest'))
        
        # Test text
        test_text = "Hello world"
        
        print("Testing translation function...")
        print(f"Ollama service available: {llm_agent.check_connection()}")
        
        # Test Hindi translation
        print("\n--- Testing Hindi Translation ---")
        result_hindi = llm_agent.translate_text('Hindi', test_text, 'testing context', 'test scene')
        print(f"Result: {result_hindi}")
        
        # Test English translation  
        print("\n--- Testing English Translation ---")
        result_english = llm_agent.translate_text('English', test_text, 'testing context', 'test scene')
        print(f"Result: {result_english}")
        
    except Exception as e:
        print(f"Error during test: {e}")
        logging.error(f"Test error: {e}")

if __name__ == "__main__":
    test_translation()