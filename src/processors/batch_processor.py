"""Batch processor for handling multiple images with progress tracking."""
import os
import uuid
import yaml
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .processor import ImageProcessorOrchestrator
from ..models.image_data import BatchProgress, ImageData
from ..config_loader import config

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Process batches of images with progress tracking."""
    
    # Class-level storage for active batches
    _active_batches: Dict[str, BatchProgress] = {}
    _batch_lock = threading.Lock()
    
    def __init__(self):
        """Initialize batch processor."""
        self.processor = ImageProcessorOrchestrator()
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        self.checkpoint_interval = config.get('batch.checkpoint_interval', 5)
    
    @classmethod
    def get_batch_status(cls, batch_id: str) -> Optional[BatchProgress]:
        """Get status of a specific batch."""
        with cls._batch_lock:
            return cls._active_batches.get(batch_id)
    
    @classmethod
    def get_all_batches(cls) -> Dict[str, BatchProgress]:
        """Get all active batches."""
        with cls._batch_lock:
            return cls._active_batches.copy()
    
    def process_folder(self, folder_path: str, recursive: bool = False) -> str:
        """
        Start batch processing of a folder.
        
        Args:
            folder_path: Path to folder containing images
            recursive: Whether to process subdirectories
            
        Returns:
            Batch ID for tracking progress
        """
        folder_path = Path(folder_path).resolve()
        
        if not folder_path.exists() or not folder_path.is_dir():
            raise ValueError(f"Invalid folder path: {folder_path}")
        
        # Generate batch ID
        batch_id = str(uuid.uuid4())
        
        # Get list of images
        images = self._get_images_from_folder(folder_path, recursive)
        
        if not images:
            raise ValueError(f"No images found in folder: {folder_path}")
        
        # Load existing progress if any
        progress_file = self._get_progress_file_path(folder_path)
        processed_files, image_data_map = self._load_progress(progress_file)
        
        # Filter out already processed images
        remaining_images = [img for img in images if img not in processed_files]
        
        # Create batch progress
        batch_progress = BatchProgress(
            batch_id=batch_id,
            folder_path=str(folder_path),
            total_images=len(images),
            completed_images=len(processed_files),
            status="pending",
            processed_files=list(processed_files)
        )
        
        # Store batch
        with self._batch_lock:
            self._active_batches[batch_id] = batch_progress
        
        # Start processing in background thread
        thread = threading.Thread(
            target=self._process_batch_thread,
            args=(batch_id, remaining_images, progress_file, image_data_map),
            daemon=True
        )
        thread.start()
        
        logger.info(f"Started batch {batch_id} with {len(remaining_images)} remaining images")
        return batch_id
    
    def _process_batch_thread(self, batch_id: str, images: List[str], 
                             progress_file: Path, image_data_map: Dict[str, dict]):
        """Process batch in background thread."""
        try:
            # Update status to processing
            with self._batch_lock:
                if batch_id in self._active_batches:
                    self._active_batches[batch_id].status = "processing"
                    self._active_batches[batch_id].start_time = datetime.now().isoformat()
            
            for idx, image_path in enumerate(images):
                try:
                    logger.info(f"Processing {idx+1}/{len(images)}: {image_path}")
                    
                    # Process image
                    image_data = self.processor.process_image(image_path, save_to_storage=True)
                    
                    # Update progress
                    with self._batch_lock:
                        if batch_id in self._active_batches:
                            batch = self._active_batches[batch_id]
                            batch.completed_images += 1
                            batch.processed_files.append(image_path)
                    
                    # Store image data
                    image_data_map[image_path] = image_data.to_dict()
                    
                    # Save checkpoint
                    if (idx + 1) % self.checkpoint_interval == 0:
                        self._save_progress(progress_file, image_data_map)
                        logger.info(f"Checkpoint saved: {idx+1}/{len(images)}")
                    
                except Exception as e:
                    logger.error(f"Error processing {image_path}: {e}")
                    with self._batch_lock:
                        if batch_id in self._active_batches:
                            batch = self._active_batches[batch_id]
                            batch.failed_images += 1
                            batch.failed_files.append(image_path)
            
            # Final save
            self._save_progress(progress_file, image_data_map)
            
            # Update status to completed
            with self._batch_lock:
                if batch_id in self._active_batches:
                    batch = self._active_batches[batch_id]
                    batch.status = "completed"
                    batch.end_time = datetime.now().isoformat()
            
            logger.info(f"Batch {batch_id} completed")
            
        except Exception as e:
            logger.error(f"Batch {batch_id} failed: {e}")
            with self._batch_lock:
                if batch_id in self._active_batches:
                    self._active_batches[batch_id].status = "failed"
                    self._active_batches[batch_id].end_time = datetime.now().isoformat()
    
    def _get_images_from_folder(self, folder_path: Path, recursive: bool) -> List[str]:
        """Get list of image files from folder."""
        images = []
        
        if recursive:
            for ext in self.image_extensions:
                images.extend(str(p) for p in folder_path.rglob(f"*{ext}"))
        else:
            for ext in self.image_extensions:
                images.extend(str(p) for p in folder_path.glob(f"*{ext}"))
        
        return sorted(images)
    
    def _get_progress_file_path(self, folder_path: Path) -> Path:
        """Get path to progress file for folder."""
        folder_name = folder_path.name
        progress_file_name = config.get('batch.progress_file_name', '{folder_name}_progress.yml')
        progress_file_name = progress_file_name.format(folder_name=folder_name)
        return folder_path / progress_file_name
    
    def _load_progress(self, progress_file: Path) -> tuple:
        """Load progress from YAML file."""
        if not progress_file.exists():
            return set(), {}
        
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            processed_files = set(data.keys())
            return processed_files, data
            
        except Exception as e:
            logger.error(f"Error loading progress file: {e}")
            return set(), {}
    
    def _save_progress(self, progress_file: Path, image_data_map: Dict[str, dict]):
        """Save progress to YAML file."""
        try:
            with open(progress_file, 'w', encoding='utf-8') as f:
                yaml.dump(image_data_map, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Progress saved to {progress_file}")
            
        except Exception as e:
            logger.error(f"Error saving progress: {e}")
