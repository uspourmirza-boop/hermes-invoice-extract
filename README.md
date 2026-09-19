# Hermes Invoice Extractor

> **Upload an invoice or receipt image. Get back structured data instantly.**

## Live Demo

**Interactive Web App:** [Hugging Face Spaces](https://huggingface.co/spaces/uspourmirza-boop/hermes-invoice-extract)

Try it right now — upload any invoice or receipt image and see structured data extracted in seconds.

## What It Does

This is a **production-grade OCR pipeline** that extracts structured data from invoice and receipt images:

- Vendor / Company name
- Invoice date & due date
- Total amount, subtotal, tax
- Invoice / Receipt number
- Line items (description, quantity, unit price, amount)
- Multi-currency support ($, €, £, ¥)
- Multi-date-format parsing

Output as clean JSON — ready to pipe into your accounting software, spreadsheet, or database.

## Quick Start

```bash
# Clone
git clone https://github.com/uspourmirza-boop/hermes-invoice-extract.git
cd hermes-invoice-extract

# Install dependencies
pip install -r requirements.txt

# Run the web demo locally
python app.py
# → Opens at http://localhost:7860
```

## CLI Usage

```bash
# Extract from a single image
python src/extract.py path/to/invoice.jpg

# Batch process a folder
python src/batch.py path/to/invoices/ output.json
```

## API Usage

```python
from src.extract import extract_invoice
import json

result = extract_invoice("invoice.jpg")
print(json.dumps(result, indent=2))
```

## Why This Exists

Manual invoice data entry costs **$5-20 per invoice** and takes 5-15 minutes. This tool does it in **seconds** for **free**.

Built for accountants, bookkeepers, small business owners, and anyone drowning in paper receipts.

## How It Works

```
Image → Tesseract OCR → Image Preprocessing → Regex Parsing → Structured JSON
```

- **Tesseract OCR**: Industry-standard open-source OCR engine
- **Image Preprocessing**: Contrast enhancement, sharpening, denoising, 2x upscale
- **Regex Parsing**: Multi-pattern extraction with fallbacks for common invoice formats

## Performance

- **Speed**: ~2-5 seconds per image (depends on size and quality)
- **Accuracy**: ~85-95% on clear printed text; lower on handwritten or very low-quality images
- **Languages**: Optimized for English; Tesseract supports 100+ languages with language packs
- **Image types**: JPG, PNG, BMP, TIFF

## License

MIT — use commercially, modify, redistribute. No attribution required.

## Part of the Hermes Economic Engine

This is **Stage 0** of an autonomous economic engine — free digital products that generate distribution and prove demand.

[Learn more about the engine](https://github.com/uspourmirza-boop/hermes-engine)
