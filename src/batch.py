#!/usr/bin/env python3
"""
Batch processor for invoices and receipts.

Processes an entire folder of images and writes results to JSON.
Usage:
    python batch.py ./invoices/ --output results.json
    python batch.py ./invoices/ --lang eng+deu --output results.json
"""

import os
import json
import argparse
from pathlib import Path
from extract import extract

SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'}


def batch_process(folder_path, lang='eng', output_path=None):
    """Process all images in a folder."""
    folder = Path(folder_path)
    if not folder.is_dir():
        print(f"ERROR: {folder_path} is not a directory")
        return []

    results = []
    image_files = [
        f for f in folder.iterdir()
        if f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not image_files:
        print(f"No image files found in {folder_path}")
        return []

    print(f"Processing {len(image_files)} images...\n")

    for i, image_file in enumerate(sorted(image_files), 1):
        print(f"[{i}/{len(image_files)}] {image_file.name}...", end=' ')
        try:
            result = extract(str(image_file), lang)
            result['source_file'] = image_file.name
            results.append(result)
            print(f"OK — {result['vendor'] or 'unknown'}, ${result['total'] or '?.??'}")
        except Exception as e:
            print(f"FAIL — {e}")
            results.append({
                'source_file': image_file.name,
                'error': str(e)
            })

    print(f"\nDone. Processed {len(results)} files.")

    if output_path:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {output_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description='Batch process invoice images')
    parser.add_argument('folder', help='Path to folder of images')
    parser.add_argument('--lang', default='eng', help='OCR language')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    args = parser.parse_args()

    batch_process(args.folder, args.lang, args.output)


if __name__ == '__main__':
    main()
