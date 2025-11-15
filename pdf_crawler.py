#!/usr/bin/env python3
"""
PDF Crawler for Hey Telecom Support Site
Crawls a website and its subpages to find and optionally download PDF files.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
from collections import deque
import argparse


class PDFCrawler:
    def __init__(self, base_url, max_depth=3, delay=1.0):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.delay = delay
        self.visited_urls = set()
        self.pdf_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def is_valid_url(self, url):
        """Check if URL belongs to the same domain and path"""
        parsed = urlparse(url)
        
        # Must be same domain
        if parsed.netloc != self.base_domain:
            return False
        
        # Must start with the base path
        base_path = urlparse(self.base_url).path
        if not parsed.path.startswith(base_path):
            return False
        
        return True

    def is_pdf(self, url):
        """Check if URL points to a PDF"""
        return url.lower().endswith('.pdf')

    def get_page_links(self, url):
        """Extract all links from a page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = set()
            
            # Find all <a> tags with href
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                # Remove fragments
                full_url = full_url.split('#')[0]
                
                if self.is_pdf(full_url):
                    self.pdf_urls.add(full_url)
                    print(f"  📄 Found PDF: {full_url}")
                elif self.is_valid_url(full_url):
                    links.add(full_url)
            
            return links
            
        except Exception as e:
            print(f"  ❌ Error fetching {url}: {e}")
            return set()

    def crawl(self):
        """Crawl the website using BFS"""
        print(f"🚀 Starting crawl from: {self.base_url}")
        print(f"📊 Max depth: {self.max_depth}\n")
        
        # Queue: (url, depth)
        queue = deque([(self.base_url, 0)])
        self.visited_urls.add(self.base_url)
        
        while queue:
            url, depth = queue.popleft()
            
            if depth > self.max_depth:
                continue
            
            print(f"🔍 Crawling (depth {depth}): {url}")
            
            # Get links from this page
            links = self.get_page_links(url)
            
            # Add new links to queue
            for link in links:
                if link not in self.visited_urls:
                    self.visited_urls.add(link)
                    queue.append((link, depth + 1))
            
            # Be polite - delay between requests
            time.sleep(self.delay)
        
        print(f"\n✅ Crawl complete!")
        print(f"📄 Total PDFs found: {len(self.pdf_urls)}")
        print(f"🔗 Total pages crawled: {len(self.visited_urls)}")

    def list_pdfs(self):
        """List all found PDFs"""
        if not self.pdf_urls:
            print("\n❌ No PDFs found")
            return
        
        print("\n📋 List of PDFs:")
        print("-" * 80)
        for i, pdf_url in enumerate(sorted(self.pdf_urls), 1):
            print(f"{i}. {pdf_url}")

    def download_pdfs(self, output_dir="pdfs"):
        """Download all found PDFs"""
        if not self.pdf_urls:
            print("\n❌ No PDFs to download")
            return
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        print(f"\n⬇️  Downloading {len(self.pdf_urls)} PDFs to '{output_dir}/'")
        
        for i, pdf_url in enumerate(sorted(self.pdf_urls), 1):
            try:
                # Get filename from URL
                filename = os.path.basename(urlparse(pdf_url).path)
                if not filename or not filename.endswith('.pdf'):
                    filename = f"document_{i}.pdf"
                
                filepath = os.path.join(output_dir, filename)
                
                # Download
                print(f"  [{i}/{len(self.pdf_urls)}] Downloading: {filename}... ", end="")
                response = self.session.get(pdf_url, timeout=30)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content) / 1024  # KB
                print(f"✅ ({file_size:.1f} KB)")
                
                time.sleep(self.delay)
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print(f"\n✅ Download complete! Files saved in '{output_dir}/'")

    def save_pdf_list(self, filename="pdf_list.txt"):
        """Save PDF URLs to a text file"""
        with open(filename, 'w') as f:
            for pdf_url in sorted(self.pdf_urls):
                f.write(f"{pdf_url}\n")
        print(f"\n💾 PDF list saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Crawl a website and find/download PDF files'
    )
    parser.add_argument(
        'url',
        nargs='?',
        default='https://www.heytelecom.be/fr/aide-et-support',
        help='Base URL to crawl (default: Hey Telecom support page)'
    )
    parser.add_argument(
        '--depth',
        type=int,
        default=3,
        help='Maximum crawl depth (default: 3)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--download',
        action='store_true',
        help='Download all found PDFs'
    )
    parser.add_argument(
        '--output',
        default='pdfs',
        help='Output directory for downloads (default: pdfs)'
    )
    parser.add_argument(
        '--save-list',
        action='store_true',
        help='Save PDF URLs to a text file'
    )
    
    args = parser.parse_args()
    
    # Create crawler
    crawler = PDFCrawler(args.url, max_depth=args.depth, delay=args.delay)
    
    # Crawl the site
    crawler.crawl()
    
    # List PDFs
    crawler.list_pdfs()
    
    # Save list if requested
    if args.save_list:
        crawler.save_pdf_list()
    
    # Download if requested
    if args.download:
        crawler.download_pdfs(args.output)
    else:
        print("\n💡 Tip: Run with --download to download all PDFs")


if __name__ == "__main__":
    main()
