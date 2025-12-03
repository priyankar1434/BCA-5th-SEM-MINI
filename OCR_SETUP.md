# OCR Functionality Setup Guide

This vehicle authorization system now includes **Optical Character Recognition (OCR)** functionality to automatically detect and extract license plates from images.

## How It Works

The system uses a **dual-mode OCR approach**:

1. **Backend OCR (Primary)**: Uses Tesseract OCR via pytesseract for faster, server-side processing
2. **Browser OCR (Fallback)**: Uses Tesseract.js for client-side processing if backend is unavailable

### Features

✅ **Automatic License Plate Detection**: When you upload or capture an image, the system automatically detects license plates
✅ **Seamless Integration**: Detected plates are automatically populated in the license field
✅ **Manual Override**: Users can still manually enter or select different detected plates
✅ **Pattern Recognition**: Supports Indian license plate formats (e.g., MH12AB1234)
✅ **Dual Processing**: Falls back to browser-based OCR if Tesseract is not installed

## Installation

### Python Dependencies (Already Installed)

```bash
pip install pytesseract pillow
```

### Tesseract OCR Engine (Optional but Recommended)

For best performance, install Tesseract OCR engine on your system:

#### On Windows:

1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run: `tesseract-ocr-w64-setup-v5.x.exe` (latest version)
3. During installation, choose default location: `C:\Program Files\Tesseract-OCR`
4. After installation, the system will automatically detect and use it

#### On macOS:

```bash
brew install tesseract
```

#### On Linux (Ubuntu/Debian):

```bash
sudo apt-get install tesseract-ocr
```

## Usage

### Upload Image
1. Click "Upload Image" card
2. Drag & drop or browse an image containing a vehicle license plate
3. The system automatically extracts the license plate text
4. **Detected plates appear as clickable buttons** - select one or enter manually
5. Click "Upload & Scan" to verify the vehicle

### Camera Capture
1. Click "Scan Using Camera" card
2. Click "Start Camera" to enable camera access
3. Click the camera icon to capture
4. The system automatically extracts the license plate from the captured frame
5. Vehicle authorization status is shown immediately

## Features

### Smart License Plate Detection
- Recognizes Indian license plate formats
- Patterns supported:
  - `MH12AB1234` (Standard format)
  - `MH12A1234` (Alternative format)
  - `MH1AB1234` (Variations)

### Fallback Mechanism
- If Tesseract is not installed, the browser-based Tesseract.js automatically takes over
- No need to manually switch modes - it happens automatically
- Browser OCR works without any additional installation

## Troubleshooting

### No plates detected?
- Ensure the image has a clear, well-lit license plate
- Try a different angle or lighting
- The system will display raw extracted text in the console for debugging

### Tesseract not found?
- The system will automatically fall back to browser-based OCR
- For backend processing, install Tesseract following the instructions above
- After installation, restart the Flask application

### Performance Issues?
- Backend OCR (Tesseract) is faster for most cases
- Browser OCR (Tesseract.js) may take longer but requires no installation
- Large images may take more time to process

## Technical Details

### Backend Processing (app.py)
- **Endpoint**: `/ocr` (POST)
- **Input**: Image file (multipart/form-data)
- **Output**: JSON with detected_plates array
- **Patterns**: Regex-based Indian license plate format detection

### Frontend Processing (JavaScript)
- **Library**: Tesseract.js v5.0.0
- **Processing**: Client-side, browser-based OCR
- **Fallback**: Automatic if backend fails
- **Pattern Extraction**: Client-side regex matching

## File Changes

Modified files:
- `app.py` - Added OCR endpoint and extraction logic
- `templates/index.html` - Added OCR UI and JavaScript processing
- `static/premium.css` - Added styling for detected plates display

New dependencies:
- pytesseract (Python)
- Tesseract OCR Engine (System-level, optional)
- Tesseract.js (Browser-based, via CDN)

## Example Output

When an image with a license plate is uploaded:

```json
{
  "success": true,
  "raw_text": "MH 12 AB 1234",
  "detected_plates": ["MH12AB1234"]
}
```

The detected plate is then:
1. Displayed as a clickable button in the UI
2. Automatically selected as the default value
3. Verified against the vehicle database
4. Recorded with the image upload

---

**For any issues or questions, check the browser console (F12) for detailed error messages.**
