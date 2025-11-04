"""Data models for image processing."""
from datetime import datetime
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field


class ImageMetadata(BaseModel):
    """Metadata for processed images."""
    model_name: str
    datetime: str = Field(default_factory=lambda: datetime.now().isoformat())
    processing_time: float = 0.0
    image_size: Dict[str, int] = Field(default_factory=dict)
    original_path: Optional[str] = None


class ImageData(BaseModel):
    """Complete image processing data."""
    image_name: str
    extracted_text: str = ""
    translated_text_hindi: str = ""
    translated_text_english: str = ""
    description: str = ""
    # New structured description fields
    description_text: str = ""  # Text found in image
    description_scene: str = ""  # Scene description
    description_context: str = ""  # Context description
    metadata: ImageMetadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()


class BatchProgress(BaseModel):
    """Batch processing progress tracker."""
    batch_id: str
    folder_path: str
    total_images: int
    completed_images: int = 0
    failed_images: int = 0
    status: str = "pending"  # pending, processing, completed, failed
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    processed_files: list[str] = Field(default_factory=list)
    failed_files: list[str] = Field(default_factory=list)
    
    @property
    def pending_images(self) -> int:
        """Get number of pending images."""
        return self.total_images - self.completed_images - self.failed_images
    
    @property
    def progress_percentage(self) -> float:
        """Get progress percentage."""
        if self.total_images == 0:
            return 0.0
        return (self.completed_images / self.total_images) * 100


class ProcessingRequest(BaseModel):
    """Request model for image processing."""
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    save_to_storage: bool = True


class BatchProcessingRequest(BaseModel):
    """Request model for batch processing."""
    folder_path: str
    recursive: bool = False
