#!/usr/bin/env python3
"""
Demo script for TextExtractor functionality.
This script demonstrates how to use the TextExtractor to extract text from images.
"""
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.processors.text_extractor import TextExtractor

def setup_logging():
    """Set up logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def demo_text_extraction():
    """Demonstrate text extraction functionality."""
    print("TextExtractor Demo")
    print("=" * 50)
    
    # Initialize the text extractor
    print("Initializing TextExtractor...")
    extractor = TextExtractor()
    
    # Check available models
    print(f"CRAFT model loaded: {extractor.craft_model is not None}")
    print(f"CRNN model loaded: {extractor.crnn_model is not None}")
    fallback_available = getattr(extractor, 'fallback_pipeline', None) is not None
    print(f"Fallback method available: {fallback_available}")
    if fallback_available:
        print(f"Fallback method: {getattr(extractor, 'fallback_method', 'unknown')}")
    
    # Test with sample image from data folder
    data_folder = project_root / "data"
    sample_images = list(data_folder.glob("*.jpg")) + list(data_folder.glob("*.png"))
    
    if not sample_images:
        print("No sample images found in data folder.")
        return
    
    for image_path in sample_images[:3]:  # Process up to 3 images
        print(f"\nProcessing: {image_path.name}")
        print("-" * 30)
        
        try:
            # Extract text
            text = extractor.extract_text(str(image_path))
            print(f"Extracted text: {text if text else '(no text detected)'}")
            
            # Get detailed information
            details = extractor.extract_text_with_details(str(image_path))
            print(f"Character count: {details['char_count']}")
            print(f"Word count: {details['word_count']}")
            print(f"Method used: {details['method_used']}")
            
        except Exception as e:
            print(f"Error processing {image_path.name}: {e}")
    
    print("\nDemo completed!")

def test_model_loading():
    """Test model loading capabilities."""
    print("\nTesting model loading...")
    print("-" * 30)
    
    try:
        extractor = TextExtractor()
        
        # Test model paths
        model_path = Path(extractor.model_path)
        print(f"Model path: {model_path}")
        print(f"Model path exists: {model_path.exists()}")
        
        if model_path.exists():
            craft_path = model_path / "craft_mlt_25k.h5"
            crnn_path = model_path / "crnn_kurapan.h5"
            print(f"CRAFT model file exists: {craft_path.exists()}")
            print(f"CRNN model file exists: {crnn_path.exists()}")
            
            if craft_path.exists():
                print(f"CRAFT model size: {craft_path.stat().st_size / (1024*1024):.1f} MB")
            if crnn_path.exists():
                print(f"CRNN model size: {crnn_path.stat().st_size / (1024*1024):.1f} MB")
        
    except Exception as e:
        print(f"Error testing model loading: {e}")

def main():
    """Main function."""
    setup_logging()
    
    print("Deep Sight TextExtractor Demo")
    print("=" * 60)
    
    # Test model loading
    test_model_loading()
    
    # Demo text extraction
    demo_text_extraction()

if __name__ == "__main__":
    main()