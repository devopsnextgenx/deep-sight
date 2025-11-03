#!/bin/bash
# Start both Deep Sight API and UI

echo "Starting Deep Sight API and UI..."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
    fi
    if [ ! -z "$UI_PID" ]; then
        kill $UI_PID 2>/dev/null
    fi
    echo "Services stopped."
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup SIGINT SIGTERM

# Start API in background
echo "Starting API..."
python run_api.py > logs/api.log 2>&1 &
API_PID=$!
echo "API started (PID: $API_PID)"

# Wait for API to start
echo "Waiting for API to initialize..."
sleep 3

# Start UI in background
echo "Starting UI..."
python run_ui.py > logs/ui.log 2>&1 &
UI_PID=$!
echo "UI started (PID: $UI_PID)"

echo ""
echo "✓ Services started successfully!"
echo ""
echo "Access URLs:"
echo "  API:      http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  UI:       http://localhost:8501"
echo ""
echo "Logs:"
echo "  API log: logs/api.log"
echo "  UI log:  logs/ui.log"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Keep script running and wait for processes
wait $API_PID $UI_PID
