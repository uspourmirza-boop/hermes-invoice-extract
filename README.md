[![Build Status](https://img.shields.io/badge/status-live-brightgreen)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)]()
[![Tesseract](https://img.shields.io/badge/Tesseract-OCR-green)]()

# Hermes Invoice Extractor

> **Upload an invoice or receipt. Get back structured JSON data in seconds.**

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

## Why This Exists

Manual invoice data entry costs **$5-20 per invoice** and takes 5-15 minutes. This tool does it in **seconds** for **free**.

Built for accountants, bookkeepers, small business owners, and anyone drowning in paper receipts.

## Features

| Feature | Detail |
|---------|--------|
| **Vendor detection** | Auto-identifies company from invoice header |
| **Date parsing** | Multi-format support (YYYY-MM-DD, MM/DD/YYYY, Month DD, YYYY) |
| **Multi-currency** | $, €, £, ¥ auto-detection |
| **Line items** | Description, quantity, unit price, total per line |
| **JSON output** | Clean structured data, ready for any downstream system |
| **Batch mode** | Process entire folders of invoices at once |
| **Zero cost** | No API keys, no subscriptions, no vendor lock-in |

## How It Works

```
Image → Tesseract OCR → Image Preprocessing → Regex Parsing → Structured JSON
```

1. **Image preprocessing** — Converts to grayscale, 2x upscale, enhances contrast and sharpness, applies median filter for noise reduction
2. **Tesseract OCR** — Industry-standard open-source OCR engine with optimized PSM modes
3. **Regex parsing** — Multi-pattern extraction with fallbacks for common invoice formats
4. **JSON output** — Structured data with vendor, dates, totals, invoice number, and line items

## Performance

- **Speed**: ~2-5 seconds per image (depends on size and quality)
- **Accuracy**: ~85-95% on clear printed text; lower on handwritten or very low-quality images
- **Languages**: Optimized for English; Tesseract supports 100+ languages
- **Image types**: JPG, PNG, BMP, TIFF

## Pricing Comparison

| Metric | Manual Entry | Hermes Extractor |
|--------|-------------|------------------|
| Time per invoice | 5-15 minutes | 2-5 seconds |
| Cost per invoice | $5-20 | $0 |
| Setup time | None | 2 minutes |
| Scalability | Linear | Instant |

For a business processing 100 invoices/month, Hermes saves **~$500-2,000/month** in manual labor costs.

## Installation

### Prerequisites

- Python 3.8+
- Tesseract OCR (install instructions in [docs/setup.md](docs/setup.md))

```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt update && sudo apt install tesseract-ocr
```

### Install

```bash
pip install -r requirements.txt
```

## License

MIT — use commercially, modify, redistribute. No attribution required.

## Part of the Hermes Economic Engine

This is **Stage 0** of an autonomous economic engine — free digital products that generate distribution and prove demand.

[Learn more about the engine](https://github.com/uspourmirza-boop/hermes-engine)
