"""FastAPI application for Deep Sight."""
import logging
import os
from pathlib import Path
from typing import Dict, Any
import requests
from io import BytesIO

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..config_loader import config
from ..processors.processor import ImageProcessorOrchestrator
from ..processors.batch_processor import BatchProcessor
from ..models.image_data import ProcessingRequest, BatchProcessingRequest

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Deep Sight API",
    description="Image processing API with OCR, LLM description, and translation",
    version="1.0.0"
)

# Configure CORS
if config.get('app.cors.enabled', True):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.get('app.cors.origins', ["*"]),
        allow_credentials=config.get('app.cors.allow_credentials', True),
        allow_methods=config.get('app.cors.allow_methods', ["*"]),
        allow_headers=config.get('app.cors.allow_headers', ["*"]),
    )

# Initialize processors
processor = ImageProcessorOrchestrator()
batch_processor = BatchProcessor()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Deep Sight API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "process_image": "/api/process/image",
            "process_url": "/api/process/url",
            "batch_process": "/api/batch/process",
            "batch_status": "/api/batch/status/{batch_id}",
            "batch_all": "/api/batch/all"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Deep Sight API"
    }


@app.post("/api/process/image")
async def process_image_upload(
    file: UploadFile = File(...),
    save_to_storage: bool = Form(True)
):
    """
    Process an uploaded image.
    
    Args:
        file: Image file
        save_to_storage: Whether to save the image to storage
        
    Returns:
        Processed image data
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save uploaded file temporarily
        storage_folder = Path(config.get('storage.data_folder', './data'))
        temp_folder = storage_folder / 'temp'
        temp_folder.mkdir(parents=True, exist_ok=True)
        
        temp_path = temp_folder / file.filename
        
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Processing uploaded image: {file.filename}")
        
        # Process image
        result = processor.process_image(str(temp_path), save_to_storage=save_to_storage)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": result.to_dict()
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing uploaded image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/process/url")
async def process_image_url(request: ProcessingRequest):
    """
    Process an image from URL.
    
    Args:
        request: Processing request with image_url
        
    Returns:
        Processed image data
    """
    try:
        if not request.image_url:
            raise HTTPException(status_code=400, detail="image_url is required")
        
        # Download image
        response = requests.get(request.image_url, timeout=30)
        response.raise_for_status()
        
        # Save to temp file
        storage_folder = Path(config.get('storage.data_folder', './data'))
        temp_folder = storage_folder / 'temp'
        temp_folder.mkdir(parents=True, exist_ok=True)
        
        # Extract filename from URL or generate one
        filename = Path(request.image_url).name or "downloaded_image.jpg"
        temp_path = temp_folder / filename
        
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Processing image from URL: {request.image_url}")
        
        # Process image
        result = processor.process_image(str(temp_path), save_to_storage=request.save_to_storage)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": result.to_dict()
            }
        )
        
    except requests.RequestException as e:
        logger.error(f"Error downloading image: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing image from URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch/process")
async def start_batch_processing(request: BatchProcessingRequest):
    """
    Start batch processing of a folder.
    
    Args:
        request: Batch processing request with folder_path
        
    Returns:
        Batch ID for tracking
    """
    try:
        # Validate folder path
        folder_path = Path(request.folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            raise HTTPException(status_code=400, detail="Invalid folder path")
        
        # Start batch processing
        batch_id = batch_processor.process_folder(
            str(folder_path),
            recursive=request.recursive
        )
        
        logger.info(f"Started batch processing: {batch_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "batch_id": batch_id,
                "message": "Batch processing started"
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/batch/status/{batch_id}")
async def get_batch_status(batch_id: str):
    """
    Get status of a batch.
    
    Args:
        batch_id: Batch ID
        
    Returns:
        Batch status and progress
    """
    try:
        batch_status = BatchProcessor.get_batch_status(batch_id)
        
        if batch_status is None:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": batch_status.model_dump()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting batch status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/batch/all")
async def get_all_batches():
    """
    Get all active batches.
    
    Returns:
        Dictionary of all batch statuses
    """
    try:
        all_batches = BatchProcessor.get_all_batches()
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    batch_id: batch.model_dump()
                    for batch_id, batch in all_batches.items()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting all batches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = config.get('app.api_port', 8000)
    uvicorn.run(app, host="0.0.0.0", port=port)
