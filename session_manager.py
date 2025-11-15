#!/usr/bin/env python3
"""
Session Manager for PDF Site Extractor
Handles browsing, viewing, and managing previous scan sessions
"""

import os
import sys
from pathlib import Path
from utils import (
    get_all_sessions, get_session_size_mb, delete_session,
    print_header, print_info, print_success, print_error, print_warning,
    colored, Colors, sanitize_domain
)


def display_session_list(domain=None):
    """Display list of previous sessions"""
    sessions = get_all_sessions(domain)

    if not sessions:
        print_info("No previous sessions found")
        return []

    if domain:
        print_header(f"PREVIOUS SESSIONS - {domain}")
    else:
        print_header("ALL PREVIOUS SESSIONS")

    print()

    for i, session in enumerate(sessions, 1):
        meta = session['metadata']
        session_name = session['session_name']
        domain_name = session['domain']

        # Get stats
        pdfs_found = meta.get('pdfs_found', '?')
        size_mb = meta.get('total_size_mb', get_session_size_mb(session['path']))
        depth = meta.get('depth', '?')

        # Format display
        print(f"  {colored(f'[{i}]', Colors.YELLOW)} {session_name:<20} │ "
              f"{colored(f'{pdfs_found} PDFs', Colors.GREEN)} │ "
              f"{colored(f'{size_mb:.1f} MB', Colors.CYAN)} │ "
              f"depth:{depth}")

        if not domain:  # Show domain if viewing all sessions
            print(f"      {colored(domain_name, Colors.BLUE)}")

    print()
    return sessions


def view_session_details(session):
    """Display detailed information about a session"""
    meta = session['metadata']
    session_path = Path(session['path'])
    pdfs_path = session_path / 'pdfs'

    print_header(f"SESSION: {session['session_name']}")
    print()

    # Scan details
    print(colored("📊 SCAN DETAILS:", Colors.BOLD))
    print(f"   URL:            {meta.get('url', 'N/A')}")
    print(f"   Date:           {meta.get('timestamp', 'N/A')}")
    print(f"   Depth:          {meta.get('depth', 'N/A')} levels")
    print(f"   Pages scanned:  {meta.get('pages_scanned', 'N/A')}")

    pdfs_found = meta.get('pdfs_found', 'N/A')
    pdfs_downloaded = meta.get('pdfs_downloaded', 'N/A')
    print(f"   PDFs found:     {pdfs_found}")
    print(f"   Downloaded:     {pdfs_downloaded} / {pdfs_found}", end="")

    if pdfs_found and pdfs_downloaded and pdfs_found == pdfs_downloaded:
        print(colored(" (100%)", Colors.GREEN))
    else:
        print()

    size_mb = meta.get('total_size_mb', get_session_size_mb(session['path']))
    print(f"   Total size:     {size_mb:.2f} MB")

    print()

    # Location
    print(colored("📁 LOCATION:", Colors.BOLD))
    print(f"   {session_path}")

    print()

    # Files
    print(colored("📄 FILES:", Colors.BOLD))
    if pdfs_path.exists():
        pdf_count = len(list(pdfs_path.glob('*.pdf')))
        print(f"   • pdfs/          ({pdf_count} PDF files)")
    else:
        print(colored("   • pdfs/          (directory not found)", Colors.RED))

    if (session_path / 'found_pdfs.txt').exists():
        print("   • found_pdfs.txt (URL list)")
    if (session_path / 'scan_report.txt').exists():
        print("   • scan_report.txt")
    if (session_path / 'metadata.json').exists():
        print("   • metadata.json")

    print()


def view_pdf_list(session):
    """View list of PDFs in a session"""
    session_path = Path(session['path'])
    pdf_list_file = session_path / 'found_pdfs.txt'

    if not pdf_list_file.exists():
        print_error("PDF list file not found")
        return

    print_header("PDF LIST")
    print()

    with open(pdf_list_file, 'r') as f:
        pdfs = [line.strip() for line in f if line.strip()]

    for i, pdf_url in enumerate(pdfs, 1):
        print(f"  {i}. {pdf_url}")

    print()
    print(colored(f"Total: {len(pdfs)} PDFs", Colors.BOLD))
    print()


def open_folder_in_browser(session):
    """Open session folder in file browser"""
    session_path = session['path']

    try:
        # macOS
        if sys.platform == 'darwin':
            os.system(f'open "{session_path}"')
        # Windows
        elif sys.platform == 'win32':
            os.system(f'explorer "{session_path}"')
        # Linux
        else:
            os.system(f'xdg-open "{session_path}"')

        print_success(f"Opened folder: {session_path}")
    except Exception as e:
        print_error(f"Could not open folder: {e}")


def delete_session_interactive(session):
    """Delete a session with confirmation"""
    print()
    print_warning(f"You are about to delete session: {session['session_name']}")
    print(f"   Location: {session['path']}")
    print(f"   PDFs: {session['metadata'].get('pdfs_found', '?')}")
    print()

    confirmation = input(colored("Type 'DELETE' to confirm: ", Colors.RED))

    if confirmation.strip() == 'DELETE':
        if delete_session(session['path']):
            print_success("Session deleted successfully")
            return True
        else:
            print_error("Failed to delete session")
            return False
    else:
        print_info("Deletion cancelled")
        return False


def session_detail_menu(session):
    """Interactive menu for session details"""
    while True:
        view_session_details(session)

        print(colored("Actions:", Colors.BOLD))
        print("  [o] - Open folder in file browser")
        print("  [v] - View PDF list")
        print("  [r] - Re-run with same settings")
        print("  [d] - Delete this session")
        print("  [0] - Back")
        print()

        choice = input("Enter choice: ").strip().lower()

        if choice == '0':
            break
        elif choice == 'o':
            open_folder_in_browser(session)
            input("\nPress ENTER to continue...")
        elif choice == 'v':
            view_pdf_list(session)
            input("Press ENTER to continue...")
        elif choice == 'r':
            return session['metadata']  # Return metadata to re-run
        elif choice == 'd':
            if delete_session_interactive(session):
                break  # Exit if deleted
            input("\nPress ENTER to continue...")
        else:
            print_warning("Invalid choice")

        print()

    return None


def browse_sessions_menu(domain=None):
    """Interactive menu for browsing sessions"""
    while True:
        sessions = display_session_list(domain)

        if not sessions:
            input("Press ENTER to return...")
            return None

        print(colored("Actions:", Colors.BOLD))
        print(f"  [1-{len(sessions)}] - View session details")
        print("  [d]   - Delete old sessions")
        print("  [0]   - Back")
        print()

        choice = input("Enter choice: ").strip().lower()

        if choice == '0':
            break
        elif choice == 'd':
            delete_old_sessions_menu(sessions)
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(sessions):
                result = session_detail_menu(sessions[idx])
                if result:  # If re-run was selected
                    return result
            else:
                print_warning("Invalid session number")
                input("\nPress ENTER to continue...")
        else:
            print_warning("Invalid choice")

        print()

    return None


def delete_old_sessions_menu(sessions):
    """Menu for bulk deleting old sessions"""
    print()
    print_header("DELETE OLD SESSIONS")
    print()

    print(colored("Select sessions to delete:", Colors.BOLD))
    print("  [1] - Delete sessions older than 7 days")
    print("  [2] - Delete sessions older than 30 days")
    print("  [3] - Delete all sessions")
    print("  [0] - Cancel")
    print()

    choice = input("Enter choice: ").strip()

    if choice == '0':
        return

    from datetime import datetime, timedelta

    # Filter sessions based on choice
    to_delete = []

    if choice == '1':
        cutoff = datetime.now() - timedelta(days=7)
        to_delete = [s for s in sessions if s['metadata'].get('timestamp', '') < cutoff.strftime('%Y-%m-%d')]
    elif choice == '2':
        cutoff = datetime.now() - timedelta(days=30)
        to_delete = [s for s in sessions if s['metadata'].get('timestamp', '') < cutoff.strftime('%Y-%m-%d')]
    elif choice == '3':
        to_delete = sessions
    else:
        print_warning("Invalid choice")
        return

    if not to_delete:
        print_info("No sessions match the criteria")
        input("\nPress ENTER to continue...")
        return

    print()
    print(colored(f"⚠️  About to delete {len(to_delete)} session(s)", Colors.YELLOW))
    confirmation = input(colored("Type 'DELETE' to confirm: ", Colors.RED))

    if confirmation.strip() == 'DELETE':
        deleted_count = 0
        for session in to_delete:
            if delete_session(session['path']):
                deleted_count += 1

        print_success(f"Deleted {deleted_count} session(s)")
    else:
        print_info("Deletion cancelled")

    input("\nPress ENTER to continue...")
