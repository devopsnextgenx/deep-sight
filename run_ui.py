"""Launcher script for Streamlit UI."""
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    ui_path = Path(__file__).parent / "src" / "ui" / "app.py"
    
    # Run Streamlit
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ui_path),
        "--server.port",
        "8501",
        "--theme.base",
        "dark"
    ])
