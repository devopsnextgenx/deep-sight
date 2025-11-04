#!/usr/bin/env python3
"""Test the fixed translation functionality."""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.processors.llm_agent import LLMAgent
from src.config_loader import config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_translation_fix():
    """Test the translation with our fixes."""
    try:
        # Initialize LLM agent
        llm_agent = LLMAgent(config.get('ollama.lmodel', 'llama3.1:latest'))
        
        print("=== Testing Translation Fix ===")
        
        # Test 1: Empty text (should return immediately)
        print("\n1. Testing empty text:")
        result = llm_agent.translate_text('Hindi', '', 'test context', 'test scene')
        print(f"Result: {result}")
        
        # Test 2: Simple text
        print("\n2. Testing simple text:")
        result = llm_agent.translate_text('Hindi', 'Hello world', 'greeting context', 'casual scene')
        print(f"Result: {result}")
        
        print("\n=== Test Complete ===")
        
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_translation_fix()