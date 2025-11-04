#!/usr/bin/env python3
"""Debug script to test Ollama connection and model availability."""

import sys
import requests  # type: ignore
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config_loader import config


def debug_ollama():
    """Debug Ollama connection and models."""
    
    # Get configuration
    host = config.get('ollama.host', 'localhost')
    port = config.get('ollama.port', 11434)
    vmodel = config.get('ollama.vmodel', 'qwen3-vl:4b')
    lmodel = config.get('ollama.lmodel', 'gemma3:27b')
    
    base_url = f"http://{host}:{port}"
    
    print("🔧 Ollama Debug Information")
    print("="*50)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Base URL: {base_url}")
    print(f"Vision Model: {vmodel}")
    print(f"Language Model: {lmodel}")
    print()
    
    # Test connection
    print("🔗 Testing connection...")
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Connection successful")
            
            # List available models
            data = response.json()
            models = data.get('models', [])
            
            print(f"\n📋 Available models ({len(models)}):")
            if models:
                for model in models:
                    name = model.get('name', 'Unknown')
                    size = model.get('size', 0)
                    size_mb = size / (1024 * 1024) if size else 0
                    print(f"  - {name} ({size_mb:.1f} MB)")
                
                # Check if required models are available
                model_names = [m.get('name', '') for m in models]
                
                print(f"\n🔍 Checking required models:")
                
                # Check vision model
                vmodel_available = any(vmodel in name for name in model_names)
                if vmodel_available:
                    print(f"  ✅ Vision model '{vmodel}' is available")
                else:
                    print(f"  ❌ Vision model '{vmodel}' not found")
                    print(f"     Try: ollama pull {vmodel}")
                
                # Check language model
                lmodel_available = any(lmodel in name for name in model_names)
                if lmodel_available:
                    print(f"  ✅ Language model '{lmodel}' is available")
                else:
                    print(f"  ❌ Language model '{lmodel}' not found")
                    print(f"     Try: ollama pull {lmodel}")
                
            else:
                print("  No models found")
                print("  Try: ollama pull qwen3-vl:4b")
                
        else:
            print(f"❌ Connection failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed: Cannot connect to Ollama service")
        print("   Make sure Ollama is running:")
        print("   Windows: Start Ollama Desktop app")
        print("   Linux/Mac: ollama serve")
        
    except requests.exceptions.Timeout:
        print("❌ Connection timeout")
        print("   Ollama might be starting up, please wait and try again")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n" + "="*50)


if __name__ == "__main__":
    debug_ollama()