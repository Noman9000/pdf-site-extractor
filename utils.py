#!/usr/bin/env python3
"""
Utilities for PDF Site Extractor
Handles directory management, domain sanitization, and session tracking
"""

import os
import re
import json
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path


def sanitize_domain(url):
    """
    Extract and sanitize domain name from URL for directory naming

    Examples:
        https://www.heytelecom.be/path -> heytelecom.be
        https://docs.example.com:8080/path -> docs.example.com_8080
        https://example.com/path -> example.com
    """
    parsed = urlparse(url)
    domain = parsed.netloc

    # Remove www. prefix if present (but keep other subdomains)
    if domain.startswith('www.'):
        domain = domain[4:]

    # Replace : with _ for ports
    domain = domain.replace(':', '_')

    # Sanitize for filesystem (remove any remaining invalid chars)
    domain = re.sub(r'[^\w\.\-]', '_', domain)

    return domain


def get_timestamp():
    """Get current timestamp in format: 2025-11-15_14-45-23"""
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def create_session_directory(url, custom_name=None):
    """
    Create organized directory structure for a scan session

    Returns: (session_path, pdfs_path)
    """
    domain = sanitize_domain(url)

    if custom_name:
        # Sanitize custom name
        custom_name = re.sub(r'[^\w\-]', '_', custom_name)
        session_name = custom_name
    else:
        session_name = get_timestamp()

    # Create paths
    base_path = Path('data') / domain / session_name
    pdfs_path = base_path / 'pdfs'

    # Create directories
    pdfs_path.mkdir(parents=True, exist_ok=True)

    return str(base_path), str(pdfs_path)


def save_metadata(session_path, metadata):
    """
    Save session metadata to JSON file

    metadata should include:
        - url
        - depth
        - delay
        - timestamp
        - pages_scanned
        - pdfs_found
        - pdfs_downloaded
        - total_size_mb
    """
    metadata_file = Path(session_path) / 'metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)


def save_scan_report(session_path, metadata, pdf_urls):
    """Save human-readable scan report"""
    report_file = Path(session_path) / 'scan_report.txt'

    with open(report_file, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("PDF EXTRACTION REPORT\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"URL:            {metadata.get('url', 'N/A')}\n")
        f.write(f"Date:           {metadata.get('timestamp', 'N/A')}\n")
        f.write(f"Depth:          {metadata.get('depth', 'N/A')} levels\n")
        f.write(f"Delay:          {metadata.get('delay', 'N/A')}s\n\n")

        f.write(f"Pages Scanned:  {metadata.get('pages_scanned', 0)}\n")
        f.write(f"PDFs Found:     {metadata.get('pdfs_found', 0)}\n")
        f.write(f"PDFs Downloaded: {metadata.get('pdfs_downloaded', 0)}\n")
        f.write(f"Total Size:     {metadata.get('total_size_mb', 0):.2f} MB\n\n")

        f.write("=" * 60 + "\n")
        f.write("PDF URLS\n")
        f.write("=" * 60 + "\n\n")

        for i, pdf_url in enumerate(sorted(pdf_urls), 1):
            f.write(f"{i}. {pdf_url}\n")


def save_pdf_list(session_path, pdf_urls):
    """Save PDF URLs to text file"""
    list_file = Path(session_path) / 'found_pdfs.txt'
    with open(list_file, 'w') as f:
        for pdf_url in sorted(pdf_urls):
            f.write(f"{pdf_url}\n")


def get_all_sessions(domain=None):
    """
    Get list of all previous sessions, optionally filtered by domain

    Returns: List of dicts with session info
    """
    sessions = []
    data_path = Path('data')

    if not data_path.exists():
        return sessions

    # If domain specified, only look in that domain's folder
    if domain:
        domain_dirs = [data_path / domain] if (data_path / domain).exists() else []
    else:
        domain_dirs = [d for d in data_path.iterdir() if d.is_dir()]

    for domain_dir in domain_dirs:
        for session_dir in domain_dir.iterdir():
            if not session_dir.is_dir():
                continue

            # Try to load metadata
            metadata_file = session_dir / 'metadata.json'
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)

                    sessions.append({
                        'domain': domain_dir.name,
                        'session_name': session_dir.name,
                        'path': str(session_dir),
                        'metadata': metadata
                    })
                except:
                    # If metadata can't be loaded, create basic info
                    sessions.append({
                        'domain': domain_dir.name,
                        'session_name': session_dir.name,
                        'path': str(session_dir),
                        'metadata': {}
                    })

    # Sort by timestamp (newest first)
    sessions.sort(key=lambda x: x['metadata'].get('timestamp', ''), reverse=True)

    return sessions


def get_session_size_mb(session_path):
    """Calculate total size of PDFs in a session"""
    pdfs_path = Path(session_path) / 'pdfs'
    if not pdfs_path.exists():
        return 0.0

    total_size = 0
    for pdf_file in pdfs_path.glob('*.pdf'):
        total_size += pdf_file.stat().st_size

    return total_size / (1024 * 1024)  # Convert to MB


def delete_session(session_path):
    """Delete a session directory and all its contents"""
    import shutil
    session_path = Path(session_path)
    if session_path.exists():
        shutil.rmtree(session_path)
        return True
    return False


# ANSI Color codes for terminal output
class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    @staticmethod
    def disable():
        """Disable colors (for non-terminal output)"""
        Colors.RESET = ''
        Colors.BOLD = ''
        Colors.BLACK = Colors.RED = Colors.GREEN = Colors.YELLOW = ''
        Colors.BLUE = Colors.MAGENTA = Colors.CYAN = Colors.WHITE = ''
        Colors.BG_BLACK = Colors.BG_RED = Colors.BG_GREEN = Colors.BG_YELLOW = ''
        Colors.BG_BLUE = Colors.BG_MAGENTA = Colors.BG_CYAN = Colors.BG_WHITE = ''


def colored(text, color):
    """Wrap text with color code"""
    return f"{color}{text}{Colors.RESET}"


def print_success(text):
    """Print success message in green"""
    print(colored(f"✅ {text}", Colors.GREEN))


def print_error(text):
    """Print error message in red"""
    print(colored(f"❌ {text}", Colors.RED))


def print_warning(text):
    """Print warning message in yellow"""
    print(colored(f"⚠️  {text}", Colors.YELLOW))


def print_info(text):
    """Print info message in cyan"""
    print(colored(f"ℹ️  {text}", Colors.CYAN))


def print_header(text):
    """Print header with border"""
    border = "╔" + "═" * 59 + "╗"
    bottom = "╚" + "═" * 59 + "╝"

    # Center text
    padding = (59 - len(text)) // 2
    centered = " " * padding + text + " " * (59 - padding - len(text))

    print(colored(border, Colors.CYAN))
    print(colored(f"║{centered}║", Colors.CYAN))
    print(colored(bottom, Colors.CYAN))
