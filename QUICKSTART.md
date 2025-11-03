# Deep Sight - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies

```powershell
# Install Python packages
pip install -r requirements.txt
```

### Step 2: Install and Setup Ollama

```powershell
# Download from https://ollama.ai/
# After installation, pull the llava model
ollama pull llava

# Verify Ollama is running
ollama list
```

### Step 3: Run the Application

**Option A: Run Both (Easiest)**

*Windows:*
```powershell
# Using PowerShell script (opens both in separate windows)
.\start_both.ps1

# OR using batch file
.\start_both.bat
```

*Linux/Mac/WSL:*
```bash
# Make executable (first time only)
chmod +x start_both.sh

# Run
./start_both.sh
```

**Option B: Run API Only**
```bash
python run_api.py
```
This will start FastAPI server on http://localhost:8000

**Option C: Run UI Only**
```bash
python run_ui.py
```
This will start Streamlit UI on http://localhost:8501

**Option D: Manual (Two Terminals)**
```powershell
# Terminal 1: Start API
python run_api.py

# Terminal 2: Start UI
python run_ui.py
```

### Step 4: Access the Application

1. **Web UI**: Open http://localhost:8501 in your browser
2. **API Docs**: Open http://localhost:8000/docs for Swagger documentation

## 📖 Usage Examples

### Process a Single Image (Web UI)

1. Go to "Process Image" page
2. Upload an image or provide a URL
3. Click "Process Image"
4. View results: extracted text, translations, and description

### Batch Process a Folder (Web UI)

1. Go to "Batch Processing" page
2. Enter the absolute folder path (e.g., `D:\images`)
3. Click "Start Batch Processing"
4. Go to "Batch Status" page to monitor progress

### Using the API

**Process Image from URL**
```powershell
curl -X POST "http://localhost:8000/api/process/url" `
  -H "Content-Type: application/json" `
  -d '{
    "image_url": "https://example.com/image.jpg",
    "save_to_storage": true
  }'
```

**Start Batch Processing**
```powershell
curl -X POST "http://localhost:8000/api/batch/process" `
  -H "Content-Type: application/json" `
  -d '{
    "folder_path": "D:/images",
    "recursive": false
  }'
```

## ⚙️ Configuration

Edit `config/config.yml` to customize:

```yaml
# Change Ollama model
ollama:
  model: llava  # or llava:13b, llava:34b

# Change ports
app:
  ui_port: 8501
  api_port: 8000

# Adjust image size
image:
  max_width: 1024
  max_height: 1024
```

## 🔧 Troubleshooting

### Issue: "Connection refused" to Ollama

**Solution:** Make sure Ollama is running
```powershell
ollama serve
```

### Issue: OCR models downloading slowly

**Solution:** This is normal on first run. Keras-OCR downloads ~200MB of models. Wait patiently.

### Issue: Port already in use

**Solution:** Change ports in `config/config.yml`
```yaml
app:
  ui_port: 8502  # Change to any available port
  api_port: 8001
```

### Issue: Memory errors with TensorFlow

**Solution:** Use smaller batch sizes or switch to Tesseract OCR
```yaml
tensorflow:
  model_type: tesseract  # Lighter on memory
```

## 📁 Directory Structure After First Run

```
deep-sight/
├── data/
│   ├── images/          # Processed images saved here
│   └── temp/            # Temporary files
├── logs/
│   └── deep_sight.log   # Application logs
└── tensor/
    └── ocr_model/       # Downloaded OCR models
```

## 🎯 Common Workflows

### Workflow 1: Process Images from Web
1. Upload images via UI
2. View results immediately
3. Download or save to storage

### Workflow 2: Batch Process Local Folder
1. Start batch via UI or API
2. Monitor progress in real-time
3. Resume if interrupted (automatic)
4. Browse and edit results

### Workflow 3: API Integration
1. Use REST API in your application
2. Post images programmatically
3. Retrieve structured JSON results
4. Build custom workflows

## 📊 Understanding Results

Each processed image generates:
```yaml
image_name: photo.jpg
extracted_text: "Text found in image..."
translated_text_hindi: "छवि में मिला पाठ..."
translated_text_english: "Text found in image..."
description: "A detailed description of the image..."
metadata:
  model_name: llava
  datetime: "2025-11-02T16:00:00"
  processing_time: 12.5
  image_size:
    width: 1024
    height: 768
```

## 🚀 Next Steps

- Explore the Streamlit UI features
- Try the REST API via Swagger docs
- Customize configuration for your needs
- Process your own image collections
- Integrate with your applications

## 💡 Tips

1. **Performance**: First image takes longer (model loading). Subsequent images are faster.
2. **Batch Processing**: Progress is saved every 5 images. Safe to interrupt and resume.
3. **LLM Quality**: Use larger models (llava:13b, llava:34b) for better descriptions.
4. **Storage**: Processed images are copied to `data/images/` folder.

## 🆘 Need Help?

- Check the full README.md for detailed documentation
- Review logs in `logs/deep_sight.log`
- Open an issue on GitHub
- Check Ollama documentation at https://ollama.ai/

Happy processing! 🎉
