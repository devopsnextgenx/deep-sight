#!/usr/bin/env python3
"""Minimal test for vision model."""

import requests  # type: ignore
import base64
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config_loader import config


def test_basic_vision():
    """Test basic vision functionality."""
    
    # Get configuration
    host = config.get('ollama.host', 'localhost')
    port = config.get('ollama.port', 11434)
    model = config.get('ollama.vmodel', 'qwen3-vl:4b')
    
    base_url = f"http://{host}:{port}"
    
    # Find an image
    image_path = Path("data/images/189246343_116718763909799_5426608247449185417_n.jpg")
    if not image_path.exists():
        print("❌ Test image not found")
        return
    
    print(f"🧪 Testing basic vision with {model}")
    print(f"📸 Image: {image_path}")
    
    # Encode image
    try:
        with open(image_path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        print("✅ Image encoded successfully")
    except Exception as e:
        print(f"❌ Failed to encode image: {e}")
        return
    
    # Test 1: Simple description without JSON format
    print("\n🔬 Test 1: Simple description")
    payload1 = {
        'model': model,
        'prompt': 'Describe this image briefly.',
        'images': [image_base64],
        'stream': False,
        'options': {
            'temperature': 0.7,
            'num_predict': 512
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json=payload1,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            description = result.get('response', '').strip()
            print(f"✅ Simple description successful ({len(description)} chars)")
            print(f"Response: {description[:200]}...")
        else:
            print(f"❌ Failed: HTTP {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return
    
    # Test 2: JSON format request
    print("\n🔬 Test 2: JSON format")
    payload2 = {
        'model': model,
        'prompt': 'Describe this image and return the result as JSON with "description" field.',
        'images': [image_base64],
        'stream': False,
        'format': 'json',
        'options': {
            'temperature': 0.7,
            'num_predict': 512
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json=payload2,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            json_response = result.get('response', '').strip()
            print(f"✅ JSON format request successful ({len(json_response)} chars)")
            print(f"Response: {json_response}")
            
            # Try to parse JSON
            try:
                parsed = json.loads(json_response)
                print("✅ Valid JSON response")
                print(f"Parsed: {parsed}")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON: {e}")
                
        else:
            print(f"❌ Failed: HTTP {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")


if __name__ == "__main__":
    test_basic_vision()