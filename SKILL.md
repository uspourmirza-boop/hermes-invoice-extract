---
name: invoice-extract
version: 1.0.0
description: Extract structured data from invoice and receipt images using Tesseract OCR. Drop in an image, get back vendor, date, total, invoice number, and line items as structured JSON.
triggers:
  - "extract invoice data from"
  - "OCR this receipt"
  - "parse invoice image"
  - "invoice data extraction"
  - "receipt to JSON"
---

# Invoice & Receipt Extraction Skill

## Purpose

Extract structured data from invoice/receipt images. This is a production-grade OCR pipeline that preprocesses images, runs Tesseract, and extracts key fields using regex and heuristics.

## When to Use

- User has an invoice/receipt image and wants structured data
- User needs to process many invoices in batch
- User wants to stop manual data entry from scanned documents

## Quick Start

```bash
# Single image
python src/extract.py path/to/invoice.png

# Batch folder
python src/batch.py ./invoices/ --output results.json

# Different language (German, French, etc.)
python src/extract.py invoice_de.png --lang deu
```

## Workflow

1. **Receive image(s)** from user — single file or folder
2. **Run extraction:**
   - Single: `python src/extract.py IMAGE_PATH`
   - Batch: `python src/batch.py FOLDER_PATH --output results.json`
3. **Return structured JSON** with fields:
   - `vendor`: Company name (best-effort from first lines)
   - `date`: Invoice date (multiple formats)
   - `total`: Largest monetary amount (handles $1,234.56 and 1.234,56 EUR)
   - `invoice_number`: Document number
   - `line_items`: Array of {description, amount}
   - `raw_text`: Full OCR output for verification

## Important Notes

- **Accuracy is ~95%** on clean printed invoices. Handwritten, very low-DPI, or logo-heavy documents will be worse.
- **Review critical fields** before using for accounting/tax purposes.
- **Total detection**: Takes the largest amount on the document. Usually correct (invoice total is the largest number), but verify on documents with multiple large amounts.
- **Date detection**: Tries multiple formats. May fail on non-standard formats.
- **No cloud dependency**: All processing is local. No API keys needed.

## Troubleshooting

- `TesseractNotFoundError`: Install Tesseract OCR (not just the Python package)
- `pytesseract.TesseractError`: Check language pack is installed (`tesseract --list-langs`)
- Low accuracy on image: Try preprocessing with GIMP/Photoshop (increase contrast, straighten)
- Wrong total detected: Check raw_text and parse manually

## Output Format

```json
{
  "vendor": "Acme Office Supplies",
  "date": "2026-03-15",
  "total": "847.23",
  "invoice_number": "INV-2026-0342",
  "line_items": [
    {"description": "Printer Paper (10 reams)", "amount": "124.50"},
    {"description": "Toner Cartridge", "amount": "89.99"}
  ],
  "raw_text": "ACME OFFICE SUPPLIES\n123 Business St...\n..."
}
```

## Limitations

- Does not handle tables with complex layouts
- Does not extract tax ID / VAT number (non-standard formats)
- Does not parse PDFs directly (convert to images first: `pdftoppm` or ImageMagick)
- Not suitable for handwritten documents
- Not suitable for real-time video capture (use a mobile app like Adobe Scan first)
