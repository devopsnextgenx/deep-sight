"""Test script to verify all imports work correctly."""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all module imports."""
    print("Testing imports...\n")
    
    try:
        print("✓ Testing config_loader...")
        from src.config_loader import config
        print(f"  Config loaded: {type(config)}")
        
        print("\n✓ Testing models...")
        from src.models.image_data import ImageData, ImageMetadata, BatchProgress
        print(f"  Models imported successfully")
        
        print("\n✓ Testing processors...")
        from src.processors.image_processor import ImageProcessor
        from src.processors.text_extractor import TextExtractor
        from src.processors.llm_agent import LLMAgent
        from src.processors.processor import ImageProcessorOrchestrator
        from src.processors.batch_processor import BatchProcessor
        print(f"  All processors imported successfully")
        
        print("\n✓ Testing API...")
        from src.api.main import app
        print(f"  FastAPI app imported successfully")
        
        print("\n✅ All imports successful!")
        print("\nConfiguration check:")
        print(f"  API Port: {config.get('app.api_port')}")
        print(f"  UI Port: {config.get('app.ui_port')}")
        print(f"  Ollama Model: {config.get('ollama.model')}")
        print(f"  Image Max Size: {config.get('image.max_width')}x{config.get('image.max_height')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
