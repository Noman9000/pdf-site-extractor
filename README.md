# PDF Site Extractor

A powerful Python tool to crawl websites, discover, and download PDF files with an interactive command-line interface.

## Features

✨ **Interactive Menu System** - User-friendly CLI with color-coded output
📁 **Organized Storage** - Automatic session management with timestamped directories
🔍 **Smart Crawling** - BFS-based web crawler with configurable depth
📊 **Session History** - Browse, review, and manage previous scans
⚡ **Fast & Reliable** - Built with UV for lightning-fast dependency management
🎨 **Visual Feedback** - Clear progress indicators and summary reports

## Installation

This project uses [UV](https://docs.astral.sh/uv/) for fast, reliable dependency management.

### Install UV (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install dependencies
```bash
uv sync
```

Or using the traditional method:
```bash
pip install -r requirements.txt
```

## Quick Start

### Interactive Menu (Recommended)

Launch the interactive menu for a guided experience:

```bash
uv run python menu.py
```

The interactive menu provides:
- 📋 Easy-to-use options for scanning and downloading
- ⚙️ Visual configuration settings
- 📊 Session browsing and management
- 💡 Built-in help and limitations guide
- 🎨 Color-coded output for better readability

### Command Line Interface (Advanced)

For direct command-line usage:

#### 1. Just count and list PDFs (no download)
```bash
uv run python pdf_crawler.py
```

#### 2. Save the list of PDF URLs to a file
```bash
uv run python pdf_crawler.py --save-list
```

#### 3. Download all PDFs
```bash
uv run python pdf_crawler.py --download
```

#### 4. Custom settings
```bash
uv run python pdf_crawler.py --depth 4 --delay 0.5 --download --output my_pdfs
```

## Command-line Options

- `url` - Base URL to crawl (default: Hey Telecom support page)
- `--depth N` - Maximum crawl depth (default: 3)
- `--delay N` - Delay between requests in seconds (default: 1.0)
- `--download` - Download all found PDFs
- `--output DIR` - Output directory for downloads (default: 'pdfs')
- `--save-list` - Save PDF URLs to pdf_list.txt

## Examples

```bash
# Scan with deeper crawl
uv run python pdf_crawler.py --depth 5

# Scan and download to specific folder
uv run python pdf_crawler.py --download --output hey_telecom_pdfs

# Scan different URL
uv run python pdf_crawler.py https://example.com/support --depth 2

# Fast scan (less polite to server)
uv run python pdf_crawler.py --delay 0.2 --save-list
```

## Data Organization

Scans are automatically organized in a clean directory structure:

```
data/
├── heytelecom.be/
│   ├── 2025-11-15_14-45-23/
│   │   ├── pdfs/                  # Downloaded PDF files
│   │   ├── found_pdfs.txt         # List of PDF URLs
│   │   ├── scan_report.txt        # Human-readable summary
│   │   └── metadata.json          # Scan configuration & stats
│   └── 2025-11-15_16-30-11/
│       └── ...
└── example.com/
    └── ...
```

Benefits:
- Each scan is isolated with a timestamp
- No file overwrites between scans
- Easy to compare results over time
- Complete session history with metadata

## How it Works

1. **Crawling**: Uses BFS (breadth-first search) to explore pages
2. **PDF Detection**: Identifies links ending in `.pdf`
3. **Scope**: Only follows links within the same domain and base path
4. **Polite**: Adds delay between requests to avoid overloading servers
5. **Session Management**: Automatically organizes downloads by domain and timestamp

## Output

The script will:
- Show progress as it crawls each page
- Display each PDF found in real-time
- Print summary statistics
- Optionally save a list of all PDF URLs
- Optionally download all PDFs to a folder

## Notes

- Respects the base path (won't crawl outside /fr/aide-et-support)
- Skips already visited URLs to avoid loops
- Handles errors gracefully
- Shows file sizes when downloading
