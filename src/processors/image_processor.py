"""Image processing utilities."""
import os
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional
import logging

from ..config_loader import config

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Process and resize images for analysis."""
    
    def __init__(self):
        """Initialize image processor with config."""
        self.max_width = config.get('image.max_width', 1024)
        self.max_height = config.get('image.max_height', 1024)
        self.maintain_aspect_ratio = config.get('image.maintain_aspect_ratio', True)
        self.quality = config.get('image.quality', 95)
        self.format = config.get('image.format', 'JPEG')
    
    def resize_image(self, image_path: str, output_path: Optional[str] = None) -> Tuple[str, Tuple[int, int]]:
        """
        Resize image to configured dimensions.
        
        Args:
            image_path: Path to input image
            output_path: Optional output path, if None returns temp path
            
        Returns:
            Tuple of (output_path, (width, height))
        """
        try:
            img = Image.open(image_path)
            original_size = img.size
            
            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate new dimensions
            if self.maintain_aspect_ratio:
                img.thumbnail((self.max_width, self.max_height), Image.Resampling.LANCZOS)
            else:
                img = img.resize((self.max_width, self.max_height), Image.Resampling.LANCZOS)
            
            new_size = img.size
            
            # Save resized image
            if output_path is None:
                output_path = self._get_temp_path(image_path)
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, format=self.format, quality=self.quality)
            
            logger.info(f"Resized image from {original_size} to {new_size}")
            return output_path, new_size
            
        except Exception as e:
            logger.error(f"Error resizing image {image_path}: {e}")
            raise
    
    def _get_temp_path(self, original_path: str) -> str:
        """Generate temporary path for resized image."""
        storage_folder = config.get('storage.data_folder', './data')
        temp_folder = Path(storage_folder) / 'temp'
        temp_folder.mkdir(parents=True, exist_ok=True)
        
        filename = Path(original_path).name
        return str(temp_folder / f"resized_{filename}")
    
    def validate_image(self, image_path: str) -> bool:
        """
        Validate if file is a valid image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if valid image, False otherwise
        """
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.warning(f"Invalid image {image_path}: {e}")
            return False
    
    def get_image_info(self, image_path: str) -> dict:
        """
        Get image information.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with image info
        """
        try:
            with Image.open(image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size_bytes': os.path.getsize(image_path)
                }
        except Exception as e:
            logger.error(f"Error getting image info for {image_path}: {e}")
            return {}
