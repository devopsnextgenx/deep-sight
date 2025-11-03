"""Main processor orchestrator for image processing pipeline."""
import time
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import shutil

import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.processors.image_processor import ImageProcessor
from src.processors.text_extractor import TextExtractor
from src.processors.llm_agent import LLMAgent
from src.models.image_data import ImageData, ImageMetadata
from src.config_loader import config

logger = logging.getLogger(__name__)

from src.config_loader import config

class ImageProcessorOrchestrator:
    """Orchestrate the complete image processing pipeline."""
    
    def __init__(self):
        """Initialize all processors."""
        self.image_processor = ImageProcessor()
        self.text_extractor = TextExtractor()
        self.vllm_agent = LLMAgent(config.get('ollama.vmodel', 'qwen3-vl:4b'))
        self.llm_agent = LLMAgent(config.get('ollama.lmodel', 'llama3.1:latest'))
    
    def process_image(self, image_path: str, save_to_storage: bool = True) -> ImageData:
        """
        Process a single image through the complete pipeline.
        
        Pipeline steps:
        1. OCR text extraction on original image (highest quality)
        2. Image resizing for LLM processing (optimized size)
        3. LLM image description (using resized image)
        4. Text translation to Hindi and English
        
        Args:
            image_path: Path to image file
            save_to_storage: Whether to save the image to storage
            
        Returns:
            ImageData object with all processed information
        """
        start_time = time.time()
        image_name = Path(image_path).name
        
        try:
            logger.info(f"Processing image: {image_name}")
            
            # Step 1: Extract text using OCR on ORIGINAL image (better quality)
            extracted_text = self.text_extractor.extract_text(image_path)
            logger.info(f"Text extracted: {len(extracted_text)} characters")
            
            # Step 2: Resize image for LLM processing (smaller, faster)
            resized_path, new_size = self.image_processor.resize_image(image_path)
            logger.info(f"Image resized to {new_size} for LLM processing")
            
            # Step 3: Get image description from LLM
            description_result = self.vllm_agent.describe_image(resized_path)
            description = description_result.get('description', '')
            logger.info(f"Description generated: {len(description)} characters")
            
            # Step 4: Translate text to Hindi
            hindi_result = self.llm_agent.translate_text(extracted_text, 'hindi')
            translated_hindi = hindi_result.get('translated_text', '')
            logger.info(f"Text translated to Hindi: {len(translated_hindi)} characters")
            
            # Step 5: Translate text to English (if not already in English)
            english_result = self.llm_agent.translate_text(extracted_text, 'english')
            translated_english = english_result.get('translated_text', '')
            logger.info(f"Text translated to English: {len(translated_english)} characters")

            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create metadata
            metadata = ImageMetadata(
                model_name=self.llm_agent.model,
                datetime=datetime.now().isoformat(),
                processing_time=processing_time,
                image_size={'width': new_size[0], 'height': new_size[1]},
                original_path=image_path
            )
            
            # Create ImageData object
            image_data = ImageData(
                image_name=image_name,
                extracted_text=extracted_text,
                translated_text_hindi=translated_hindi,
                translated_text_english=translated_english,
                description=description,
                metadata=metadata
            )
            # convert to json and print pretty
            json_data = image_data.to_dict()
            print(f"ImageData: {json.dumps(json_data, indent=2)}")
            logger.info(f"ImageData: {json.dumps(json_data, indent=2)}")
            # Save to storage if requested
            if save_to_storage:
                self._save_to_storage(image_path, resized_path, image_data)
            
            logger.info(f"Image processing completed in {processing_time:.2f}s")
            return image_data
            
        except Exception as e:
            logger.error(f"Error processing image {image_name}: {e}")
            # Return partial data with error
            metadata = ImageMetadata(
                model_name=self.llm_agent.model,
                datetime=datetime.now().isoformat(),
                processing_time=time.time() - start_time,
                original_path=image_path
            )
            return ImageData(
                image_name=image_name,
                metadata=metadata
            )
    
    def _save_to_storage(self, original_path: str, resized_path: str, image_data: ImageData):
        """Save processed image and data to storage."""
        try:
            storage_folder = Path(config.get('storage.data_folder', './data'))
            images_folder = storage_folder / 'images'
            images_folder.mkdir(parents=True, exist_ok=True)
            
            # Copy original image
            dest_path = images_folder / image_data.image_name
            shutil.copy2(original_path, dest_path)
            logger.info(f"Image saved to {dest_path}")
            # Save metadata as JSON
            metadata_path = dest_path.with_suffix('.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(image_data.to_dict(), f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Error saving to storage: {e}")
