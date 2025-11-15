# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PDF Site Extractor is a Python-based web crawler designed to discover and download PDF files from websites. The project provides both an interactive menu system and command-line scripts:

### Interactive System
1. **menu.py** - Main interactive CLI with color-coded menus, session management, and guided workflows
2. **utils.py** - Utilities for directory management, domain sanitization, session tracking, and colored output
3. **session_manager.py** - Session browsing, viewing, and management functionality

### Command-Line Scripts
1. **pdf_crawler.py** - Full-featured crawler with BFS traversal, configurable depth, and download support
2. **simple_pdf_finder.py** - Lightweight scanner for quick discovery (no download capability)
3. **download_pdfs.py** - Standalone downloader for processing lists of PDF URLs

## Architecture

### Core Design Pattern

All scripts use **Breadth-First Search (BFS)** with a queue-based approach:
- Maintains a `visited` set to prevent re-crawling pages
- Uses `deque` for efficient queue operations
- Respects domain boundaries (only follows links within base domain and path)
- Implements polite crawling with configurable delays

### Main Components

**PDFCrawler class** (pdf_crawler.py:16-164):
- Encapsulates all crawling logic with configurable max_depth and delay
- Uses `requests.Session()` for connection pooling
- Implements three validation methods:
  - `is_valid_url()`: Ensures links stay within base domain and path
  - `is_pdf()`: Simple `.pdf` extension check
  - `get_page_links()`: Extracts and validates all links from a page
- Core BFS algorithm in `crawl()` method using (url, depth) tuples

**URL Scope Restrictions**:
- All scripts check `parsed.netloc == base_domain` to prevent external crawling
- Path validation ensures URLs start with the base path (e.g., `/fr/aide-et-support`)
- Fragment identifiers (#) are stripped from URLs

## Common Development Commands

### Installation

This project uses [UV](https://docs.astral.sh/uv/) for dependency management.

**Install UV:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Install project dependencies:**
```bash
uv sync
```

**Alternative (traditional method):**
```bash
pip install -r requirements.txt
```

### UV Workflow

UV automatically manages dependencies and creates isolated virtual environments. Key benefits:
- **Fast**: Rust-based, 10-100x faster than pip
- **Reliable**: Deterministic dependency resolution with lock files
- **Simple**: `uv run` automatically syncs dependencies before running scripts

**How it works:**
- `uv sync` creates/updates `.venv/` based on `pyproject.toml`
- `uv run` ensures dependencies are installed, then runs the command
- Dependencies are specified in `pyproject.toml` under `[project.dependencies]`
- Lock file `uv.lock` (auto-generated) ensures reproducible builds

### Running the Application

**Interactive Menu (Recommended):**
```bash
uv run python menu.py
```

This launches an interactive CLI with:
- Color-coded menus and output
- Session management and history
- Configuration settings
- Dry-run previews
- Built-in help and limitations guide

**Command-Line Scripts (Direct):**

**Quick scan (no download):**
```bash
uv run python simple_pdf_finder.py
# Outputs to: found_pdfs.txt
```

**Full crawler - list only:**
```bash
uv run python pdf_crawler.py
uv run python pdf_crawler.py https://example.com/custom-path
```

**Full crawler - with download:**
```bash
uv run python pdf_crawler.py --download
uv run python pdf_crawler.py --download --output my_pdfs --depth 5 --delay 0.5
```

**Download from existing list:**
```bash
uv run python pdf_crawler.py --save-list  # Creates pdf_list.txt
uv run python download_pdfs.py pdf_list.txt
uv run python download_pdfs.py --url "https://example.com/file.pdf"  # Single file
```

## Data Directory Structure

The interactive menu system organizes all downloads in a structured hierarchy:

```
data/
├── {sanitized_domain}/
│   └── {timestamp or custom_name}/
│       ├── pdfs/              # Downloaded PDF files
│       ├── found_pdfs.txt     # List of all PDF URLs found
│       ├── scan_report.txt    # Human-readable summary
│       └── metadata.json      # Machine-readable config and stats
```

**Key Functions:**
- `sanitize_domain(url)` - Extracts domain from URL, removes www., handles ports (utils.py:19-43)
- `create_session_directory(url, custom_name)` - Creates session structure (utils.py:51-68)
- `save_metadata()`, `save_scan_report()`, `save_pdf_list()` - Save session files (utils.py:71-116)

**Session Metadata Fields:**
- url, depth, delay, timestamp
- pages_scanned, pdfs_found, pdfs_downloaded
- total_size_mb

**Benefits:**
- Each scan is isolated (no overwrites)
- Complete history with searchable metadata
- Easy to compare scans over time
- Can delete old sessions in bulk

## Configuration Details

### Default Values
- Base URL: `https://www.heytelecom.be/fr/aide-et-support` (hardcoded in simple_pdf_finder.py:12, argument default in pdf_crawler.py:173)
- Max crawl depth: 3 levels (pdf_crawler.py:179)
- Request delay: 1.0 seconds (pdf_crawler.py:186)
- Output directory: `pdfs/` (pdf_crawler.py:196)
- User-Agent: Mozilla/5.0 string for server compatibility (pdf_crawler.py:26)

### Command-line Arguments (pdf_crawler.py)
- `url` (positional): Override base URL
- `--depth N`: Maximum BFS depth
- `--delay N`: Seconds between requests (be server-friendly)
- `--download`: Trigger PDF downloads after scan
- `--output DIR`: Download destination folder
- `--save-list`: Export PDF URLs to pdf_list.txt

## Key Implementation Notes

### Error Handling
- All HTTP requests wrapped in try/except blocks
- Timeouts set to 10s for page requests, 30s for downloads
- Graceful degradation: errors logged but don't stop crawl
- Uses `response.raise_for_status()` to catch HTTP errors

### File Naming
- Filenames extracted from URL path using `os.path.basename(urlparse(url).path)`
- Fallback naming: `document_{i}.pdf` (pdf_crawler.py:136) or `document_{hash(url)}.pdf` (download_pdfs.py:26)
- No duplicate filename handling - files may be overwritten

### Session Management
- `requests.Session()` used for connection reuse across multiple requests
- Custom User-Agent header set to avoid bot detection
- No authentication or cookie handling implemented

## Modifying Base URL

**simple_pdf_finder.py**: Edit `BASE_URL` constant at line 12

**pdf_crawler.py**: Pass as first argument or modify default at line 173

**download_pdfs.py**: Not URL-specific, operates on URL lists

## Limitations to Consider

1. **No JavaScript rendering** - PDFs loaded dynamically won't be discovered (uses BeautifulSoup, not browser automation)
2. **No authentication** - Cannot access protected content
3. **Single-threaded** - Sequential page crawling (no asyncio or multiprocessing)
4. **No retry logic** - Failed requests are logged and skipped
5. **Simple PDF detection** - Only checks `.pdf` extension, won't find PDFs with unusual URLs
6. **No duplicate file handling** - Downloads may overwrite existing files with same name
