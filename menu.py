#!/usr/bin/env python3
"""
Interactive Menu for PDF Site Extractor
Main entry point for the interactive CLI interface
"""

import sys
import os
from pathlib import Path
from utils import (
    print_header, print_info, print_success, print_error, print_warning,
    colored, Colors, sanitize_domain, create_session_directory,
    save_metadata, save_scan_report, save_pdf_list, get_all_sessions
)
from session_manager import browse_sessions_menu


class AppConfig:
    """Application configuration state"""
    def __init__(self):
        self.url = "https://www.heytelecom.be/fr/aide-et-support"
        self.depth = 3
        self.delay = 1.0
        self.output = "data"
        self.custom_session_name = None
        self.last_run = None

    def display(self):
        """Display current settings"""
        print(colored("Current Settings:", Colors.BOLD))
        print(f"  • URL: {colored(self.url, Colors.CYAN)}")
        print(f"  • Max Depth: {colored(str(self.depth), Colors.GREEN)} levels")
        print(f"  • Delay: {colored(f'{self.delay}s', Colors.GREEN)} between requests")
        domain = sanitize_domain(self.url)
        print(f"  • Output: {colored(f'data/{domain}/', Colors.CYAN)}")
        print()


config = AppConfig()


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def show_main_menu():
    """Display main menu"""
    clear_screen()
    print_header("PDF SITE EXTRACTOR - INTERACTIVE MENU")
    print()

    # Show last run if available
    if config.last_run:
        last_domain = sanitize_domain(config.last_run['url'])
        last_pdfs = config.last_run.get('pdfs_found', '?')
        print(colored(f"💡 LAST RUN: ", Colors.YELLOW) +
              f"Scan from {last_domain} ({last_pdfs} PDFs found)")
        print(colored("   Press [R] to repeat with same settings", Colors.YELLOW))
        print()

    print(colored("📋 MAIN OPTIONS:", Colors.BOLD))
    print(f"  {colored('[1]', Colors.YELLOW)} Quick Scan (Fast, no download)          "
          f"{colored('💡 Shortcut: q', Colors.CYAN)}")
    print(f"  {colored('[2]', Colors.YELLOW)} Full Scan & List PDFs                   "
          f"{colored('💡 Shortcut: s', Colors.CYAN)}")
    print(f"  {colored('[3]', Colors.YELLOW)} Full Scan & Download PDFs               "
          f"{colored('💡 Shortcut: d', Colors.CYAN)}")
    print(f"  {colored('[4]', Colors.YELLOW)} Download from existing PDF list         "
          f"{colored('💡 Shortcut: l', Colors.CYAN)}")
    print(f"  {colored('[5]', Colors.YELLOW)} Browse Previous Sessions                "
          f"{colored('💡 Shortcut: b', Colors.CYAN)}")
    print(f"  {colored('[6]', Colors.YELLOW)} Configure Settings                      "
          f"{colored('💡 Shortcut: c', Colors.CYAN)}")
    print(f"  {colored('[7]', Colors.YELLOW)} View Limitations & Help                 "
          f"{colored('💡 Shortcut: h', Colors.CYAN)}")
    print(f"  {colored('[0]', Colors.YELLOW)} Exit                                    "
          f"{colored('💡 Shortcut: x', Colors.CYAN)}")
    print()

    config.display()


def configure_menu():
    """Configuration submenu"""
    while True:
        clear_screen()
        print_header("CONFIGURATION SETTINGS")
        print()

        print(f"{colored('[1]', Colors.YELLOW)} Change Target URL")
        print(f"    Current: {colored(config.url, Colors.CYAN)}")
        print()

        print(f"{colored('[2]', Colors.YELLOW)} Set Crawl Depth (1-10)")
        print(f"    Current: {colored(str(config.depth), Colors.GREEN)} levels")
        print_info("Higher = more pages scanned, slower")
        print()

        print(f"{colored('[3]', Colors.YELLOW)} Set Request Delay (0.1-5.0 seconds)")
        print(f"    Current: {colored(f'{config.delay}s', Colors.GREEN)}")
        print_warning("Lower = faster but less server-friendly")
        print()

        print(f"{colored('[4]', Colors.YELLOW)} Set Custom Session Name")
        print(f"    Current: {colored(config.custom_session_name or 'Auto-generate', Colors.CYAN)}")
        print()

        print(f"{colored('[5]', Colors.YELLOW)} Reset to Defaults")
        print()

        print(f"{colored('[0]', Colors.YELLOW)} Back to Main Menu")
        print()

        choice = input("Enter choice: ").strip()

        if choice == '0':
            break
        elif choice == '1':
            new_url = input(f"\nEnter new URL (or press ENTER to keep current):\n{colored('> ', Colors.CYAN)}").strip()
            if new_url:
                config.url = new_url
                print_success(f"URL updated to: {new_url}")
            input("\nPress ENTER to continue...")

        elif choice == '2':
            try:
                depth = input(f"\nEnter crawl depth (1-10): {colored('', Colors.CYAN)}").strip()
                depth = int(depth)
                if 1 <= depth <= 10:
                    config.depth = depth
                    print_success(f"Depth set to: {depth}")
                else:
                    print_error("Depth must be between 1 and 10")
            except ValueError:
                print_error("Invalid number")
            input("\nPress ENTER to continue...")

        elif choice == '3':
            try:
                delay = input(f"\nEnter request delay (0.1-5.0): {colored('', Colors.CYAN)}").strip()
                delay = float(delay)
                if 0.1 <= delay <= 5.0:
                    config.delay = delay
                    print_success(f"Delay set to: {delay}s")
                else:
                    print_error("Delay must be between 0.1 and 5.0")
            except ValueError:
                print_error("Invalid number")
            input("\nPress ENTER to continue...")

        elif choice == '4':
            name = input(f"\nEnter custom session name (or press ENTER for auto-generate):\n{colored('> ', Colors.CYAN)}").strip()
            if name:
                config.custom_session_name = name
                print_success(f"Session name set to: {name}")
            else:
                config.custom_session_name = None
                print_success("Session name will be auto-generated")
            input("\nPress ENTER to continue...")

        elif choice == '5':
            config.url = "https://www.heytelecom.be/fr/aide-et-support"
            config.depth = 3
            config.delay = 1.0
            config.custom_session_name = None
            print_success("Settings reset to defaults")
            input("\nPress ENTER to continue...")

        else:
            print_warning("Invalid choice")
            input("\nPress ENTER to continue...")


def show_limitations():
    """Display limitations and help"""
    clear_screen()
    print_header("LIMITATIONS & TROUBLESHOOTING")
    print()

    print(colored("⚠️  KNOWN LIMITATIONS:", Colors.RED + Colors.BOLD))
    print()

    print(colored("  1. No JavaScript Support", Colors.YELLOW))
    print("     • Only finds PDFs in HTML source code")
    print("     • Dynamically loaded PDFs won't be detected")
    print("     • Solution: Try increasing crawl depth")
    print()

    print(colored("  2. No Authentication", Colors.YELLOW))
    print("     • Cannot access password-protected pages")
    print("     • Cannot handle login sessions")
    print()

    print(colored("  3. Same-Domain Only", Colors.YELLOW))
    print("     • Only follows links within the base domain")
    print("     • Only scans pages under the starting path")
    print("     • Example: Won't leave /fr/aide-et-support")
    print()

    print(colored("  4. Simple PDF Detection", Colors.YELLOW))
    print("     • Only detects files ending in .pdf")
    print("     • May miss PDFs with unusual URLs")
    print()

    print(colored("  5. File Name Conflicts", Colors.YELLOW))
    print("     • Duplicate names will be overwritten")
    print("     • No automatic rename on collision")
    print()

    print(colored("💡 TIPS:", Colors.GREEN + Colors.BOLD))
    print()
    print("  • Start with depth 2-3, increase if needed")
    print("  • Use 1.0s delay to be server-friendly")
    print("  • Check found_pdfs.txt before downloading")
    print("  • Increase depth if expected PDFs are missing")
    print()

    print(colored("❓ TROUBLESHOOTING:", Colors.CYAN + Colors.BOLD))
    print()
    print(colored('  "No PDFs found"', Colors.YELLOW))
    print("    → PDFs may be JavaScript-loaded")
    print("    → Try increasing depth")
    print("    → Check if authentication is required")
    print()

    print(colored('  "Connection errors"', Colors.YELLOW))
    print("    → Check internet connection")
    print("    → Try increasing delay")
    print("    → Corporate networks may block scraping")
    print()

    input("Press ENTER to return to main menu...")


def show_dry_run_preview(mode):
    """Show dry-run preview before execution"""
    clear_screen()
    print_header("READY TO EXECUTE")
    print()

    print(colored("📋 WHAT WILL HAPPEN:", Colors.BOLD))
    print(f"   {colored('✓', Colors.GREEN)} Scan: {config.url}")
    print(f"   {colored('✓', Colors.GREEN)} Max depth: {config.depth} levels")

    # Estimate pages based on depth (rough estimate)
    estimated_pages = 5 * (3 ** config.depth)
    print(f"   {colored('✓', Colors.GREEN)} Estimated pages: ~{min(estimated_pages, 100)} "
          f"(based on depth)")

    domain = sanitize_domain(config.url)
    session_name = config.custom_session_name or "[auto-generated timestamp]"
    print(f"   {colored('✓', Colors.GREEN)} Save to: data/{domain}/{session_name}/")

    if mode in ['download', 'full']:
        print(f"   {colored('✓', Colors.GREEN)} Download PDFs: Yes")
    else:
        print(f"   {colored('✓', Colors.GREEN)} Download PDFs: No (list only)")

    print(f"   {colored('✓', Colors.GREEN)} Delay: {config.delay}s per request")
    print()

    # Time estimate
    estimated_time = estimated_pages * config.delay
    if estimated_time < 60:
        time_str = f"{int(estimated_time)}s"
    else:
        time_str = f"{int(estimated_time / 60)}min"

    print(colored(f"⏱️  Estimated time: {time_str} - {time_str * 2} (depends on page count)", Colors.CYAN))
    print()

    if mode in ['download', 'full']:
        print_warning("WARNING: Existing files in target directory may be overwritten")
        print()

    print("Proceed?")
    print(f"  {colored('[Y]', Colors.GREEN)} - Start")
    print(f"  {colored('[n]', Colors.RED)} - Cancel")
    print()

    choice = input("Enter choice [Y/n]: ").strip().lower()

    return choice != 'n'


def run_crawler(download=False, mode='quick'):
    """Run the PDF crawler"""
    if not show_dry_run_preview(mode):
        print_info("Operation cancelled")
        input("\nPress ENTER to continue...")
        return

    # Import here to avoid circular dependencies
    from pdf_crawler import PDFCrawler
    from datetime import datetime

    try:
        # Create session directory
        session_path, pdfs_path = create_session_directory(config.url, config.custom_session_name)

        print()
        print_header("SCAN IN PROGRESS")
        print()

        # Create and run crawler
        crawler = PDFCrawler(config.url, max_depth=config.depth, delay=config.delay)
        crawler.crawl()

        # Save PDF list
        save_pdf_list(session_path, crawler.pdf_urls)

        # Prepare metadata
        metadata = {
            'url': config.url,
            'depth': config.depth,
            'delay': config.delay,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'pages_scanned': len(crawler.visited_urls),
            'pdfs_found': len(crawler.pdf_urls),
            'pdfs_downloaded': 0,
            'total_size_mb': 0.0
        }

        # Download if requested
        if download and crawler.pdf_urls:
            print()
            crawler.download_pdfs(pdfs_path)

            # Calculate total size
            from pathlib import Path
            total_size = sum(f.stat().st_size for f in Path(pdfs_path).glob('*.pdf'))
            metadata['total_size_mb'] = total_size / (1024 * 1024)
            metadata['pdfs_downloaded'] = len(list(Path(pdfs_path).glob('*.pdf')))

        # Save metadata and report
        save_metadata(session_path, metadata)
        save_scan_report(session_path, metadata, crawler.pdf_urls)

        # Store as last run
        config.last_run = metadata

        # Display summary
        print()
        print_header("SCAN COMPLETE")
        print()

        print("┌─────────────────────────────────────────────────────────┐")
        print("│ PDF EXTRACTION REPORT                                   │")
        print("│ ─────────────────────────────────────────────────────── │")
        print(f"│ URL:          {config.url[:40]:<40} │")
        print(f"│ Date:         {metadata['timestamp']:<40} │")
        print(f"│ Pages Scanned: {metadata['pages_scanned']:<39} │")
        print(f"│ PDFs Found:    {metadata['pdfs_found']:<39} │")

        if download:
            print(f"│ Downloaded:    {metadata['pdfs_downloaded']} / {metadata['pdfs_found']}"
                  f" ({100 if metadata['pdfs_found'] == metadata['pdfs_downloaded'] else 0}%)"
                  f"{'':<27} │")
            print(f"│ Total Size:    {metadata['total_size_mb']:.2f} MB{'':<30} │")

        print(f"│ Location:      {session_path[:40]:<40} │")
        print(f"│ List Saved:    found_pdfs.txt{'':<27} │")
        print("└─────────────────────────────────────────────────────────┘")
        print()

        print_success("Scan complete!")
        print_info("Tip: Copy this report for your records")
        print()

        print(f"Press {colored('[ENTER]', Colors.CYAN)} to continue, "
              f"{colored('[v]', Colors.YELLOW)} to view PDF list: ", end='')

        choice = input().strip().lower()

        if choice == 'v':
            print()
            crawler.list_pdfs()
            input("\nPress ENTER to continue...")

    except Exception as e:
        print_error(f"Error during scan: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress ENTER to continue...")


def main():
    """Main menu loop"""
    while True:
        show_main_menu()

        choice = input("Enter choice [0-7] or shortcut: ").strip().lower()

        # Map shortcuts
        shortcut_map = {
            'q': '1', 's': '2', 'd': '3', 'l': '4',
            'b': '5', 'c': '6', 'h': '7', 'x': '0',
            'r': 'repeat'
        }
        choice = shortcut_map.get(choice, choice)

        if choice == '0':
            print()
            print_success("Thank you for using PDF Site Extractor!")
            sys.exit(0)

        elif choice == '1':  # Quick scan
            run_crawler(download=False, mode='quick')

        elif choice == '2':  # Full scan & list
            run_crawler(download=False, mode='full')

        elif choice == '3':  # Full scan & download
            run_crawler(download=True, mode='download')

        elif choice == '4':  # Download from list
            print_info("Feature coming soon: Download from existing list")
            input("\nPress ENTER to continue...")

        elif choice == '5':  # Browse sessions
            result = browse_sessions_menu()
            if result:  # If user chose to re-run
                config.url = result.get('url', config.url)
                config.depth = result.get('depth', config.depth)
                config.delay = result.get('delay', config.delay)
                print_success("Settings loaded from previous session")
                input("\nPress ENTER to continue...")

        elif choice == '6':  # Configure
            configure_menu()

        elif choice == '7':  # Help
            show_limitations()

        elif choice == 'repeat' and config.last_run:
            # Repeat last run with same settings
            run_crawler(download=True, mode='download')

        else:
            print_warning("Invalid choice")
            input("\nPress ENTER to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_info("Operation cancelled by user")
        sys.exit(0)
