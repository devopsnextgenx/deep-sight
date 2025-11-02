"""Main processor orchestrator for image processing pipeline."""
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import shutil

from .image_processor import ImageProcessor
from .text_extractor import TextExtractor
from .llm_agent import LLMAgent
from ..models.image_data import ImageData, ImageMetadata
from ..config_loader import config

logger = logging.getLogger(__name__)


class ImageProcessorOrchestrator:
    """Orchestrate the complete image processing pipeline."""
    
    def __init__(self):
        """Initialize all processors."""
        self.image_processor = ImageProcessor()
        self.text_extractor = TextExtractor()
        self.llm_agent = LLMAgent()
    
    def process_image(self, image_path: str, save_to_storage: bool = True) -> ImageData:
        """
        Process a single image through the complete pipeline.
        
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
            
            # Step 1: Resize image
            resized_path, new_size = self.image_processor.resize_image(image_path)
            logger.info(f"Image resized to {new_size}")
            
            # Step 2: Extract text using OCR
            extracted_text = self.text_extractor.extract_text(resized_path)
            logger.info(f"Text extracted: {len(extracted_text)} characters")
            
            # Step 3: Get image description from LLM
            description_result = self.llm_agent.describe_image(resized_path)
            description = description_result.get('description', '')
            logger.info(f"Description generated: {len(description)} characters")
            
            # Step 4: Translate text to Hindi
            hindi_result = self.llm_agent.translate_text(extracted_text, 'hindi')
            translated_hindi = hindi_result.get('translated_text', '')
            
            # Step 5: Translate text to English (if not already in English)
            english_result = self.llm_agent.translate_text(extracted_text, 'english')
            translated_english = english_result.get('translated_text', '')
            
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
            
        except Exception as e:
            logger.error(f"Error saving to storage: {e}")
