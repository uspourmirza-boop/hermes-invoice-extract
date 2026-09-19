#!/usr/bin/env python3
"""
Hermes Invoice & Receipt Data Extraction Pipeline
==================================================

Extracts structured data from invoice/receipt images using Tesseract OCR.
Designed for production use — handles real-world scan quality, multiple vendors,
and common failure modes.

Usage:
    python extract.py image.png
    python extract.py image.png --lang eng+deu
    python extract.py image.png --output json
"""

import re
import json
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

try:
    import pytesseract
    from PIL import Image, ImageFilter, ImageEnhance
except ImportError:
    print("ERROR: Install dependencies first: pip install pytesseract Pillow")
    print("       Also install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
    sys.exit(1)


def preprocess(image_path):
    """
    Prepare an image for OCR.
    
    Applies: grayscale, contrast enhancement, mild sharpening, threshold.
    Handles typical real-world scans: low contrast, slight rotation, noise.
    """
    img = Image.open(image_path)
    
    # Convert to grayscale
    if img.mode != 'L':
        img = img.convert('L')
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)
    
    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)
    
    # Apply threshold for clean black/white
    threshold = 140
    img = img.point(lambda p: 255 if p > threshold else 0)
    
    return img


def extract_text(image_path, lang='eng'):
    """
    Run Tesseract OCR on an image and return raw text.
    """
    img = preprocess(image_path)
    
    # PSM 3 = fully automatic page segmentation
    # PSM 6 = uniform block of text (better for receipts)
    try:
        text = pytesseract.image_to_string(
            img,
            lang=lang,
            config='--psm 3 --oem 3'
        )
    except pytesseract.TesseractError:
        # Fallback to psm 6 for simple receipts
        text = pytesseract.image_to_string(
            img,
            lang=lang,
            config='--psm 6 --oem 3'
        )
    
    return text.strip()


def extract_vendor(text):
    """
    Extract vendor name from invoice text.
    
    Strategy: first non-empty line that's not a common header word.
    Most invoices put vendor name at the top.
    """
    lines = text.split('\n')
    skip_words = {'invoice', 'receipt', 'bill', 'tax', 'vat', 'rechnung',
                  'factura', 'date', 'page', 'tel', 'fax', 'www', 'http'}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        lower = line.lower()
        if any(lower.startswith(s) for s in skip_words):
            continue
        if len(line) < 3:
            continue
        if re.match(r'^[\d\-\.\:\/\s]+$', line):
            continue
        return line
    
    return None


def extract_date(text):
    """
    Extract the invoice date.
    
    Tries multiple formats: MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD,
    "Month DD, YYYY", "DD Month YYYY".
    """
    patterns = [
        # MM/DD/YYYY or DD/MM/YYYY
        r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        # YYYY-MM-DD
        r'(\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})',
        # Month DD, YYYY
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+\d{4})',
        # DD Month YYYY
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4})',
        # DD.MM.YYYY (German/European)
        r'(\d{1,2}\.\d{1,2}\.\d{4})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[0]
    
    return None


def extract_total(text):
    """
    Extract the invoice total amount.
    
    Looks for patterns like:
    - Total: $1,234.56
    - Amount Due: 1.234,56 EUR
    - Grand Total 1234.56
    
    Returns the largest monetary amount found on the document.
    This handles cases where subtotal, tax, and total are all present.
    """
    # Find all monetary amounts
    amounts = re.findall(r'[\$\€\£\¥]?\s*([\d,]+\.?\d*)', text)
    amounts += re.findall(r'[\$\€\£\¥]?\s*([\d\.]+,\d{2})', text)
    
    if not amounts:
        return None
    
    # Normalize and find largest
    normalized = []
    for amt in amounts:
        # Handle European format (1.234,56)
        if ',' in amt and '.' in amt:
            if amt.index(',') > amt.index('.'):
                amt = amt.replace('.', '').replace(',', '.')
            else:
                amt = amt.replace(',', '')
        elif ',' in amt:
            # Could be 1,234 or 1,23 (European)
            parts = amt.split(',')
            if len(parts[-1]) == 2:
                amt = amt.replace(',', '.')
            else:
                amt = amt.replace(',', '')
        
        try:
            normalized.append(float(amt))
        except ValueError:
            continue
    
    if not normalized:
        return None
    
    return str(max(normalized))


def extract_invoice_number(text):
    """
    Extract invoice/receipt number.
    
    Looks for patterns like:
    - Invoice #: INV-2026-0342
    - Receipt No. R-12345
    - Rechnungsnummer: RE-2026-001
    """
    patterns = [
        r'(?:invoice|receipt|rechnung|factura|bill)\s*(?:#|no|num|nummer|n[úu]mero)?[\.:]?\s*([A-Z0-9\-\/]+)',
        r'(?:#|no)\s*[:.]?\s*([A-Z]{0,3}[\-\/]?\d{3,})',
        r'(?:ref|reference|referenz)\s*[\.:]?\s*([A-Z0-9\-\/]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            if len(candidate) >= 3:
                return candidate
    
    return None


def extract_line_items(text):
    """
    Extract line items from the invoice body.
    
    Looks for lines with description + amount pattern:
    - Description ... $123.45
    - 2x Widget ... $24.99
    
    This is the hardest field. Accuracy depends on document layout.
    """
    items = []
    lines = text.split('\n')
    
    for line in lines:
        # Look for lines ending with a monetary amount
        match = re.match(
            r'^(.+?)\s+[\$\€\£\¥]?\s*([\d,]+\.\d{2})\s*$',
            line.strip()
        )
        if match:
            desc = match.group(1).strip()
            amt = match.group(2)
            # Skip if description is too short or looks like a total
            if len(desc) < 5:
                continue
            if any(w in desc.lower() for w in ['total', 'subtotal', 'tax', 'vat', 'sum']):
                continue
            items.append({
                'description': desc,
                'amount': amt
            })
    
    return items


def extract(image_path, lang='eng'):
    """
    Main extraction function.
    
    Takes an image path, returns structured data.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    text = extract_text(image_path, lang)
    
    return {
        'vendor': extract_vendor(text),
        'date': extract_date(text),
        'total': extract_total(text),
        'invoice_number': extract_invoice_number(text),
        'line_items': extract_line_items(text),
        'raw_text': text
    }


def main():
    parser = argparse.ArgumentParser(
        description='Extract structured data from invoice/receipt images'
    )
    parser.add_argument('image', help='Path to image file')
    parser.add_argument('--lang', default='eng', help='OCR language (default: eng)')
    parser.add_argument('--output', choices=['json', 'pretty'], default='pretty',
                       help='Output format')
    
    args = parser.parse_args()
    
    try:
        result = extract(args.image, args.lang)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    if args.output == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*50}")
        print(f"  EXTRACTED INVOICE DATA")
        print(f"{'='*50}")
        print(f"  Vendor:         {result['vendor'] or 'NOT FOUND'}")
        print(f"  Date:           {result['date'] or 'NOT FOUND'}")
        print(f"  Total:          {result['total'] or 'NOT FOUND'}")
        print(f"  Invoice #:      {result['invoice_number'] or 'NOT FOUND'}")
        print(f"  Line Items:     {len(result['line_items'])} found")
        for i, item in enumerate(result['line_items'], 1):
            print(f"    {i}. {item['description'][:40]:40s} ${item['amount']}")
        print(f"{'='*50}\n")


if __name__ == '__main__':
    main()
