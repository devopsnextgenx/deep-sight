"""Streamlit UI for Deep Sight."""
import streamlit as st
import yaml
import requests
from pathlib import Path
import time
from typing import Dict, Any
from PIL import Image
import sys
import os

# Add parent directory to path for imports
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.config_loader import config
except ImportError:
    from config_loader import config

# Page configuration
st.set_page_config(
    page_title="Deep Sight",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark blue theme
st.markdown("""
<style>
    /* Dark blue theme */
    .stApp {
        background-color: #0a1929;
    }
    
    .main {
        background-color: #0a1929;
        color: #e0e0e0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #0d2238;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #64b5f6 !important;
    }
    
    /* Cards and containers */
    .stButton > button {
        background-color: #1976d2;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
    }
    
    .stButton > button:hover {
        background-color: #2196f3;
    }
    
    /* Text input */
    .stTextInput > div > div > input {
        background-color: #0d2238;
        color: #e0e0e0;
        border-color: #1976d2;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: #1976d2;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #0d2238;
        border-left: 4px solid #1976d2;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    
    /* Success box */
    .success-box {
        background-color: #0d3023;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    
    /* Error box */
    .error-box {
        background-color: #3d0d0d;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


def get_api_url():
    """Get API base URL from config."""
    api_port = config.get('app.api_port', 8000)
    return f"http://localhost:{api_port}"


def main():
    """Main UI application."""
    st.title("🔍 Deep Sight")
    st.markdown("### AI-Powered Image Processing & Analysis")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Home", "Process Image", "Batch Processing", "Batch Status", "Browse Data"]
    )
    
    if page == "Home":
        show_home()
    elif page == "Process Image":
        show_process_image()
    elif page == "Batch Processing":
        show_batch_processing()
    elif page == "Batch Status":
        show_batch_status()
    elif page == "Browse Data":
        show_browse_data()


def show_home():
    """Show home page."""
    st.header("Welcome to Deep Sight")
    
    st.markdown("""
    <div class="info-box">
    <h3>Features</h3>
    <ul>
        <li>📝 <b>Text Extraction</b>: Extract text from images using TensorFlow OCR</li>
        <li>🖼️ <b>Image Description</b>: Generate detailed descriptions using LLM</li>
        <li>🌐 <b>Translation</b>: Translate extracted text to Hindi and English</li>
        <li>📁 <b>Batch Processing</b>: Process entire folders of images</li>
        <li>📊 <b>Progress Tracking</b>: Monitor batch processing with real-time updates</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # System status
    st.subheader("System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("API Status", "🟢 Online" if check_api_health() else "🔴 Offline")
    
    with col2:
        ollama_status = check_ollama_connection()
        st.metric("LLM Service", "🟢 Connected" if ollama_status else "🔴 Disconnected")
    
    with col3:
        data_folder = Path(config.get('storage.data_folder', './data'))
        st.metric("Data Folder", "✓ Ready" if data_folder.exists() else "✗ Not Found")


def show_process_image():
    """Show image processing page."""
    st.header("Process Single Image")
    
    tab1, tab2 = st.tabs(["Upload Image", "Image URL"])
    
    with tab1:
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp']
        )
        
        if uploaded_file is not None:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            
            with col2:
                save_to_storage = st.checkbox("Save to storage", value=True)
                
                if st.button("Process Image", key="process_upload"):
                    process_uploaded_image(uploaded_file, save_to_storage)
    
    with tab2:
        image_url = st.text_input("Enter image URL")
        
        if image_url:
            save_to_storage = st.checkbox("Save to storage", value=True, key="url_save")
            
            if st.button("Process Image from URL", key="process_url"):
                process_image_from_url(image_url, save_to_storage)


def process_uploaded_image(uploaded_file, save_to_storage):
    """Process uploaded image."""
    try:
        with st.spinner("Processing image..."):
            # Prepare multipart form data
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {'save_to_storage': save_to_storage}
            
            response = requests.post(
                f"{get_api_url()}/api/process/image",
                files=files,
                data=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                display_processing_result(result['data'])
            else:
                st.error(f"Error: {response.text}")
    
    except Exception as e:
        st.error(f"Error processing image: {e}")


def process_image_from_url(image_url, save_to_storage):
    """Process image from URL."""
    try:
        with st.spinner("Processing image from URL..."):
            response = requests.post(
                f"{get_api_url()}/api/process/url",
                json={
                    'image_url': image_url,
                    'save_to_storage': save_to_storage
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                display_processing_result(result['data'])
            else:
                st.error(f"Error: {response.text}")
    
    except Exception as e:
        st.error(f"Error processing image: {e}")


def display_processing_result(data: Dict[str, Any]):
    """Display processing results."""
    st.success("✓ Image processed successfully!")
    
    st.subheader("Results")
    
    # Image info
    st.markdown(f"**Image Name:** {data['image_name']}")
    
    # Extracted Text
    st.markdown("#### 📝 Extracted Text")
    st.text_area("Original Text", data['extracted_text'], height=100)
    
    # Translations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🇮🇳 Hindi Translation")
        st.text_area("Hindi", data['translated_text_hindi'], height=100, key="hindi")
    
    with col2:
        st.markdown("#### 🇬🇧 English Translation")
        st.text_area("English", data['translated_text_english'], height=100, key="english")
    
    # Description
    st.markdown("#### 🖼️ Image Description")
    st.text_area("Description", data['description'], height=150)
    
    # Metadata
    st.markdown("#### ℹ️ Metadata")
    metadata = data['metadata']
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Model", metadata['model_name'])
    
    with col2:
        st.metric("Processing Time", f"{metadata['processing_time']:.2f}s")
    
    with col3:
        if 'image_size' in metadata and metadata['image_size']:
            size = metadata['image_size']
            st.metric("Image Size", f"{size.get('width', 0)}x{size.get('height', 0)}")


def show_batch_processing():
    """Show batch processing page."""
    st.header("Batch Processing")
    
    st.markdown("""
    <div class="info-box">
    Process multiple images from a folder. Progress will be saved to a YAML file in the folder,
    allowing you to resume if interrupted.
    </div>
    """, unsafe_allow_html=True)
    
    folder_path = st.text_input("Folder Path (absolute path)", value="")
    recursive = st.checkbox("Process subdirectories recursively", value=False)
    
    if st.button("Start Batch Processing"):
        if not folder_path:
            st.warning("Please enter a folder path")
        else:
            start_batch_processing(folder_path, recursive)


def start_batch_processing(folder_path: str, recursive: bool):
    """Start batch processing."""
    try:
        with st.spinner("Starting batch processing..."):
            response = requests.post(
                f"{get_api_url()}/api/batch/process",
                json={
                    'folder_path': folder_path,
                    'recursive': recursive
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                batch_id = result['batch_id']
                
                st.success(f"✓ Batch processing started!")
                st.info(f"Batch ID: `{batch_id}`")
                st.markdown("Go to **Batch Status** page to monitor progress.")
            else:
                st.error(f"Error: {response.text}")
    
    except Exception as e:
        st.error(f"Error starting batch: {e}")


def show_batch_status():
    """Show batch status page."""
    st.header("Batch Processing Status")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh every 5 seconds", value=True)
    
    try:
        response = requests.get(f"{get_api_url()}/api/batch/all", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            batches = result['data']
            
            if not batches:
                st.info("No active batches")
            else:
                for batch_id, batch_data in batches.items():
                    display_batch_card(batch_id, batch_data)
        else:
            st.error(f"Error fetching batches: {response.text}")
    
    except Exception as e:
        st.error(f"Error: {e}")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(5)
        st.rerun()


def display_batch_card(batch_id: str, batch_data: Dict[str, Any]):
    """Display batch status card."""
    with st.expander(f"📁 Batch: {Path(batch_data['folder_path']).name}", expanded=True):
        # Status indicator
        status = batch_data['status']
        status_emoji = {
            'pending': '⏳',
            'processing': '⚙️',
            'completed': '✅',
            'failed': '❌'
        }
        
        st.markdown(f"### {status_emoji.get(status, '❓')} Status: {status.upper()}")
        st.markdown(f"**Folder:** `{batch_data['folder_path']}`")
        st.markdown(f"**Batch ID:** `{batch_id}`")
        
        # Progress metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total", batch_data['total_images'])
        
        with col2:
            st.metric("Completed", batch_data['completed_images'])
        
        with col3:
            st.metric("Pending", batch_data['total_images'] - batch_data['completed_images'] - batch_data['failed_images'])
        
        with col4:
            st.metric("Failed", batch_data['failed_images'])
        
        # Progress bar
        progress = batch_data['completed_images'] / batch_data['total_images'] if batch_data['total_images'] > 0 else 0
        st.progress(progress)
        st.markdown(f"**Progress:** {progress * 100:.1f}%")
        
        # Timestamps
        if batch_data.get('start_time'):
            st.markdown(f"**Started:** {batch_data['start_time']}")
        if batch_data.get('end_time'):
            st.markdown(f"**Completed:** {batch_data['end_time']}")


def show_browse_data():
    """Show data browser page."""
    st.header("Browse Processed Data")
    
    data_folder = Path(config.get('storage.data_folder', './data'))
    
    if not data_folder.exists():
        st.warning("Data folder not found")
        return
    
    # Find all YAML progress files
    yaml_files = list(data_folder.rglob("*_progress.yml"))
    
    if not yaml_files:
        st.info("No processed data found")
        return
    
    # Select folder
    selected_file = st.selectbox(
        "Select folder data",
        yaml_files,
        format_func=lambda x: x.stem.replace("_progress", "")
    )
    
    if selected_file:
        display_folder_data(selected_file)


def display_folder_data(yaml_file: Path):
    """Display data from YAML file."""
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        
        if not data:
            st.info("No processed images in this folder")
            return
        
        # Image selector
        image_paths = list(data.keys())
        selected_image = st.selectbox("Select image", image_paths, format_func=lambda x: Path(x).name)
        
        if selected_image and selected_image in data:
            image_data = data[selected_image]
            
            # Display image if exists
            if Path(selected_image).exists():
                st.image(str(selected_image), caption=Path(selected_image).name, width=400)
            
            # Editable fields
            st.subheader("Image Data (Editable)")
            
            extracted_text = st.text_area("Extracted Text", image_data.get('extracted_text', ''), height=100)
            translated_hindi = st.text_area("Hindi Translation", image_data.get('translated_text_hindi', ''), height=100)
            translated_english = st.text_area("English Translation", image_data.get('translated_text_english', ''), height=100)
            description = st.text_area("Description", image_data.get('description', ''), height=150)
            
            if st.button("Save Changes"):
                # Update data
                data[selected_image]['extracted_text'] = extracted_text
                data[selected_image]['translated_text_hindi'] = translated_hindi
                data[selected_image]['translated_text_english'] = translated_english
                data[selected_image]['description'] = description
                
                # Save to file
                with open(yaml_file, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
                
                st.success("✓ Changes saved!")
    
    except Exception as e:
        st.error(f"Error loading data: {e}")


def check_api_health() -> bool:
    """Check if API is healthy."""
    try:
        response = requests.get(f"{get_api_url()}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def check_ollama_connection() -> bool:
    """Check Ollama connection."""
    try:
        ollama_host = config.get('ollama.host', 'localhost')
        ollama_port = config.get('ollama.port', 11434)
        response = requests.get(f"http://{ollama_host}:{ollama_port}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


if __name__ == "__main__":
    main()
