"""Main entry point for Deep Sight application."""
import sys
import argparse
import uvicorn
import subprocess
from pathlib import Path

from src.config_loader import config


def run_api():
    """Run FastAPI server."""
    print("Starting Deep Sight API...")
    port = config.get('app.api_port', 8000)
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )


def run_ui():
    """Run Streamlit UI."""
    print("Starting Deep Sight UI...")
    ui_port = config.get('app.ui_port', 8501)
    app_path = Path(__file__).parent / "src" / "ui" / "app.py"
    
    subprocess.run([
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(ui_port),
        "--theme.base",
        "dark"
    ])


def run_desktop():
    """Run desktop launcher."""
    print("Starting Deep Sight Desktop Launcher...")
    try:
        from src.ui.desktop_launcher import main as desktop_main
        desktop_main()
    except ImportError as e:
        print(f"Error: {e}")
        print("\nTo use the desktop launcher, install CustomTkinter:")
        print("  pip install customtkinter")
        sys.exit(1)


def run_both():
    """Run both API and UI in separate processes."""
    import threading
    
    print("Starting Deep Sight API and UI...")
    
    # Start API in a separate thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Wait a bit for API to start
    import time
    time.sleep(2)
    
    # Start UI in main thread
    run_ui()


def main():
    """Main entry point with CLI arguments."""
    parser = argparse.ArgumentParser(description="Deep Sight - AI-Powered Image Processing")
    parser.add_argument(
        "mode",
        choices=["api", "ui", "desktop", "both"],
        help="Run mode: api (FastAPI only), ui (Streamlit only), desktop (CustomTkinter), both (API + UI)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "api":
        run_api()
    elif args.mode == "ui":
        run_ui()
    elif args.mode == "desktop":
        run_desktop()
    elif args.mode == "both":
        run_both()


if __name__ == "__main__":
    main()
