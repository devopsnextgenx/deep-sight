"""Tests for TextExtractor class."""
import unittest
import sys
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.processors.text_extractor import TextExtractor


class TestTextExtractor(unittest.TestCase):
    """Test cases for TextExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Suppress logging during tests
        logging.disable(logging.CRITICAL)
        
        # Sample test image path (from data folder)
        self.test_image_path = str(project_root / "data" / "470645990_122197173416204766_6105174035824046095_n.jpg")
        self.non_existent_path = "non_existent_image.jpg"
        
    def tearDown(self):
        """Clean up after tests."""
        logging.disable(logging.NOTSET)
    
    @patch('src.processors.text_extractor.config')
    def test_init_with_default_config(self, mock_config):
        """Test TextExtractor initialization with default configuration."""
        mock_config.get.side_effect = lambda key, default=None: {
            'tensorflow.model_path': './tensor/ocr_model',
            'tensorflow.confidence_threshold': 0.5
        }.get(key, default)
        
        with patch('pathlib.Path.exists', return_value=False):
            extractor = TextExtractor()
            
        self.assertEqual(extractor.model_path, './tensor/ocr_model')
        self.assertEqual(extractor.confidence_threshold, 0.5)
        self.assertIsNone(extractor.craft_model)
        self.assertIsNone(extractor.crnn_model)
    
    @patch('src.processors.text_extractor.config')
    @patch('tensorflow.keras.models.load_model')
    @patch('pathlib.Path.exists')
    def test_init_with_tensorflow_models(self, mock_exists, mock_load_model, mock_config):
        """Test TextExtractor initialization with TensorFlow models."""
        mock_config.get.side_effect = lambda key, default=None: {
            'tensorflow.model_path': './tensor/ocr_model',
            'tensorflow.confidence_threshold': 0.5
        }.get(key, default)
        
        mock_exists.return_value = True
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        extractor = TextExtractor()
        
        self.assertEqual(mock_load_model.call_count, 2)  # CRAFT and CRNN models
        self.assertIsNotNone(extractor.craft_model)
        self.assertIsNotNone(extractor.crnn_model)
    
    @patch('src.processors.text_extractor.config')
    @patch('pathlib.Path.exists')
    def test_init_with_fallback_keras_ocr(self, mock_exists, mock_config):
        """Test TextExtractor initialization with keras-ocr fallback."""
        mock_config.get.side_effect = lambda key, default=None: {
            'tensorflow.model_path': './tensor/ocr_model',
            'tensorflow.confidence_threshold': 0.5
        }.get(key, default)
        
        mock_exists.return_value = False
        
        with patch('keras_ocr.pipeline.Pipeline') as mock_pipeline:
            mock_pipeline.return_value = MagicMock()
            extractor = TextExtractor()
            
            self.assertEqual(extractor.fallback_method, 'keras-ocr')
            self.assertIsNotNone(extractor.fallback_pipeline)
    
    @patch('src.processors.text_extractor.config')
    @patch('pathlib.Path.exists')
    def test_init_with_fallback_tesseract(self, mock_exists, mock_config):
        """Test TextExtractor initialization with tesseract fallback."""
        mock_config.get.side_effect = lambda key, default=None: {
            'tensorflow.model_path': './tensor/ocr_model',
            'tensorflow.confidence_threshold': 0.5
        }.get(key, default)
        
        mock_exists.return_value = False
        
        with patch('keras_ocr.pipeline.Pipeline', side_effect=ImportError):
            with patch('pytesseract.get_tesseract_version') as mock_tesseract:
                mock_tesseract.return_value = "5.0.0"
                with patch('pytesseract') as mock_pytesseract:
                    extractor = TextExtractor()
                    
                    self.assertEqual(extractor.fallback_method, 'tesseract')
                    self.assertIsNotNone(extractor.fallback_pipeline)
    
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    @patch('cv2.resize')
    def test_preprocess_image_success(self, mock_resize, mock_cvtColor, mock_imread):
        """Test successful image preprocessing."""
        # Mock image data
        mock_image = np.zeros((1200, 1600, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_cvtColor.return_value = mock_image
        mock_resize.return_value = np.zeros((614, 1024, 3), dtype=np.uint8)
        
        extractor = TextExtractor()
        result = extractor._preprocess_image("test.jpg")
        
        self.assertIsNotNone(result)
        mock_imread.assert_called_once_with("test.jpg")
        mock_cvtColor.assert_called_once()
        mock_resize.assert_called_once()
    
    @patch('cv2.imread')
    def test_preprocess_image_failure(self, mock_imread):
        """Test image preprocessing failure."""
        mock_imread.return_value = None
        
        extractor = TextExtractor()
        result = extractor._preprocess_image("invalid.jpg")
        
        self.assertIsNone(result)
    
    @patch('pathlib.Path.exists')
    def test_extract_text_file_not_found(self, mock_exists):
        """Test text extraction with non-existent file."""
        mock_exists.return_value = False
        
        extractor = TextExtractor()
        result = extractor.extract_text(self.non_existent_path)
        
        self.assertEqual(result, "")
    
    @patch('pathlib.Path.exists')
    @patch.object(TextExtractor, '_preprocess_image')
    def test_extract_text_preprocessing_failure(self, mock_preprocess, mock_exists):
        """Test text extraction with preprocessing failure."""
        mock_exists.return_value = True
        mock_preprocess.return_value = None
        
        extractor = TextExtractor()
        result = extractor.extract_text("test.jpg")
        
        self.assertEqual(result, "")
    
    @patch('pathlib.Path.exists')
    @patch.object(TextExtractor, '_preprocess_image')
    @patch.object(TextExtractor, '_extract_with_tensorflow')
    def test_extract_text_with_tensorflow_models(self, mock_tensorflow_extract, mock_preprocess, mock_exists):
        """Test text extraction using TensorFlow models."""
        mock_exists.return_value = True
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_preprocess.return_value = mock_image
        mock_tensorflow_extract.return_value = "extracted text"
        
        extractor = TextExtractor()
        extractor.craft_model = MagicMock()  # Simulate loaded model
        
        result = extractor.extract_text("test.jpg")
        
        self.assertEqual(result, "extracted text")
        mock_tensorflow_extract.assert_called_once_with(mock_image)
    
    @patch('pathlib.Path.exists')
    @patch.object(TextExtractor, '_preprocess_image')
    @patch.object(TextExtractor, '_extract_with_fallback')
    def test_extract_text_with_fallback(self, mock_fallback_extract, mock_preprocess, mock_exists):
        """Test text extraction using fallback methods."""
        mock_exists.return_value = True
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_preprocess.return_value = mock_image
        mock_fallback_extract.return_value = "fallback text"
        
        extractor = TextExtractor()
        # No TensorFlow models loaded
        extractor.craft_model = None
        extractor.crnn_model = None
        
        result = extractor.extract_text("test.jpg")
        
        self.assertEqual(result, "fallback text")
        mock_fallback_extract.assert_called_once_with("test.jpg")
    
    def test_detect_text_regions_without_model(self):
        """Test text region detection without CRAFT model."""
        extractor = TextExtractor()
        extractor.craft_model = None
        
        mock_image = np.zeros((100, 200, 3), dtype=np.uint8)
        regions = extractor._detect_text_regions(mock_image)
        
        self.assertEqual(len(regions), 1)
        self.assertEqual(regions[0], (0, 0, 200, 100))  # Full image region
    
    @patch('tensorflow.keras.models.load_model')
    def test_detect_text_regions_with_model(self, mock_load_model):
        """Test text region detection with CRAFT model."""
        mock_model = MagicMock()
        mock_model.predict.return_value = [np.random.rand(1, 100, 200, 2)]
        
        extractor = TextExtractor()
        extractor.craft_model = mock_model
        
        mock_image = np.zeros((100, 200, 3), dtype=np.uint8)
        regions = extractor._detect_text_regions(mock_image)
        
        self.assertGreater(len(regions), 0)
        mock_model.predict.assert_called_once()
    
    def test_recognize_text_without_model(self):
        """Test text recognition without CRNN model."""
        extractor = TextExtractor()
        extractor.crnn_model = None
        
        mock_region = np.zeros((32, 128, 3), dtype=np.uint8)
        text = extractor._recognize_text(mock_region)
        
        self.assertEqual(text, "")
    
    @patch('cv2.cvtColor')
    @patch('cv2.resize')
    def test_recognize_text_with_model(self, mock_resize, mock_cvtColor):
        """Test text recognition with CRNN model."""
        mock_model = MagicMock()
        mock_model.predict.return_value = np.random.rand(1, 32, 80)
        
        extractor = TextExtractor()
        extractor.crnn_model = mock_model
        
        mock_region = np.zeros((32, 128, 3), dtype=np.uint8)
        mock_gray = np.zeros((32, 128), dtype=np.uint8)
        mock_resized = np.zeros((32, 128), dtype=np.uint8)
        
        mock_cvtColor.return_value = mock_gray
        mock_resize.return_value = mock_resized
        
        text = extractor._recognize_text(mock_region)
        
        # Should return placeholder text for simplified implementation
        self.assertEqual(text, "extracted_text")
        mock_model.predict.assert_called_once()
    
    @patch.object(TextExtractor, '_detect_text_regions')
    @patch.object(TextExtractor, '_recognize_text')
    def test_extract_with_tensorflow(self, mock_recognize, mock_detect):
        """Test TensorFlow-based text extraction."""
        mock_detect.return_value = [(0, 0, 100, 50), (100, 0, 200, 50)]
        mock_recognize.side_effect = ["text1", "text2"]
        
        extractor = TextExtractor()
        mock_image = np.zeros((100, 200, 3), dtype=np.uint8)
        
        result = extractor._extract_with_tensorflow(mock_image)
        
        self.assertEqual(result, "text1 text2")
        self.assertEqual(mock_recognize.call_count, 2)
    
    @patch('keras_ocr.tools.read')
    def test_extract_with_keras_ocr_fallback(self, mock_read):
        """Test extraction using keras-ocr fallback."""
        mock_pipeline = MagicMock()
        mock_pipeline.recognize.return_value = [[("hello", np.array([[0, 0], [50, 0], [50, 20], [0, 20]])),
                                                  ("world", np.array([[60, 0], [110, 0], [110, 20], [60, 20]]))]]
        
        extractor = TextExtractor()
        extractor.fallback_pipeline = mock_pipeline
        extractor.fallback_method = 'keras-ocr'
        
        mock_image = np.zeros((100, 200, 3), dtype=np.uint8)
        mock_read.return_value = mock_image
        
        result = extractor._extract_with_keras_ocr("test.jpg")
        
        self.assertEqual(result, "hello world")
        mock_pipeline.recognize.assert_called_once()
    
    @patch('pytesseract.image_to_string')
    @patch('PIL.Image.open')
    def test_extract_with_tesseract_fallback(self, mock_open, mock_tesseract):
        """Test extraction using tesseract fallback."""
        mock_image = MagicMock()
        mock_open.return_value = mock_image
        mock_tesseract.return_value = "  extracted text  "
        
        extractor = TextExtractor()
        extractor.fallback_pipeline = MagicMock()
        
        result = extractor._extract_with_tesseract("test.jpg")
        
        self.assertEqual(result, "extracted text")
        mock_tesseract.assert_called_once_with(mock_image)
    
    @patch.object(TextExtractor, 'extract_text')
    def test_extract_text_with_details(self, mock_extract):
        """Test detailed text extraction."""
        mock_extract.return_value = "sample extracted text"
        
        extractor = TextExtractor()
        extractor.craft_model = MagicMock()
        extractor.crnn_model = None
        extractor.fallback_pipeline = MagicMock()
        
        result = extractor.extract_text_with_details("test.jpg")
        
        expected = {
            'text': 'sample extracted text',
            'char_count': 21,
            'word_count': 3,
            'method_used': 'tensorflow',
            'models_available': {
                'craft_model': True,
                'crnn_model': False,
                'fallback': True
            }
        }
        
        self.assertEqual(result, expected)
    
    @patch.object(TextExtractor, 'extract_text')
    def test_extract_text_with_details_fallback(self, mock_extract):
        """Test detailed text extraction using fallback."""
        mock_extract.return_value = "fallback text"
        
        extractor = TextExtractor()
        extractor.craft_model = None
        extractor.crnn_model = None
        extractor.fallback_method = 'tesseract'
        extractor.fallback_pipeline = MagicMock()
        
        result = extractor.extract_text_with_details("test.jpg")
        
        expected = {
            'text': 'fallback text',
            'char_count': 13,
            'word_count': 2,
            'method_used': 'tesseract',
            'models_available': {
                'craft_model': False,
                'crnn_model': False,
                'fallback': True
            }
        }
        
        self.assertEqual(result, expected)
    
    def test_decode_predictions_empty(self):
        """Test prediction decoding with empty input."""
        extractor = TextExtractor()
        result = extractor._decode_predictions(None)
        self.assertEqual(result, "")
        
        result = extractor._decode_predictions([])
        self.assertEqual(result, "")
    
    def test_decode_predictions_with_data(self):
        """Test prediction decoding with data."""
        extractor = TextExtractor()
        mock_predictions = np.random.rand(1, 32, 80)
        result = extractor._decode_predictions(mock_predictions)
        
        # For simplified implementation, should return placeholder
        self.assertEqual(result, "extracted_text")


class TestTextExtractorIntegration(unittest.TestCase):
    """Integration tests for TextExtractor with real data."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        # Suppress logging during tests
        logging.disable(logging.CRITICAL)
        
        self.test_image_path = str(Path(__file__).parent.parent.parent / "data" / "470645990_122197173416204766_6105174035824046095_n.jpg")
    
    def tearDown(self):
        """Clean up after tests."""
        logging.disable(logging.NOTSET)
    
    def test_extract_text_integration(self):
        """Integration test for text extraction."""
        if not Path(self.test_image_path).exists():
            self.skipTest("Test image not found")
        
        # This test will only run if dependencies are available
        try:
            extractor = TextExtractor()
            result = extractor.extract_text(self.test_image_path)
            
            # Should return a string (may be empty if no text detected)
            self.assertIsInstance(result, str)
            
        except ImportError as e:
            self.skipTest(f"Required dependencies not available: {e}")
    
    def test_extract_text_with_details_integration(self):
        """Integration test for detailed text extraction."""
        if not Path(self.test_image_path).exists():
            self.skipTest("Test image not found")
        
        try:
            extractor = TextExtractor()
            result = extractor.extract_text_with_details(self.test_image_path)
            
            # Verify structure
            self.assertIn('text', result)
            self.assertIn('char_count', result)
            self.assertIn('word_count', result)
            self.assertIn('method_used', result)
            self.assertIn('models_available', result)
            
            # Verify types
            self.assertIsInstance(result['text'], str)
            self.assertIsInstance(result['char_count'], int)
            self.assertIsInstance(result['word_count'], int)
            self.assertIsInstance(result['method_used'], str)
            self.assertIsInstance(result['models_available'], dict)
            
        except ImportError as e:
            self.skipTest(f"Required dependencies not available: {e}")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)