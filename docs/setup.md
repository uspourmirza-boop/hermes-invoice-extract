# Setup Guide

## 5-Minute Installation

### Step 1: Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr
```

**Windows:**
Download installer from: https://github.com/UB-Mannheim/tesseract/wiki

**Termux (Android):**
```bash
pkg install tesseract
```

### Step 2: Install Python Dependencies

```bash
pip install pytesseract Pillow
```

### Step 3: Verify Installation

```bash
# Check Tesseract is installed
tesseract --version

# Check Python can find it
python -c "import pytesseract; print('OK')"
```

### Step 4: Test with Sample

```bash
python src/extract.py tests/sample_invoice.png
```

## Optional: Install Additional Language Packs

```bash
# German
sudo apt install tesseract-ocr-deu

# French
sudo apt install tesseract-ocr-fra

# Spanish
sudo apt install tesseract-ocr-spa

# List all available
tesseract --list-langs
```

## Optional: PDF Support

To extract from PDF invoices, convert to images first:

```bash
# Using poppler (recommended)
sudo apt install poppler-utils
pdftoppm -png -r 300 invoice.pdf invoice_page

# Using ImageMagick
convert -density 300 invoice.pdf invoice_page-%02d.png
```

Then run extraction on the resulting images.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `TesseractNotFoundError` | Tesseract binary not in PATH. Install it or set `pytesseract.pytesseract.tesseract_cmd = '/path/to/tesseract'` |
| `TesseractError: failed` | Language pack not installed. Run `tesseract --list-langs` to check |
| Very low accuracy | Image quality too low. Scan at 300+ DPI, increase contrast, straighten |
| Wrong language | Install the correct language pack and pass `--lang` flag |
