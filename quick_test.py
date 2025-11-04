#!/usr/bin/env python3
"""Quick test with timeout handling."""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.processors.llm_agent import LLMAgent
from src.config_loader import config


def quick_test():
    """Quick test with timeout."""
    
    model = config.get('ollama.vmodel', 'qwen3-vl:4b')
    agent = LLMAgent(model)
    
    # Override timeout for quick test
    agent.timeout = 30
    
    print(f"🧪 Quick test with {model} (30s timeout)")
    
    # Test with image
    image_path = "data/images/189246343_116718763909799_5426608247449185417_n.jpg"
    
    if not Path(image_path).exists():
        print("❌ Test image not found")
        return
    
    print(f"📸 Testing with: {image_path}")
    
    start_time = time.time()
    result = agent.describe_image(image_path)
    end_time = time.time()
    
    print(f"⏱️  Request took {end_time - start_time:.2f} seconds")
    print(f"✅ Success: {result.get('success', False)}")
    
    if result.get('success'):
        print(f"📄 Method: {result.get('method', 'unknown')}")
        print(f"📝 Text: '{result.get('text', '')}'")
        print(f"🖼️  Description: {result.get('description', '')[:100]}...")
        print(f"🎬 Scene: {result.get('scene', '')}")
        print(f"🎯 Context: {result.get('context', '')}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown')}")
        if result.get('raw_response'):
            print(f"Raw: {result.get('raw_response')[:200]}...")


if __name__ == "__main__":
    quick_test()