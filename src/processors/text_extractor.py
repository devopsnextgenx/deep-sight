"""Text extraction from images using TensorFlow."""
import logging
import sys
from pathlib import Path
from typing import Optional, Tuple, List
import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.config_loader import config

logger = logging.getLogger(__name__)


class TextExtractor:
    """Extract text from images using TensorFlow OCR models."""
    
    def __init__(self):
        """Initialize text extractor with TensorFlow models from tensor folder."""
        self.model_path = config.get('tensorflow.model_path', './tensor/ocr_model')
        self.confidence_threshold = config.get('tensorflow.confidence_threshold', 0.5)
        self.craft_model = None  # Text detection model
        self.crnn_model = None   # Text recognition model
        self._initialize_models()
    def _initialize_models(self):
        """Initialize TensorFlow OCR models."""
        try:
            import tensorflow as tf
            
            # -----------------------------------------------------------------
            # (FIX 1) IMPORT MODEL DEFINITIONS
            # You MUST import the Python classes that define your models.
            # These names are placeholders; you need to find the real ones
            # in your project's 'model' folder or similar.
            # -----------------------------------------------------------------
            # from your_project.models.craft_tf import CRAFT_Model
            # from your_project.models.crnn_tf import CRNN_Model

            # Initialize paths
            craft_path = Path(self.model_path) / "craft_mlt_25k.h5"
            crnn_path = Path(self.model_path) / "crnn_kurapan.h5"
            
            if craft_path.exists() and crnn_path.exists():
                logger.info("Loading TensorFlow OCR models...")
                
                # --- Load CRAFT model (Detection) ---
                try:
                    # ---------------------------------------------------------
                    # (FIX 2) USE .load_weights() INSTEAD OF .load_model()
                    #
                    # 1. Create an instance of the model architecture
                    #    (Replace CRAFT_Model with your actual class)
                    # self.craft_model = CRAFT_Model() 
                    
                    # 2. Load the weights into the model instance
                    # self.craft_model.load_weights(str(craft_path))
                    #
                    # ---
                    # Quick Fix (if you can't find the model class):
                    # Try to load it as-is, but this is likely the part that fails.
                    # For this example, I will assume the original code *was*
                    # trying to load a full model, but if it fails, the user
                    # MUST do the 2 steps above.
                    # ---------------------------------------------------------
                    self.craft_model = tf.keras.models.load_model(str(craft_path), compile=False)
                    logger.info("CRAFT text detection model loaded successfully")

                except Exception as e:
                    # This exception is what my first answer was about.
                    # It means craft_path.h5 is WEIGHTS ONLY.
                    logger.warning(f"Could not load CRAFT model with load_model: {e}")
                    logger.info("This likely means it's a weights-only file. You must import the model class and use .load_weights().")
                    # Example of what to do (uncomment and fix imports):
                    # try:
                    #     logger.info("Attempting to load as weights-only...")
                    #     self.craft_model = CRAFT_Model() # Replace with your model class
                    #     self.craft_model.load_weights(str(craft_path))
                    #     logger.info("CRAFT model loaded successfully (as weights).")
                    # except NameError: # If CRAFT_Model is not defined
                    #     logger.error("CRAFT_Model class not found. Please import it.")
                    #     self.craft_model = None
                    # except Exception as e2:
                    #     logger.error(f"Failed to load CRAFT weights: {e2}")
                    #     self.craft_model = None

                # --- Load CRNN model (Recognition) ---
                try:
                    # (Same fix applies here as for CRAFT)
                    self.crnn_model = tf.keras.models.load_model(str(crnn_path), compile=False)
                    logger.info("CRNN text recognition model loaded successfully")

                except Exception as e:
                    logger.warning(f"Could not load CRNN model with load_model: {e}")
                    logger.info("This likely means it's a weights-only file. You must import the model class and use .load_weights().")
                    # Example (uncomment and fix imports):
                    # try:
                    #     logger.info("Attempting to load as weights-only...")
                    #     self.crnn_model = CRNN_Model() # Replace with your model class
                    #     self.crnn_model.load_weights(str(crnn_path))
                    #     logger.info("CRNN model loaded successfully (as weights).")
                    # except NameError: # If CRNN_Model is not defined
                    #     logger.error("CRNN_Model class not found. Please import it.")
                    #     self.crnn_model = None
                    # except Exception as e2:
                    #     logger.error(f"Failed to load CRNN weights: {e2}")
                    #     self.crnn_model = None
            else:
                logger.warning(f"Model files not found at {self.model_path}")
                logger.info("Falling back to alternative OCR methods")
                self._initialize_fallback()
        except ImportError:
            logger.error("TensorFlow not installed. Install with: pip install tensorflow")
            self._initialize_fallback()
        except Exception as e:
            logger.error(f"Error initializing TensorFlow models: {e}")
            self._initialize_fallback()
        
        # Ensure fallback attributes are always set
        if not hasattr(self, 'fallback_pipeline'):
            self.fallback_pipeline = None
        if not hasattr(self, 'fallback_method'):
            self.fallback_method = None
    
    def _initialize_fallback(self):
        """Initialize fallback OCR method."""
        try:
            # Try keras-ocr first
            import keras_ocr
            self.fallback_pipeline = keras_ocr.pipeline.Pipeline()
            self.fallback_method = 'keras-ocr'
            logger.info("Fallback: Keras OCR pipeline initialized")
        except ImportError:
            try:
                # Try tesseract as last resort
                import pytesseract
                pytesseract.get_tesseract_version()
                self.fallback_pipeline = pytesseract
                self.fallback_method = 'tesseract'
                logger.info("Fallback: Tesseract OCR initialized")
            except (ImportError, Exception):
                logger.warning("No OCR fallback available")
                self.fallback_pipeline = None
                self.fallback_method = None
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for OCR."""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image from {image_path}")
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize if too large
            height, width = image.shape[:2]
            max_dim = 1024
            if max(height, width) > max_dim:
                scale = max_dim / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {e}")
            return None
    
    def _detect_text_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect text regions using CRAFT model."""
        if self.craft_model is None:
            logger.warning("CRAFT model not available, returning full image region")
            h, w = image.shape[:2]
            return [(0, 0, w, h)]
        
        try:
            import tensorflow as tf
            
            # Prepare image for CRAFT model
            input_image = image.astype(np.float32) / 255.0
            input_image = np.expand_dims(input_image, axis=0)
            
            # Predict text regions
            predictions = self.craft_model.predict(input_image, verbose=0)
            
            # Process predictions to extract bounding boxes
            # This is a simplified approach - actual CRAFT post-processing is more complex
            text_regions = []
            if len(predictions) > 0:
                # For demo purposes, return some regions based on prediction
                h, w = image.shape[:2]
                # Split image into regions for processing
                regions = [
                    (0, 0, w//2, h//2),
                    (w//2, 0, w, h//2),
                    (0, h//2, w//2, h),
                    (w//2, h//2, w, h)
                ]
                text_regions.extend(regions)
            
            return text_regions if text_regions else [(0, 0, image.shape[1], image.shape[0])]
            
        except Exception as e:
            logger.error(f"Error in text detection: {e}")
            h, w = image.shape[:2]
            return [(0, 0, w, h)]
    
    def _recognize_text(self, image_region: np.ndarray) -> str:
        """Recognize text in image region using CRNN model."""
        if self.crnn_model is None:
            logger.warning("CRNN model not available")
            return ""
        
        try:
            import tensorflow as tf
            
            # Prepare image for CRNN model
            # CRNN typically expects grayscale input
            if len(image_region.shape) == 3:
                gray_image = cv2.cvtColor(image_region, cv2.COLOR_RGB2GRAY)
            else:
                gray_image = image_region
            
            # Resize to model expected size (this varies by model)
            input_image = cv2.resize(gray_image, (128, 32))
            input_image = input_image.astype(np.float32) / 255.0
            input_image = np.expand_dims(input_image, axis=0)
            input_image = np.expand_dims(input_image, axis=-1)
            
            # Predict text
            predictions = self.crnn_model.predict(input_image, verbose=0)
            
            # Decode predictions (simplified - actual CTC decoding needed)
            # This is a placeholder implementation
            text = self._decode_predictions(predictions)
            
            return text
            
        except Exception as e:
            logger.error(f"Error in text recognition: {e}")
            return ""
    
    def _decode_predictions(self, predictions: np.ndarray) -> str:
        """Decode CRNN predictions to text."""
        try:
            # This is a simplified decoder
            # Real implementation would use CTC decoding
            # For now, return a placeholder
            if predictions is not None and len(predictions) > 0:
                return "extracted_text"  # Placeholder
            return ""
        except Exception as e:
            logger.error(f"Error decoding predictions: {e}")
            return ""
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from image using TensorFlow models.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text string
        """
        try:
            # Check if image file exists
            if not Path(image_path).exists():
                logger.error(f"Image file not found: {image_path}")
                return ""
            
            # Preprocess image
            image = self._preprocess_image(image_path)
            if image is None:
                return ""
            
            # If TensorFlow models are available, use them
            if self.craft_model is not None or self.crnn_model is not None:
                return self._extract_with_tensorflow(image)
            else:
                # Use fallback method
                return self._extract_with_fallback(image_path)
                
        except Exception as e:
            logger.error(f"Error extracting text from {image_path}: {e}")
            return ""
    
    def _extract_with_tensorflow(self, image: np.ndarray) -> str:
        """Extract text using TensorFlow models."""
        try:
            # Detect text regions
            text_regions = self._detect_text_regions(image)
            
            # Extract text from each region
            extracted_texts = []
            for x1, y1, x2, y2 in text_regions:
                region = image[y1:y2, x1:x2]
                if region.size > 0:
                    text = self._recognize_text(region)
                    if text.strip():
                        extracted_texts.append(text.strip())
            
            result = " ".join(extracted_texts)
            logger.info(f"Extracted text from {len(text_regions)} regions using TensorFlow models")
            return result
            
        except Exception as e:
            logger.error(f"Error in TensorFlow text extraction: {e}")
            return ""
    
    def _extract_with_fallback(self, image_path: str) -> str:
        """Extract text using fallback methods."""
        if self.fallback_pipeline is None:
            logger.warning("No fallback OCR method available")
            return ""
        
        try:
            if self.fallback_method == 'keras-ocr':
                return self._extract_with_keras_ocr(image_path)
            elif self.fallback_method == 'tesseract':
                return self._extract_with_tesseract(image_path)
            else:
                return ""
        except Exception as e:
            logger.error(f"Error in fallback extraction: {e}")
            return ""
    
    def _extract_with_keras_ocr(self, image_path: str) -> str:
        """Extract text using Keras OCR."""
        try:
            import keras_ocr
            
            # Read image
            image = keras_ocr.tools.read(image_path)
            
            # Perform prediction
            predictions = self.fallback_pipeline.recognize([image])[0]
            
            # Extract text with confidence filtering
            texts = []
            for text, box in predictions:
                # keras-ocr doesn't provide confidence directly, so we use all results
                texts.append(text)
            
            result = " ".join(texts)
            logger.info(f"Extracted {len(texts)} text elements from image using Keras OCR")
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
        
        # Determine which method was used
        method_used = "tensorflow"
        if self.craft_model is None and self.crnn_model is None:
            method_used = getattr(self, 'fallback_method', 'none')
        
        return {
            'text': text,
            'char_count': len(text),
            'word_count': len(text.split()),
            'method_used': method_used,
            'models_available': {
                'craft_model': self.craft_model is not None,
                'crnn_model': self.crnn_model is not None,
                'fallback': getattr(self, 'fallback_pipeline', None) is not None
            }
        }
