# Deep Sight - Complete Setup Guide

## Prerequisites

1. **Python 3.9 or higher**
   ```powershell
   python --version
   # Should show Python 3.9.x or higher
   ```

2. **Ollama** (for LLM processing)
   - Download from: https://ollama.ai/
   - Install and verify:
   ```powershell
   ollama --version
   ```

## Installation Steps

### 1. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- FastAPI & Uvicorn (API server)
- Streamlit (Web UI)
- Pillow (Image processing)
- Keras-OCR & TensorFlow (OCR)
- PyYAML (Configuration)
- Pydantic (Data validation)
- Requests (HTTP client)

### 2. Install and Configure Ollama

```powershell
# Pull the llava model (required for image description)
ollama pull llava

# Verify installation
ollama list
# Should show: llava:latest

# Start Ollama service (if not auto-started)
ollama serve
```

### 3. Verify Setup

```powershell
# Test imports and configuration
python test_imports.py
```

Expected output:
```
✅ All imports successful!

Configuration check:
  API Port: 8000
  UI Port: 8501
  Ollama Model: llava
  Image Max Size: 1024x1024
```

## Running the Application

### Option 1: Run API Only

```powershell
python run_api.py
```

- Access API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Option 2: Run UI Only

```powershell
python run_ui.py
```

- Access UI: http://localhost:8501

### Option 3: Run Both (Recommended for Windows)

**Method A: Using PowerShell Script (Easiest)**
```powershell
.\start_both.ps1
```
This opens both services in separate windows automatically!

**Method B: Using Batch File**
```powershell
.\start_both.bat
```

**Method C: Manual (Two Terminals)**

**Terminal 1:**
```powershell
python run_api.py
```

**Terminal 2:**
```powershell
python run_ui.py
```

### Option 4: Using main.py (Not Recommended for 'both')

```powershell
# Run individually
python main.py api   # API only
python main.py ui    # UI only

# Run both (has limitations on Windows)
python main.py both  # Works but may have issues with reload
```

**Note:** `main.py both` uses multiprocessing which can have issues on Windows. 
Recommended to use the scripts above instead.

## Configuration

Edit `config/config.yml` to customize:

```yaml
# Ollama Settings
ollama:
  host: localhost
  port: 11434
  model: llava        # Change to llava:13b or llava:34b for better quality

# Application Ports
app:
  ui_port: 8501       # Change if port is in use
  api_port: 8000      # Change if port is in use

# Image Processing
image:
  max_width: 1024     # Adjust based on your needs
  max_height: 1024
  maintain_aspect_ratio: true

# TensorFlow OCR
tensorflow:
  model_type: keras-ocr  # or 'tesseract'
  
# Storage
storage:
  data_folder: ./data
  logs_folder: ./logs
```

## Troubleshooting

### Issue 1: Import Errors

**Error:** `ModuleNotFoundError: No module named 'src'`

**Solution:**
```powershell
# Use the provided launcher scripts
python run_api.py   # Instead of direct file execution
python run_ui.py
```

### Issue 2: Ollama Connection Failed

**Error:** `Ollama connection check failed`

**Solution:**
```powershell
# Check if Ollama is running
ollama list

# If not, start it
ollama serve

# In another terminal, test
ollama run llava
```

### Issue 3: Port Already in Use

**Error:** `Address already in use`

**Solution 1 - Change ports in config.yml:**
```yaml
app:
  ui_port: 8502  # Changed from 8501
  api_port: 8001  # Changed from 8000
```

**Solution 2 - Find and kill process:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Issue 4: Keras-OCR Download Slow

**Symptoms:** First run takes a long time, "Downloading models..."

**Solution:** This is normal! Keras-OCR downloads ~200MB of models on first use.
- Be patient (5-10 minutes depending on connection)
- Models are cached for future use
- Alternative: Use Tesseract instead

To use Tesseract:
1. Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Update config.yml:
```yaml
tensorflow:
  model_type: tesseract
```
3. Install Python wrapper:
```powershell
pip install pytesseract
```

### Issue 5: TensorFlow Memory Errors

**Error:** `ResourceExhaustedError` or `OOM`

**Solutions:**
1. Use Tesseract instead of Keras-OCR (lighter)
2. Process smaller batches
3. Reduce image size in config:
```yaml
image:
  max_width: 512
  max_height: 512
```

### Issue 6: Streamlit Import Error

**Error:** `attempted relative import with no known parent package`

**Solution:** Always use the launcher scripts:
```powershell
python run_ui.py   # ✓ Correct
# Do NOT run: streamlit run src/ui/app.py  # ✗ Wrong
```

## Testing Your Setup

### 1. Test API

```powershell
# Start API
python run_api.py

# In another terminal, test health endpoint
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Deep Sight API"
}
```

### 2. Test UI

```powershell
python run_ui.py
```

Then open http://localhost:8501 in your browser and check:
- ✓ Home page loads
- ✓ API Status shows "🟢 Online"
- ✓ LLM Service shows "🟢 Connected"

### 3. Test Image Processing

Via UI:
1. Go to "Process Image" page
2. Upload a test image
3. Click "Process Image"
4. Verify results appear

Via API:
```powershell
# Using curl (with a test image)
curl -X POST http://localhost:8000/api/process/url ^
  -H "Content-Type: application/json" ^
  -d "{\"image_url\":\"https://example.com/test.jpg\",\"save_to_storage\":true}"
```

## Performance Notes

### First Run
- **Keras-OCR**: Downloads models (~200MB, 5-10 min)
- **TensorFlow**: Initializes and compiles models (~30 sec)
- **LLM**: First request warms up Ollama (~10 sec)

### Subsequent Runs
- **Image Resize**: < 1 second
- **OCR Extraction**: 2-5 seconds per image
- **LLM Description**: 5-15 seconds (depends on model size)
- **Translation**: 3-10 seconds per language

### Tips for Better Performance
1. **Use GPU** if available (TensorFlow will auto-detect)
2. **Use larger Ollama models** for better quality (llava:13b, llava:34b)
3. **Process in batches** to amortize model loading
4. **Keep Ollama running** to avoid startup time

## Directory Structure After Setup

```
deep-sight/
├── config/
│   ├── config.yml           # Your configuration
│   └── llm_schema.yml       # LLM schemas
├── src/                     # Source code
├── data/
│   ├── images/              # Processed images (created on first use)
│   └── temp/                # Temporary files (created on first use)
├── logs/
│   └── deep_sight.log       # Application logs (created on first use)
├── tensor/
│   └── ocr_model/           # Downloaded OCR models (created on first use)
├── run_api.py               # Use this to start API
├── run_ui.py                # Use this to start UI
├── test_imports.py          # Use this to test setup
└── main.py                  # Alternative launcher
```

## Next Steps

After successful setup:

1. **Read QUICKSTART.md** for usage examples
2. **Check README.md** for complete documentation
3. **Try processing an image** via UI
4. **Test batch processing** with a folder of images
5. **Explore API docs** at http://localhost:8000/docs

## Getting Help

If you encounter issues:

1. Check `logs/deep_sight.log` for errors
2. Run `python test_imports.py` to verify setup
3. Verify Ollama is running: `ollama list`
4. Check if ports are available: `netstat -an | findstr "8000 8501"`
5. Review this guide's troubleshooting section

## Optional: Desktop Launcher

To use the CustomTkinter desktop launcher:

```powershell
# Install CustomTkinter
pip install customtkinter

# Run desktop launcher
python main.py desktop
```

Note: Desktop launcher is basic - it just launches the web UI. Full desktop features are planned for future releases.

## Security Note

This application is designed for **local development and trusted environments**:
- No authentication by default
- CORS allows all origins in development
- File paths are not sanitized
- Suitable for local/private network use

For production deployment, add:
- Authentication/authorization
- Input validation and sanitization
- Restricted CORS origins
- HTTPS/TLS encryption
- Rate limiting

## Success!

If all tests pass, you're ready to use Deep Sight! 🎉

Try processing your first image:
```powershell
# Terminal 1
python run_api.py

# Terminal 2
python run_ui.py

# Then open http://localhost:8501 in your browser
```
