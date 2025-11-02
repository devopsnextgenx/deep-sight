# Deep Sight 🔍

AI-Powered Image Processing & Analysis with OCR, LLM Description, and Translation

## Features

- 📝 **Text Extraction**: Extract text from images using TensorFlow OCR (Keras-OCR or Tesseract)
- 🖼️ **Image Description**: Generate detailed descriptions using Ollama LLM
- 🌐 **Translation**: Translate extracted text to Hindi and English
- 📁 **Batch Processing**: Process entire folders of images with progress tracking
- 💾 **Progress Checkpointing**: Resume interrupted batch processing
- 🌐 **REST API**: FastAPI endpoints with Swagger documentation
- 🎨 **Modern UI**: Streamlit web interface with dark blue theme
- 🖥️ **Desktop Ready**: CustomTkinter launcher for future desktop features

## Project Structure

```
deep-sight/
├── config/
│   ├── config.yml          # Main configuration
│   └── llm_schema.yml      # LLM response schemas
├── src/
│   ├── processors/
│   │   ├── image_processor.py      # Image resizing
│   │   ├── text_extractor.py       # OCR processing
│   │   ├── llm_agent.py            # LLM agent
│   │   ├── processor.py            # Main orchestrator
│   │   └── batch_processor.py      # Batch processing
│   ├── api/
│   │   └── main.py                 # FastAPI application
│   ├── ui/
│   │   ├── app.py                  # Streamlit UI
│   │   └── desktop_launcher.py     # CustomTkinter launcher
│   ├── models/
│   │   └── image_data.py           # Data models
│   └── config_loader.py            # Configuration loader
├── data/                   # Processed images and data
├── logs/                   # Application logs
├── tensor/                 # TensorFlow models
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
└── README.md

```

## Prerequisites

- Python 3.9+
- [Ollama](https://ollama.ai/) with `llava` model installed
- (Optional) Tesseract OCR for alternative text extraction

## Installation

1. **Clone the repository**
   ```powershell
   git clone <repository-url>
   cd deep-sight
   ```

2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Install Ollama and pull the llava model**
   ```powershell
   # Download and install Ollama from https://ollama.ai/
   ollama pull llava
   ```

4. **Configure the application**
   Edit `config/config.yml` to customize:
   - Ollama host/port/model
   - API and UI ports
   - Image processing settings
   - Storage locations

## Usage

### Quick Start (API + UI)

```powershell
python main.py both
```

This starts both the FastAPI server and Streamlit UI.

### Run API Only

```powershell
python main.py api
```

Access Swagger docs at: http://localhost:8000/docs

### Run UI Only

```powershell
python main.py ui
```

Access UI at: http://localhost:8501

### Run Desktop Launcher (Optional)

```powershell
# Install CustomTkinter first
pip install customtkinter

python main.py desktop
```

## API Endpoints

### Process Single Image

**Upload Image**
```http
POST /api/process/image
Content-Type: multipart/form-data

file: <image-file>
save_to_storage: true
```

**Process from URL**
```http
POST /api/process/url
Content-Type: application/json

{
  "image_url": "https://example.com/image.jpg",
  "save_to_storage": true
}
```

### Batch Processing

**Start Batch**
```http
POST /api/batch/process
Content-Type: application/json

{
  "folder_path": "D:/images",
  "recursive": false
}
```

**Get Batch Status**
```http
GET /api/batch/status/{batch_id}
```

**Get All Batches**
```http
GET /api/batch/all
```

## Configuration

### config.yml

Key configuration options:

```yaml
# Ollama LLM
ollama:
  host: localhost
  port: 11434
  model: llava

# Application Ports
app:
  ui_port: 8501
  api_port: 8000

# Image Processing
image:
  max_width: 1024
  max_height: 1024
  maintain_aspect_ratio: true

# TensorFlow OCR
tensorflow:
  model_type: keras-ocr  # or tesseract
```

## Batch Processing

Batch processing automatically:
- Scans folders for images
- Saves progress to `{folder_name}_progress.yml`
- Resumes from last checkpoint if interrupted
- Processes images in parallel threads

Progress file format:
```yaml
/path/to/image1.jpg:
  image_name: image1.jpg
  extracted_text: "..."
  translated_text_hindi: "..."
  translated_text_english: "..."
  description: "..."
  metadata:
    model_name: llava
    datetime: "2025-11-02T16:00:00"
```

## UI Features

### Home Page
- System status (API, LLM, Storage)
- Quick overview of features

### Process Image
- Upload images or provide URLs
- View extracted text, translations, and descriptions
- Save to storage

### Batch Processing
- Start batch processing of folders
- Configure recursive processing

### Batch Status
- Real-time progress monitoring
- Auto-refresh every 5 seconds
- Visual progress bars

### Browse Data
- View processed images
- Edit and save extracted data
- Navigate folder structure

## Development

### Project Uses

- **FastAPI**: REST API with automatic OpenAPI docs
- **Streamlit**: Modern web UI with hot-reloading
- **Uvicorn**: ASGI server for production
- **Pydantic**: Data validation and serialization
- **Keras-OCR**: TensorFlow-based text extraction
- **Ollama**: Local LLM for descriptions and translation

### Class Architecture

- `ImageProcessor`: Image resizing and preprocessing
- `TextExtractor`: OCR text extraction (pluggable backends)
- `LLMAgent`: Ollama integration with schema-based responses
- `ImageProcessorOrchestrator`: Pipeline orchestration
- `BatchProcessor`: Multi-threaded batch processing with checkpoints

## Troubleshooting

### Ollama Connection Issues
```powershell
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve
```

### OCR Model Download
Keras-OCR will automatically download models on first use. This may take several minutes.

### Port Conflicts
Edit `config/config.yml` to change default ports:
```yaml
app:
  ui_port: 8502  # Change if 8501 is in use
  api_port: 8001  # Change if 8000 is in use
```

## Future Enhancements

- [ ] Full CustomTkinter desktop application
- [ ] GPU acceleration for TensorFlow
- [ ] Multiple LLM provider support
- [ ] Advanced image preprocessing
- [ ] Export to various formats (PDF, JSON, CSV)
- [ ] Image classification and tagging
- [ ] Search functionality

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
