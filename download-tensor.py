#!/usr/bin/env python
"""Download pre-trained models for Deep Sight without TensorFlow dependency."""
import os
import sys
import urllib.request
import zipfile
import hashlib
from pathlib import Path

# Model URLs and checksums (from official Keras models)
MODELS = {
    'ResNet50': {
        'url': 'https://storage.googleapis.com/tensorflow/keras-applications/resnet/resnet50_weights_tf_dim_ordering_tf_kernels.h5',
        'filename': 'resnet50_weights_tf_dim_ordering_tf_kernels.h5',
        'size': '102967424',  # ~98 MB
    },
    'MobileNetV2': {
        'url': 'https://storage.googleapis.com/tensorflow/keras-applications/mobilenet_v2/mobilenet_v2_weights_tf_dim_ordering_tf_kernels_1.0_224.h5',
        'filename': 'mobilenet_v2_weights_tf_dim_ordering_tf_kernels_1.0_224.h5',
        'size': '14536120',  # ~14 MB
    },
    'VGG16': {
        'url': 'https://storage.googleapis.com/tensorflow/keras-applications/vgg16/vgg16_weights_tf_dim_ordering_tf_kernels.h5',
        'filename': 'vgg16_weights_tf_dim_ordering_tf_kernels.h5',
        'size': '553467096',  # ~528 MB
    }
}

# OCR Models (Keras-OCR)
OCR_MODELS = {
    'craft_detector': {
        'url': 'https://github.com/faustomorales/keras-ocr/releases/download/v0.8.4/craft_mlt_25k.h5',
        'filename': 'craft_mlt_25k.h5',
        'size': '88573928',  # ~84 MB
    },
    'crnn_recognizer': {
        'url': 'https://github.com/faustomorales/keras-ocr/releases/download/v0.8.4/crnn_kurapan.h5',
        'filename': 'crnn_kurapan.h5',
        'size': '51178304',  # ~49 MB
    }
}


def download_file(url, destination, description=""):
    """Download a file with progress bar."""
    print(f"Downloading {description}...")
    print(f"  URL: {url}")
    print(f"  Destination: {destination}")
    
    try:
        def reporthook(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\r  Progress: {percent}% ")
            sys.stdout.flush()
        
        urllib.request.urlretrieve(url, destination, reporthook)
        print("\n  ✓ Download complete!")
        return True
    except Exception as e:
        print(f"\n  ✗ Download failed: {e}")
        return False


def download_models(model_list='all', include_ocr=True):
    """Download specified models."""
    # Setup directories
    tensor_dir = Path(__file__).parent / "tensor"
    models_dir = tensor_dir / "models"
    ocr_dir = tensor_dir / "ocr_model"
    
    tensor_dir.mkdir(exist_ok=True)
    models_dir.mkdir(exist_ok=True)
    ocr_dir.mkdir(exist_ok=True)
    
    print("="*60)
    print("Deep Sight - Model Downloader")
    print("="*60)
    print()
    
    # Determine which models to download
    if model_list == 'all':
        models_to_download = list(MODELS.keys())
    elif model_list == 'resnet50':
        models_to_download = ['ResNet50']
    elif model_list == 'mobilenet':
        models_to_download = ['MobileNetV2']
    elif model_list == 'vgg16':
        models_to_download = ['VGG16']
    else:
        models_to_download = []
    
    # Download vision models
    if models_to_download:
        print("Vision Models:")
        print("-" * 60)
        for model_name in models_to_download:
            model_info = MODELS[model_name]
            dest_path = models_dir / model_info['filename']
            
            if dest_path.exists():
                print(f"\n{model_name}:")
                print(f"  Already exists: {dest_path}")
                print(f"  Skipping download.")
            else:
                print(f"\n{model_name}:")
                success = download_file(
                    model_info['url'],
                    str(dest_path),
                    f"{model_name} ({int(model_info['size'])/(1024*1024):.1f} MB)"
                )
                if not success:
                    print(f"  Warning: Failed to download {model_name}")
    
    # Download OCR models
    if include_ocr:
        print("\n" + "="*60)
        print("OCR Models (Keras-OCR):")
        print("-" * 60)
        for model_name, model_info in OCR_MODELS.items():
            dest_path = ocr_dir / model_info['filename']
            
            if dest_path.exists():
                print(f"\n{model_name}:")
                print(f"  Already exists: {dest_path}")
                print(f"  Skipping download.")
            else:
                print(f"\n{model_name}:")
                success = download_file(
                    model_info['url'],
                    str(dest_path),
                    f"{model_name} ({int(model_info['size'])/(1024*1024):.1f} MB)"
                )
                if not success:
                    print(f"  Warning: Failed to download {model_name}")
    
    print("\n" + "="*60)
    print("Download Summary:")
    print("-" * 60)
    print(f"Models directory: {models_dir}")
    print(f"OCR directory: {ocr_dir}")
    
    # List downloaded files
    vision_models = list(models_dir.glob('*.h5'))
    ocr_models = list(ocr_dir.glob('*.h5'))
    
    print(f"\nVision models: {len(vision_models)} file(s)")
    for model in vision_models:
        size_mb = model.stat().st_size / (1024 * 1024)
        print(f"  - {model.name} ({size_mb:.1f} MB)")
    
    print(f"\nOCR models: {len(ocr_models)} file(s)")
    for model in ocr_models:
        size_mb = model.stat().st_size / (1024 * 1024)
        print(f"  - {model.name} ({size_mb:.1f} MB)")
    
    print("\n" + "="*60)
    print("✓ Model download complete!")
    print("="*60)
    print("\nNote: These are pre-trained model weights.")
    print("      TensorFlow/Keras is still required to use them.")
    print("      Install with: pip install tensorflow keras-ocr")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Download pre-trained models for Deep Sight'
    )
    parser.add_argument(
        '--models',
        choices=['all', 'resnet50', 'mobilenet', 'vgg16', 'none'],
        default='resnet50',
        help='Which vision models to download (default: resnet50)'
    )
    parser.add_argument(
        '--no-ocr',
        action='store_true',
        help='Skip OCR model downloads'
    )
    
    args = parser.parse_args()
    
    download_models(
        model_list=args.models,
        include_ocr=not args.no_ocr
    )
