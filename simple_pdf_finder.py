#!/usr/bin/env python3
"""
Simple PDF Finder - Quick script to find all PDFs on a website
Usage: python simple_pdf_finder.py
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

BASE_URL = "https://www.heytelecom.be/fr/aide-et-support"

def find_all_pdfs(base_url):
    """Find all PDFs on a website and its subpages"""
    visited = set()
    pdfs = set()
    queue = deque([base_url])
    base_domain = urlparse(base_url).netloc
    base_path = urlparse(base_url).path
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    print(f"Scanning: {base_url}\n")
    
    while queue:
        url = queue.popleft()
        if url in visited:
            continue
            
        visited.add(url)
        print(f"Checking: {url}")
        
        try:
            response = session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href']).split('#')[0]
                parsed = urlparse(full_url)
                
                # Check if it's a PDF
                if full_url.lower().endswith('.pdf'):
                    pdfs.add(full_url)
                    print(f"  ✓ PDF found: {full_url}")
                
                # Check if we should crawl this link
                elif (parsed.netloc == base_domain and 
                      parsed.path.startswith(base_path) and 
                      full_url not in visited):
                    queue.append(full_url)
                    
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    return pdfs, visited

if __name__ == "__main__":
    pdfs, pages = find_all_pdfs(BASE_URL)
    
    print("\n" + "="*60)
    print(f"RESULTS:")
    print(f"  Pages scanned: {len(pages)}")
    print(f"  PDFs found: {len(pdfs)}")
    print("="*60)
    
    if pdfs:
        print("\nPDF URLs:")
        for i, pdf in enumerate(sorted(pdfs), 1):
            print(f"  {i}. {pdf}")
        
        # Save to file
        with open('found_pdfs.txt', 'w') as f:
            for pdf in sorted(pdfs):
                f.write(f"{pdf}\n")
        print(f"\n✓ PDF list saved to: found_pdfs.txt")
    else:
        print("\nNo PDFs found.")
