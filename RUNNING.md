# Running Deep Sight - All Methods

## Quick Reference

| Method | Command | Best For | Notes |
|--------|---------|----------|-------|
| **PowerShell Script** | `.\start_both.ps1` | Windows users | ⭐ Easiest - opens both in separate windows |
| **Batch File** | `.\start_both.bat` | Windows users | ⭐ Simple - opens both in separate windows |
| **Bash Script** | `./start_both.sh` | Linux/Mac/WSL | ⭐ Best for Unix-like systems |
| **API Only** | `python run_api.py` | Development | Single service |
| **UI Only** | `python run_ui.py` | Development | Single service |
| **Manual Both** | Two terminals | Cross-platform | Most control |
| **main.py** | `python main.py api/ui` | Individual services | Alternative launcher |

## Recommended Methods

### 🎯 Best for Windows: PowerShell Script

```powershell
.\start_both.ps1
```

**What it does:**
- Opens API in a new PowerShell window
- Opens UI in another new PowerShell window
- Shows you the URLs
- Keeps both running

**To stop:** Close the PowerShell windows or press Ctrl+C in each

### 🎯 Alternative for Windows: Batch File

```powershell
.\start_both.bat
```

**What it does:**
- Opens API in a new command prompt
- Opens UI in another command prompt
- Shows you the URLs

**To stop:** Close the command prompt windows

### 🎯 Best for Linux/Mac/WSL: Bash Script

```bash
# Make executable (first time only)
chmod +x start_both.sh

# Run the script
./start_both.sh
```

**What it does:**
- Starts both services in background
- Logs output to `logs/api.log` and `logs/ui.log`
- Shows you the URLs
- Handles cleanup on Ctrl+C

**To stop:** Press Ctrl+C in the terminal

**View logs:**
```bash
# Follow API logs
tail -f logs/api.log

# Follow UI logs
tail -f logs/ui.log
```

## Individual Services

### Run API Only

```powershell
python run_api.py
```

Access at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

Press Ctrl+C to stop

### Run UI Only

```powershell
python run_ui.py
```

Access at:
- UI: http://localhost:8501

Press Ctrl+C to stop

## Manual Method (Two Terminals)

This works on all platforms and gives you the most control.

**Terminal 1:**
```powershell
python run_api.py
```

**Terminal 2:**
```powershell
python run_ui.py
```

**Benefits:**
- See logs from each service separately
- Can restart one without affecting the other
- Full control over each service

## Using main.py

### For Individual Services (Recommended)

```powershell
# API only
python main.py api

# UI only  
python main.py ui
```

### For Both Services (Limited Support)

```powershell
python main.py both
```

**⚠️ Known Issues:**
- On Windows, reload feature disabled when running both
- Signal handling issues in threads
- Harder to stop cleanly

**Recommendation:** Use the PowerShell script instead!

## Troubleshooting

### Issue: "start_both.ps1 cannot be loaded"

**Error:**
```
start_both.ps1 cannot be loaded because running scripts is disabled on this system
```

**Solution:**
```powershell
# Enable script execution (run PowerShell as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
.\start_both.ps1
```

### Issue: Port Already in Use

**Error:**
```
Address already in use
```

**Solution 1 - Find what's using the port:**
```powershell
# For port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

**Solution 2 - Change ports in config.yml:**
```yaml
app:
  ui_port: 8502  # Changed from 8501
  api_port: 8001  # Changed from 8000
```

### Issue: Services Don't Stop

**Solution:**
```powershell
# Find Python processes
Get-Process python

# Kill all Python processes (be careful!)
Get-Process python | Stop-Process -Force

# Or kill specific ports
taskkill /F /IM python.exe
```

## Development Workflow

### Recommended Setup

1. **API Terminal** - Always keep running:
   ```powershell
   python run_api.py
   ```

2. **UI Terminal** - Restart as needed:
   ```powershell
   python run_ui.py
   ```

3. **Test Terminal** - For running tests:
   ```powershell
   python test_imports.py
   # or other test commands
   ```

### Why Separate Terminals?

- ✅ See API logs separately from UI logs
- ✅ Restart UI without restarting API
- ✅ Easier debugging
- ✅ Better control

## Production Deployment

For production, run as separate services:

### API Service
```powershell
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### UI Service (Behind Reverse Proxy)
```powershell
streamlit run src/ui/app.py --server.port 8501
```

Use a reverse proxy (nginx/Apache) in front of both services.

## Quick Commands Summary

```powershell
# Easiest way to start both (Windows)
.\start_both.ps1

# Individual services
python run_api.py      # API only
python run_ui.py       # UI only

# Test setup
python test_imports.py

# Alternative launchers
python main.py api     # API via main.py
python main.py ui      # UI via main.py

# Check health
curl http://localhost:8000/health
```

## Access URLs

After starting the services:

| Service | URL | Purpose |
|---------|-----|---------|
| API | http://localhost:8000 | REST API endpoints |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| API Health | http://localhost:8000/health | Health check |
| UI | http://localhost:8501 | Web interface |

## Best Practices

1. **Always start API first** - UI depends on API for some features
2. **Wait 3-5 seconds** between starting services
3. **Check health endpoint** before using UI: `curl http://localhost:8000/health`
4. **Use separate terminals** for easier debugging
5. **Close cleanly** with Ctrl+C rather than closing windows

## Summary

**For regular use on Windows:**
```powershell
.\start_both.ps1
```

**For regular use on Linux/Mac/WSL:**
```bash
chmod +x start_both.sh  # First time only
./start_both.sh
```

**For development (all platforms):**
```bash
# Terminal 1
python run_api.py

# Terminal 2
python run_ui.py
```

**For testing:**
```bash
python test_imports.py
curl http://localhost:8000/health
```

That's it! Choose the method that works best for your workflow.
