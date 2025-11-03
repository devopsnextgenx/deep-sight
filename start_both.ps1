# Start both Deep Sight API and UI in separate windows

Write-Host "Starting Deep Sight API and UI..." -ForegroundColor Cyan
Write-Host ""

# Start API in new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python run_api.py" -WindowStyle Normal

Write-Host "Waiting for API to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start UI in new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python run_ui.py" -WindowStyle Normal

Write-Host ""
Write-Host "Services started in separate windows!" -ForegroundColor Green
Write-Host "API:  http://localhost:8000" -ForegroundColor White
Write-Host "UI:   http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "To stop: Close the PowerShell windows or press Ctrl+C in each" -ForegroundColor Yellow
