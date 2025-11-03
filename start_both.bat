@echo off
echo Starting Deep Sight API and UI...
echo.

REM Start API in a new window
start "Deep Sight API" cmd /k "python run_api.py"

REM Wait 3 seconds for API to start
timeout /t 3 /nobreak > nul

REM Start UI in a new window
start "Deep Sight UI" cmd /k "python run_ui.py"

echo.
echo Services started in separate windows!
echo API: http://localhost:8000
echo UI: http://localhost:8501
echo.
echo Press any key to close this window (services will keep running)
pause > nul
