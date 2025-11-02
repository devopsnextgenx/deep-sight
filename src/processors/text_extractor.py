"""Text extraction from images using TensorFlow."""
import logging
from typing import Optional
import numpy as np

from ..config_loader import config

logger = logging.getLogger(__name__)


class TextExtractor:
    """Extract text from images using TensorFlow OCR."""
    
    def __init__(self):
        """Initialize text extractor with configured model."""
        self.model_path = config.get('tensorflow.model_path')
        self.model_type = config.get('tensorflow.model_type', 'keras-ocr')
        self.confidence_threshold = config.get('tensorflow.confidence_threshold', 0.5)
        self.pipeline = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize OCR model based on configuration."""
        try:
            if self.model_type == 'keras-ocr':
                self._initialize_keras_ocr()
            elif self.model_type == 'tesseract':
                self._initialize_tesseract()
            else:
                logger.warning(f"Unknown model type: {self.model_type}, falling back to keras-ocr")
                self._initialize_keras_ocr()
        except Exception as e:
            logger.error(f"Error initializing OCR model: {e}")
            logger.info("OCR model will be initialized on first use")
    
    def _initialize_keras_ocr(self):
        """Initialize Keras OCR pipeline."""
        try:
            import keras_ocr
            self.pipeline = keras_ocr.pipeline.Pipeline()
            logger.info("Keras OCR pipeline initialized successfully")
        except ImportError:
            logger.error("keras-ocr not installed. Install with: pip install keras-ocr")
        except Exception as e:
            logger.error(f"Error initializing Keras OCR: {e}")
    
    def _initialize_tesseract(self):
        """Initialize Tesseract OCR."""
        try:
            import pytesseract
            # Test if tesseract is available
            pytesseract.get_tesseract_version()
            self.pipeline = pytesseract
            logger.info("Tesseract OCR initialized successfully")
        except ImportError:
            logger.error("pytesseract not installed. Install with: pip install pytesseract")
        except Exception as e:
            logger.error(f"Error initializing Tesseract: {e}")
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text string
        """
        try:
            if self.pipeline is None:
                self._initialize_model()
            
            if self.model_type == 'keras-ocr':
                return self._extract_with_keras_ocr(image_path)
            elif self.model_type == 'tesseract':
                return self._extract_with_tesseract(image_path)
            else:
                logger.warning("No OCR model available, returning empty string")
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting text from {image_path}: {e}")
            return ""
    
    def _extract_with_keras_ocr(self, image_path: str) -> str:
        """Extract text using Keras OCR."""
        try:
            import keras_ocr
            
            # Read image
            image = keras_ocr.tools.read(image_path)
            
            # Perform prediction
            predictions = self.pipeline.recognize([image])[0]
            
            # Extract text with confidence filtering
            texts = []
            for text, box in predictions:
                # keras-ocr doesn't provide confidence directly, so we use all results
                texts.append(text)
            
            result = " ".join(texts)
            logger.info(f"Extracted {len(texts)} text elements from image")
            return result
            
        except Exception as e:
            logger.error(f"Error in Keras OCR extraction: {e}")
            return ""
    
    def _extract_with_tesseract(self, image_path: str) -> str:
        """Extract text using Tesseract OCR."""
        try:
            import pytesseract
            from PIL import Image
            
            # Read image
            image = Image.open(image_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            logger.info(f"Extracted text using Tesseract: {len(text)} characters")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error in Tesseract extraction: {e}")
            return ""
    
    def extract_text_with_details(self, image_path: str) -> dict:
        """
        Extract text with detailed information.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with text and metadata
        """
        text = self.extract_text(image_path)
        return {
            'text': text,
            'char_count': len(text),
            'word_count': len(text.split()),
            'model_type': self.model_type
        }
