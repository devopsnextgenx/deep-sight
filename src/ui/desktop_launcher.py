"""Simple CustomTkinter launcher for future desktop integration."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import customtkinter as ctk
except ImportError:
    print("CustomTkinter not installed. Install with: pip install customtkinter")
    ctk = None


class DeepSightDesktopApp:
    """Basic desktop launcher - ready for future feature implementation."""
    
    def __init__(self):
        """Initialize the desktop application."""
        if ctk is None:
            raise ImportError("CustomTkinter is required for desktop mode")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Deep Sight - Desktop")
        self.root.geometry("800x600")
        
        # Set dark blue theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup basic UI components."""
        # Title
        title_label = ctk.CTkLabel(
            self.root,
            text="🔍 Deep Sight",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=40)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            self.root,
            text="AI-Powered Image Processing & Analysis",
            font=ctk.CTkFont(size=16)
        )
        subtitle_label.pack(pady=10)
        
        # Info frame
        info_frame = ctk.CTkFrame(self.root, width=600, height=300)
        info_frame.pack(pady=40, padx=40, fill="both", expand=True)
        
        info_text = """
        Desktop Application - Coming Soon!
        
        This is a placeholder for the future desktop integration.
        
        Currently, please use the Streamlit web interface:
        - Run: streamlit run src/ui/app.py
        
        Features planned for desktop version:
        • Native file browser
        • Drag & drop support
        • Offline processing
        • System tray integration
        • Better performance
        """
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        info_label.pack(pady=20, padx=20)
        
        # Launch Web UI button
        web_button = ctk.CTkButton(
            self.root,
            text="Launch Web Interface",
            command=self._launch_web_ui,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        web_button.pack(pady=20)
        
        # Close button
        close_button = ctk.CTkButton(
            self.root,
            text="Close",
            command=self.root.quit,
            width=200,
            height=40,
            fg_color="#666666",
            hover_color="#888888"
        )
        close_button.pack(pady=10)
    
    def _launch_web_ui(self):
        """Launch the Streamlit web interface."""
        import subprocess
        import os
        from pathlib import Path
        
        # Get the path to app.py
        app_path = Path(__file__).parent / "app.py"
        
        # Launch Streamlit in a new process
        subprocess.Popen(
            ["streamlit", "run", str(app_path)],
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        print("Web interface launched! Check your browser.")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main entry point for desktop launcher."""
    try:
        app = DeepSightDesktopApp()
        app.run()
    except ImportError as e:
        print(f"Error: {e}")
        print("\nTo use the desktop launcher, install CustomTkinter:")
        print("  pip install customtkinter")
        print("\nAlternatively, use the web interface:")
        print("  streamlit run src/ui/app.py")


if __name__ == "__main__":
    main()
