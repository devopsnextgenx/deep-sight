#!/usr/bin/env python3
"""Test script for structured description functionality with text translation."""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.processors.llm_agent import LLMAgent
from src.config_loader import config


def test_structured_description():
    """Test the structured description functionality with text translation to English."""
    
    # Initialize LLM agent for image description
    vmodel = config.get('ollama.vmodel', 'qwen3-vl:4b')
    print(f"🤖 Using vision model: {vmodel}")
    
    # Initialize separate LLM agent for translation
    lmodel = config.get('ollama.lmodel', 'gemma3:27b')
    print(f"🌐 Using language model for translation: {lmodel}")
    
    agent = LLMAgent(vmodel)
    translation_agent = LLMAgent(lmodel)
    
    # Check connection first
    print("Checking Ollama connection...")
    if not agent.check_connection():
        print("❌ Ollama service not available. Please ensure Ollama is running.")
        print("   Try: ollama serve")
        return False
    
    print("✅ Ollama connection successful")
    
    # Check if both models are available
    print(f"🔍 Checking if vision model '{vmodel}' is available...")
    print(f"🔍 Checking if language model '{lmodel}' is available...")
    try:
        import requests  # type: ignore
        response = requests.get(f"http://{agent.host}:{agent.port}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]
            
            # Check vision model
            if any(vmodel in name for name in model_names):
                print(f"✅ Vision model '{vmodel}' is available")
            else:
                print(f"⚠️  Vision model '{vmodel}' not found. Available models:")
                for name in model_names:
                    print(f"   - {name}")
                print(f"   Try: ollama pull {vmodel}")
            
            # Check language model
            if any(lmodel in name for name in model_names):
                print(f"✅ Language model '{lmodel}' is available")
            else:
                print(f"⚠️  Language model '{lmodel}' not found. Available models:")
                for name in model_names:
                    print(f"   - {name}")
                print(f"   Try: ollama pull {lmodel}")
        else:
            print(f"⚠️  Could not retrieve model list. Status: {response.status_code}")
    except (requests.exceptions.RequestException, ImportError, KeyError) as e:
        print(f"⚠️  Could not check available models: {e}")
    
    # Test with a sample image from data folder
    data_folder = Path("data/images")
    if not data_folder.exists():
        print("❌ Data/images folder not found")
        return False
    
    # Find the first image file
    image_files = list(data_folder.glob("*.jpg")) + list(data_folder.glob("*.png"))
    if not image_files:
        print("❌ No image files found in data/images folder")
        return False
    
    test_image = image_files[0]
    # test_image = "data/images/470031571_920626546852346_2254552615187365620_n.jpg"
    test_image = "data/images/189246343_116718763909799_5426608247449185417_n.jpg"
    # test_image = "data/images/527273796_765430096064125_1348122522665340777_n.jpg"
    print(f"📸 Testing with image: {test_image}")
    
    # Test structured description
    print("\n🔄 Getting structured description...")
    result = agent.describe_image(str(test_image))
    
    # Print results
    print("\n📋 Results:")
    print("="*50)
    print(f"Success: {result.get('success', False)}")
    print(f"Model: {result.get('model', 'Unknown')}")
    
    translation_success = False
    
    if result.get('success'):
        print(f"\n📝 Text found: '{result.get('text', '')}'")
        print(f"\n🖼️  Description: {result.get('description', '')}")
        print(f"\n🎬 Scene: {result.get('scene', '')}")
        print(f"\n🎯 Context: {result.get('context', '')}")
        
        # Test translation for any non-empty text found
        text_content = result.get('text', '').strip()
        text_context = result.get('context', '').strip()
        scene = result.get('scene', '').strip()
        if text_content:
            print("\n🌐 Translating text to English...")
            translation_result = translation_agent.translate_text('English', text_content, text_context, scene)
            
            print("\n📋 Translation Results:")
            print("-"*30)
            print(f"\nTranslation Success: {translation_result.get('success', False)}")
            print(f"\nTranslation Model: {translation_result.get('model', lmodel)}")
            print(f"\nOriginal Text: '{translation_result.get('original_text', '')}'")
            print(f"\nTranslated Text: '{translation_result.get('translated_text', '')}'")
            print(f"\nTarget Language: {translation_result.get('target_language', '')}")
            
            if not translation_result.get('success'):
                print(f"❌ Translation Error: {translation_result.get('error', 'Unknown error')}")
            else:
                translation_success = True
        else:
            print("\n🔍 No text found in image to translate")
            translation_success = True  # Consider successful if no text to translate
        
        if text_content:
            print("\n🌐 Translating text to Hindi...")
            translation_result = translation_agent.translate_text('Hindi', text_content, text_context, scene)
            
            print("\n📋 Translation Results:")
            print("-"*30)
            print(f"\nTranslation Success: {translation_result.get('success', False)}")
            print(f"\nTranslation Model: {translation_result.get('model', lmodel)}")
            print(f"\nOriginal Text: '{translation_result.get('original_text', '')}'")
            print(f"\nTranslated Text: '{translation_result.get('translated_text', '')}'")
            print(f"\nTarget Language: {translation_result.get('target_language', '')}")
            
            if not translation_result.get('success'):
                print(f"❌ Translation Error: {translation_result.get('error', 'Unknown error')}")
            else:
                translation_success = True
        else:
            print("\n🔍 No text found in image to translate")
            translation_success = True  # Consider successful if no text to translate
        
        # Show raw response for debugging
        # if result.get('raw_response'):
        #     print("\n🔧 Raw JSON Response:")
        #     try:
        #         formatted_json = json.dumps(json.loads(result['raw_response']), indent=2)
        #         print(formatted_json)
        #     except (json.JSONDecodeError, TypeError):
        #         print(result['raw_response'])
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        if result.get('raw_response'):
            print(f"Raw response: {result['raw_response']}")
    
    return result.get('success', False) and translation_success


if __name__ == "__main__":
    print("🚀 Testing Structured Description with Translation Functionality")
    print("="*60)
    
    success = test_structured_description()
    
    print("\n" + "="*60)
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")