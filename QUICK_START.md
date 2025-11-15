# Quick Start Guide

## The Easiest Way to Extract PDFs

### Interactive Menu (Recommended)

**1. Install UV (if not already installed)**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. Install dependencies**
```bash
uv sync
```

**3. Launch the interactive menu**
```bash
uv run python menu.py
```

**What you get:**
- 🎨 Beautiful color-coded interface
- 📋 Easy step-by-step guidance
- ⚙️ Visual configuration options
- 📊 Browse previous scans
- 💡 Built-in help and tips
- ✅ Progress indicators and summaries

### Alternative: Command-Line Scripts

**Option 1: Simple Script (Quick check)**
```bash
uv run python simple_pdf_finder.py
```
- Scans and lists PDFs
- Saves to `found_pdfs.txt`
- No download

**Option 2: Full-Featured Crawler**
```bash
# Just scan and count
uv run python pdf_crawler.py

# Scan and download all PDFs
uv run python pdf_crawler.py --download

# Scan deeper with more pages
uv run python pdf_crawler.py --depth 5 --download
```

## What You'll Get

### With Interactive Menu:
- **Organized storage**: PDFs saved in `data/domain-name/timestamp/pdfs/`
- **Complete history**: Each scan is isolated with its own directory
- **Detailed reports**: Both human-readable (`scan_report.txt`) and machine-readable (`metadata.json`)
- **Session browsing**: Review previous scans anytime
- **No overwrites**: Each scan gets its own timestamp

### With Command-Line Scripts:
1. **How many PDFs exist** on the site
2. **The URLs** of all PDFs found
3. **Which pages** were scanned
4. **Downloaded PDFs** (if using `--download`)

## Customization

To scan a different part of the site, edit the URL:

**Simple script**: Edit `BASE_URL` at the top of `simple_pdf_finder.py`

**Full script**: Pass URL as argument:
```bash
uv run python pdf_crawler.py https://www.heytelecom.be/fr/autre-page
```

## Tips

- Start with depth 2-3 (default is 3)
- Use `--delay 0.5` for faster scanning (be polite to servers!)
- The script only scans pages under the base URL path
- It won't follow external links or go to unrelated sections

## Troubleshooting

**"No PDFs found"**: 
- The PDFs might be loaded dynamically with JavaScript
- Try increasing `--depth` to scan more pages
- Check if the site requires authentication

**"Connection error"**:
- Check your internet connection
- Some corporate networks block web scraping
- Try adding a longer `--delay`
