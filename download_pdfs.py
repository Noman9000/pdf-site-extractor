#!/usr/bin/env python3
"""
PDF Downloader - Download PDFs from a list of URLs
Usage: python download_pdfs.py pdf_list.txt
       python download_pdfs.py --url "https://example.com/file.pdf"
"""

import requests
import os
import sys
import argparse
from urllib.parse import urlparse

def download_pdf(url, output_dir="pdfs", session=None):
    """Download a single PDF"""
    if session is None:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    try:
        # Get filename from URL
        filename = os.path.basename(urlparse(url).path)
        if not filename or not filename.endswith('.pdf'):
            filename = f"document_{hash(url)}.pdf"
        
        filepath = os.path.join(output_dir, filename)
        
        print(f"Downloading: {filename}... ", end="", flush=True)
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        file_size = len(response.content) / 1024  # KB
        print(f"✓ ({file_size:.1f} KB)")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def download_from_file(input_file, output_dir="pdfs"):
    """Download all PDFs from a text file containing URLs"""
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found")
        return
    
    # Read URLs
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not urls:
        print("No URLs found in file")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Found {len(urls)} PDF URLs")
    print(f"Downloading to: {output_dir}/\n")
    
    # Download all
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    success = 0
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] ", end="")
        if download_pdf(url, output_dir, session):
            success += 1
    
    print(f"\n✓ Complete: {success}/{len(urls)} PDFs downloaded successfully")

def main():
    parser = argparse.ArgumentParser(
        description='Download PDF files from URLs'
    )
    parser.add_argument(
        'input',
        nargs='?',
        default='pdf_list.txt',
        help='Text file with PDF URLs (one per line) or use --url for single download'
    )
    parser.add_argument(
        '--url',
        help='Download a single PDF from URL'
    )
    parser.add_argument(
        '--output',
        default='pdfs',
        help='Output directory (default: pdfs)'
    )
    
    args = parser.parse_args()
    
    if args.url:
        # Single URL download
        os.makedirs(args.output, exist_ok=True)
        download_pdf(args.url, args.output)
    else:
        # Download from file
        download_from_file(args.input, args.output)

if __name__ == "__main__":
    main()
