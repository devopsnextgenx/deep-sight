# Model Download Guide

## Overview

The `download-tensor.py` script downloads pre-trained models for Deep Sight **without requiring TensorFlow to be installed first**. This is useful when you want to pre-download models before installing the full dependencies.

## Quick Start

### Download ResNet50 + OCR Models (Recommended)

```bash
python download-tensor.py
```

This downloads:
- ResNet50 (~98 MB) - Vision model
- CRAFT detector (~84 MB) - OCR text detection
- CRNN recognizer (~49 MB) - OCR text recognition

**Total size: ~231 MB**

## Usage

### Basic Commands

```bash
# Download ResNet50 + OCR models (default)
python download-tensor.py

# Download all vision models + OCR
python download-tensor.py --models all

# Download only MobileNetV2 + OCR
python download-tensor.py --models mobilenet

# Download only VGG16 + OCR
python download-tensor.py --models vgg16

# Download only vision models (skip OCR)
python download-tensor.py --models resnet50 --no-ocr

# Download only OCR models (no vision models)
python download-tensor.py --models none
```

### Available Options

| Option | Description | Models | Size |
|--------|-------------|--------|------|
| `--models resnet50` | ResNet50 (default) | 1 model | ~98 MB |
| `--models mobilenet` | MobileNetV2 (lightweight) | 1 model | ~14 MB |
| `--models vgg16` | VGG16 (large) | 1 model | ~528 MB |
| `--models all` | All vision models | 3 models | ~640 MB |
| `--models none` | No vision models | 0 models | 0 MB |
| `--no-ocr` | Skip OCR models | - | Save ~133 MB |

## Model Details

### Vision Models

**ResNet50** (Recommended)
- Size: ~98 MB
- Use case: General image classification
- GPU: Recommended but not required
- Accuracy: High

**MobileNetV2** (Lightweight)
- Size: ~14 MB
- Use case: Mobile/embedded devices
- GPU: Not required
- Accuracy: Good

**VGG16** (Large)
- Size: ~528 MB
- Use case: High accuracy requirements
- GPU: Strongly recommended
- Accuracy: Very high

### OCR Models

**CRAFT Detector**
- Size: ~84 MB
- Purpose: Text region detection
- Required for: Keras-OCR text extraction

**CRNN Recognizer**
- Size: ~49 MB
- Purpose: Text recognition
- Required for: Keras-OCR text extraction

## Directory Structure

After running the script:

```
tensor/
├── models/
│   ├── resnet50_weights_tf_dim_ordering_tf_kernels.h5
│   ├── mobilenet_v2_weights_tf_dim_ordering_tf_kernels_1.0_224.h5
│   └── vgg16_weights_tf_dim_ordering_tf_kernels.h5
└── ocr_model/
    ├── craft_mlt_25k.h5
    └── crnn_kurapan.h5
```

## Examples

### Example 1: Quick Setup (Minimal)

```bash
# Download only MobileNetV2 + OCR (smallest option)
python download-tensor.py --models mobilenet

# Total: ~147 MB
```

### Example 2: Recommended Setup

```bash
# Download ResNet50 + OCR (balanced)
python download-tensor.py

# Total: ~231 MB
```

### Example 3: Complete Setup

```bash
# Download all models
python download-tensor.py --models all

# Total: ~773 MB
```

### Example 4: OCR Only

```bash
# Download only OCR models (if you already have vision models)
python download-tensor.py --models none

# Total: ~133 MB
```

## Model URLs

Models are downloaded from official sources:

**Vision Models:**
- Google Cloud Storage (TensorFlow/Keras official)
- https://storage.googleapis.com/tensorflow/keras-applications/

**OCR Models:**
- GitHub Releases (Keras-OCR official)
- https://github.com/faustomorales/keras-ocr/releases/

## What Happens Next?

After downloading models:

1. **Install TensorFlow** (if not already):
   ```bash
   pip install tensorflow keras-ocr
   ```

2. **Models are ready** to use by Deep Sight processors

3. **No re-download** needed - models are cached locally

## Troubleshooting

### Download Fails

**Error:** Connection timeout or network error

**Solution:**
```bash
# Try again - download will resume
python download-tensor.py

# Or download manually using curl/wget
# URLs are shown in the output
```

### Disk Space

**Check available space:**
```bash
# Windows
Get-PSDrive C

# Linux/Mac
df -h
```

**Recommended space:**
- Minimal setup: 200 MB
- Recommended: 500 MB
- Complete: 1 GB

### Already Downloaded

If models exist, the script will skip them:

```
ResNet50:
  Already exists: D:\...\tensor\models\resnet50_weights_tf_dim_ordering_tf_kernels.h5
  Skipping download.
```

To re-download, delete the existing files first.

## Integration with Deep Sight

These models are used by:

1. **TextExtractor** - Uses OCR models for text extraction
2. **ImageProcessor** - Can use vision models for advanced features (future)
3. **LLMAgent** - Models available for local processing (future)

## Performance Notes

### Download Time

| Connection | ResNet50 | All Models |
|-----------|----------|------------|
| Fast (100 Mbps) | ~10 seconds | ~1 minute |
| Medium (20 Mbps) | ~1 minute | ~5 minutes |
| Slow (5 Mbps) | ~3 minutes | ~15 minutes |

### First Use

After download:
- **First run**: Models loaded into memory (~5-10 seconds)
- **Subsequent runs**: Instant (models cached)

## FAQ

**Q: Do I need TensorFlow installed to run this script?**
A: No! This script uses only Python's built-in `urllib` for downloads.

**Q: Will models download automatically when I use Deep Sight?**
A: Keras-OCR will auto-download on first use. This script allows pre-downloading.

**Q: Can I use different model versions?**
A: Yes, but you'll need to modify the URLs in the script.

**Q: Where are models stored?**
A: In the `tensor/` directory in your Deep Sight installation.

**Q: Can I delete models I don't need?**
A: Yes, but OCR models are required for text extraction.

**Q: Do models work offline?**
A: Yes, once downloaded, no internet connection is needed.

## Summary

**Quick download:**
```bash
python download-tensor.py
```

**Custom download:**
```bash
python download-tensor.py --models <choice> [--no-ocr]
```

**Choices:** `resnet50`, `mobilenet`, `vgg16`, `all`, `none`

Models are cached locally and ready for immediate use by Deep Sight! 🚀
