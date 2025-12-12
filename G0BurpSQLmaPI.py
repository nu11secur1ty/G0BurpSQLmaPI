#!/usr/bin/env python3
# G0BurpSQLmaPI — polished + CLI + metadata + logging + auto-detect params
# Author: nu11secur1ty (polished)
# License: GPL-3.0 (preserve your repo license)

# ============================
# STANDARD LIBRARY IMPORTS
# ============================
import os
import sys
import re
import json
import time
import shutil
import argparse
import logging
import subprocess
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ============================
# LOAD INTERNAL LIBS (lib/)
# ============================
# Add "lib" folder to Python import path
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

# Payloads
from lib.payloads import get_sqlmap_default_args, SQLMAP_PROFILES

import settings
from lib.payloads import get_sqlmap_default_args, SQLMAP_PROFILES   # <— imported cleanly at top

# ============================
# OPTIONAL COLOR SUPPORT
# ============================
try:
    from colorama import init, Fore, Style
    init(autoreset=True, convert=True)
except Exception:
    # Fail-safe dummy color class when colorama is missing
    class _C:
        def __getattr__(self, _): return ""
    Fore = Style = _C()

import requests  # (Used by modules / future features)

# ============================
# LOAD LOGO/BANNER FROM settings.py
# ============================
try:
    LOGO = settings.LOGO
except:
    LOGO = "G0BurpSQLmaPI"

try:
    BANNER = settings.BANNER
except:
    BANNER = "G0BurpSQLmaPI - default banner"

print(Fore.CYAN + LOGO + Style.RESET_ALL)
print(Fore.MAGENTA + BANNER + Style.RESET_ALL)

# ============================
# PATH CONSTANTS
# ============================
ROOT = Path.cwd()                    # Current working directory
MODULES_DIR = ROOT / "modules"       # Directory containing modules
EXPLOIT_PATH = ROOT / "exploit.txt"  # Local PoC file
MODULES_EXPLOIT_PATH = MODULES_DIR / "exploit.txt"   # Copy stored inside modules/
META_PATH = MODULES_DIR / "exploit_meta.json"         # Metadata store
LOG_PATH = ROOT / "g0burpsqlmapi.log"                 # Main log file

# Default sqlmap lookup paths
DEFAULT_SQLMAP_ENV = "G0_SQLMAP_PATH"
DEFAULT_SQLMAP_REL = Path("D:/CVE/sqlmap-nu11secur1ty/sqlmap.py")

# ============================
# LOGGING SETUP
# ============================
def setup_logging(verbose: bool = False):
    """
    Initialize logger with file + console handler.
    Uses rotating logs and supports verbose mode.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger("G0BurpSQLmaPI")
    logger.setLevel(level)

    # File logging with rotation
    fh = RotatingFileHandler(LOG_PATH, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(level)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh.setFormatter(fmt)
    if not logger.handlers:
        logger.addHandler(fh)

    # Console logging
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(fmt)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(ch)

    return logger

logger = setup_logging(False)

# ============================
# UTILITY FUNCTIONS
# ============================
def ensure_modules_dir():
    """Ensure that modules/ directory exists."""
    MODULES_DIR.mkdir(parents=True, exist_ok=True)

def input_multiline(prompt=None):
    """
    Accept multi-line user input.
    Ends when user enters '.' or 'exit'.
    """
    if prompt:
        print(prompt)
    print("(Enter a single dot '.' on its own line to finish, or type 'exit' to cancel.)")
    lines = []
    try:
        while True:
            line = input()
            if line.lower().strip() == "exit":
                return None
            if line.strip() == ".":
                break
            lines.append(line)
    except KeyboardInterrupt:
        print(Fore.RED + "\nInterrupted during input. Cancelled." + Style.RESET_ALL)
        return None
    return "\n".join(lines).rstrip("\n")

# ============================
# AUTO PARAMETER EXTRACTION
# ============================
def detect_params_from_payload(payload: str):
    """
    Analyze a raw HTTP request and extract possible parameter names.
    Supports:
      - Query-string extraction
      - POST body extraction
      - name="value" style extraction
    """
    if not payload:
        return []

    params = []
    seen = set()
    lines = payload.splitlines()
    if not lines:
        return []

    # Extract parameters from query string
    first = lines[0]
    m = re.search(r'^[A-Z]+\s+[^?\s]+\?([^ \t]+)', first)
    if m:
        query = m.group(1).split()[0]
        for pair in query.split('&'):
            if '=' in pair:
                key = pair.split('=', 1)[0].strip()
                if key and key not in seen:
                    params.append(key)
                    seen.add(key)

    # Extract POST body
    try:
        blank_idx = lines.index('')
        body = "\n".join(lines[blank_idx+1:]).strip()
    except ValueError:
        body = lines[-1].strip()

    for pair in re.split(r'[&\r\n]+', body):
        if '=' in pair:
            key = pair.split('=', 1)[0].strip()
            if key and key not in seen:
                params.append(key)
                seen.add(key)

    # Extract name="value" patterns
    for match in re.finditer(r'([a-zA-Z0-9_\-\.]{1,50})\s*=\s*["\']', payload):
        key = match.group(1)
        if key and key not in seen:
            params.append(key)
            seen.add(key)

    return params[:50]

# ============================
# CREATE/STORE EXPLOIT (PoC)
# ============================
def create_exploit_file_interactive(logger):
    """
    Create exploit.txt interactively.
    Auto-detect parameters.
    Save exploit + JSON metadata.
    """
    ensure_modules_dir()

    payload = input_multiline(Fore.GREEN + "Paste your full POST or GET request below:")
    if payload is None:
        logger.info("User cancelled PoC creation.")
        print(Fore.YELLOW + "Cancelled PoC creation, returning to menu..." + Style.RESET_ALL)
        return
    if not payload.strip():
        logger.warning("Empty payload submitted.")
        print(Fore.RED + "❌ ERROR: Empty payload." + Style.RESET_ALL)
        return

    # Minimal verification of request type
    first_line = payload.strip().splitlines()[0].upper()
    if not (first_line.startswith("POST") or first_line.startswith("GET")):
        print(Fore.RED + "❌ ERROR: Payload must start with POST or GET." + Style.RESET_ALL)
        return

    # Auto-detect vulnerable parameters
    auto = detect_params_from_payload(payload)
    if auto:
        print(Fore.CYAN + f"[Auto-detected] potential params: {auto}" + Style.RESET_ALL)
        use_auto = input(Fore.CYAN + "Use auto-detected parameters? (Y/n) ").strip().lower()
        if use_auto in ("", "y", "yes"):
            vuln_params_list = auto
        else:
            vuln_params = input(Fore.CYAN + "Enter vulnerable parameter(s): ").strip()
            vuln_params_list = [p.strip() for p in vuln_params.split(",") if p.strip()]
    else:
        vuln_params = input(Fore.CYAN + "Enter vulnerable parameter(s): ").strip()
        vuln_params_list = [p.strip() for p in vuln_params.split(",") if p.strip()]

    # Header for PoC file
    header_lines = [f"# VULN_PARAMS: {','.join(vuln_params_list)}"] if vuln_params_list else []
    header_lines.append(f"# Generated by G0BurpSQLmaPI - {time.strftime('%Y-%m-%dT%H:%M:%S')}")
    header = "\n".join(header_lines) + "\n\n"

    # Write PoC to both root and modules/
    try:
        EXPLOIT_PATH.write_text(header + payload, encoding="utf-8")
        MODULES_EXPLOIT_PATH.write_text(header + payload, encoding="utf-8")
        logger.info("exploit files written")
        print(Fore.GREEN + "✅ PoC saved." + Style.RESET_ALL)
    except Exception as e:
        logger.exception("Failed to write exploit files")
        print(Fore.RED + f"❌ Failed: {e}" + Style.RESET_ALL)
        return

    # Save metadata
    meta = {"vuln_params": vuln_params_list, "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    META_PATH.write_text(json.dumps(meta, indent=2), encoding="utf-8")

# ============================
# SQLMAP WRAPPER
# ============================
def find_sqlmap():
    """
    Auto-detect sqlmap.py from:
      1. Environment variable
      2. Default hardcoded path
      3. PATH search (sqlmap.py or sqlmap binary)
    """
    env_path = os.getenv(DEFAULT_SQLMAP_ENV)
    if env_path and Path(env_path).exists():
        return env_path

    if DEFAULT_SQLMAP_REL.exists():
        return str(DEFAULT_SQLMAP_REL)

    found = shutil.which("sqlmap.py") or shutil.which("sqlmap")
    return found

def run_sqlmap(logger):
    """
    Construct and execute sqlmap command using:
      - exploit.txt
      - auto-detected vulnerable parameters
      - interactive selection of payload/profile from lib/payloads.py
    """
    ensure_modules_dir()

    # Check exploit presence
    if not MODULES_EXPLOIT_PATH.exists():
        print(Fore.RED + "❌ ERROR: exploit not found." + Style.RESET_ALL)
        return

    # Resolve sqlmap path
    sqlmap_path = find_sqlmap()
    if not sqlmap_path:
        print(Fore.RED + "❌ ERROR: sqlmap not found." + Style.RESET_ALL)
        return

    # Load vulnerable parameters from metadata
    params_flag = []
    if META_PATH.exists():
        meta = json.loads(META_PATH.read_text(encoding="utf-8"))
        vuln_params = meta.get("vuln_params") or []
        if vuln_params:
            params_flag = ["-p", ",".join(vuln_params)]
            print(Fore.GREEN + f"[+] Using vulnerable params: {vuln_params}" + Style.RESET_ALL)

    # ===== INTERACTIVE PROFILE SELECTION =====
    if SQLMAP_PROFILES:
        print(Fore.CYAN + "[*] Available SQLmap profiles:" + Style.RESET_ALL)
        for idx, profile_name in enumerate(SQLMAP_PROFILES.keys(), 1):
            print(f"{idx}. {profile_name}")
        choice = input(Fore.CYAN + "Select profile number (default 1): " + Style.RESET_ALL).strip()
        try:
            choice_idx = int(choice) - 1 if choice else 0
            profile_name = list(SQLMAP_PROFILES.keys())[choice_idx]
        except (ValueError, IndexError):
            profile_name = list(SQLMAP_PROFILES.keys())[0]
        print(Fore.GREEN + f"[+] Selected profile: {profile_name}" + Style.RESET_ALL)
    else:
        profile_name = None
    # =======================================

    # Build sqlmap command base
    cmd = [sys.executable, sqlmap_path] if sqlmap_path.endswith(".py") else [sqlmap_path]

    # Append default SQLmap arguments for the selected profile
    cmd += get_sqlmap_default_args(MODULES_EXPLOIT_PATH, params_flag, profile=profile_name)

    print(Fore.YELLOW + "\n[+] Starting sqlmap..." + Style.RESET_ALL)

    try:
        subprocess.run(cmd, check=False)
    except KeyboardInterrupt:
        print(Fore.RED + "\nInterrupted." + Style.RESET_ALL)
    finally:
        print(Fore.RED + "\nHappy hunting =)\n" + Style.RESET_ALL)

# ============================
# MODULES SYSTEM (URLi, HashCracker, etc.)
# ============================
def run_module(module_filename, logger):
    """
    Execute a python module stored inside modules/.
    Example: URLi.py, User-Agent.py, HashCracker.py
    """
    ensure_modules_dir()
    module_path = MODULES_DIR / module_filename
    if not module_path.exists():
        print(Fore.RED + f"❌ Module not found: {module_path}" + Style.RESET_ALL)
        return

    print(Fore.YELLOW + f"\n[+] Running module {module_path}...\n" + Style.RESET_ALL)
    try:
        subprocess.run([sys.executable, str(module_path)], check=False)
    except KeyboardInterrupt:
        print(Fore.RED + "\nInterrupted." + Style.RESET_ALL)
    finally:
        print(Fore.RED + "\nModule finished.\n" + Style.RESET_ALL)

# ============================
# VIEW & CLEAN METADATA / FILES
# ============================
def view_metadata():
    """Display exploit metadata JSON."""
    if not META_PATH.exists():
        print(Fore.YELLOW + "No metadata found." + Style.RESET_ALL)
        return
    print(json.dumps(json.loads(META_PATH.read_text(encoding="utf-8")), indent=2))

def clean_up(logger):
    """
    Delete exploit.txt and metadata files from both root and modules/.
    """
    deleted_any = False
    for path in (EXPLOIT_PATH, MODULES_EXPLOIT_PATH, META_PATH):
        if path.exists():
            path.unlink()
            print(Fore.GREEN + f"🧹 Deleted: {path}" + Style.RESET_ALL)
            deleted_any = True

    if not deleted_any:
        print(Fore.YELLOW + "⚠️ No files to delete." + Style.RESET_ALL)

# ============================
# MENU UI (Interactive mode)
# ============================
def display_menu():
    """Print the interactive menu."""
    print(Fore.CYAN + "\n===== G0BurpSQLmaPI Menu =====\n" + Style.RESET_ALL)
    print("1. Generate PoC (exploit.txt)")
    print("2. Start sqlmap with PoC")
    print("3. Run module: modules/URLi.py")
    print("4. Run module: modules/User-Agent.py")
    print("5. Run module: modules/HashCracker.py")
    print("6. View metadata")
    print("7. Clean evidence")
    print("8. Exit\n")

def interactive_main(verbose=False):
    """
    Main interactive menu loop.
    Handles each option and dispatches to appropriate functions.
    """
    global logger
    logger = setup_logging(verbose)

    try:
        while True:
            display_menu()
            choice = input("Enter your choice: ").strip()

            if choice == '1':
                create_exploit_file_interactive(logger)
            elif choice == '2':
                run_sqlmap(logger)
            elif choice == '3':
                run_module("URLi.py", logger)
            elif choice == '4':
                run_module("User-Agent.py", logger)
            elif choice == '5':
                run_module("HashCracker.py", logger)
            elif choice == '6':
                view_metadata()
            elif choice == '7':
                clean_up(logger)
            elif choice == '8':
                print(Fore.GREEN + "Exiting... Happy hunting ☠️" + Style.RESET_ALL)
                break
            else:
                print(Fore.RED + "❌ Invalid choice." + Style.RESET_ALL)

    except KeyboardInterrupt:
        print(Fore.RED + "\nInterrupted. Exiting." + Style.RESET_ALL)
        sys.exit(0)

# ============================
# CLI FLAGS ENTRYPOINT
# ============================
def cli_main():
    """
    Command-line interface support.
    Allows calling functions without interactive menu.
    """
    parser = argparse.ArgumentParser(
        prog="G0BurpSQLmaPI",
        description="G0BurpSQLmaPI - polished CLI"
    )

    parser.add_argument("--create", action="store_true", help="Create PoC")
    parser.add_argument("--run-sqlmap", action="store_true", help="Run sqlmap with exploit")
    parser.add_argument("--module", type=str, help="Run a module inside modules/")
    parser.add_argument("--clean", action="store_true", help="Delete exploit & metadata")
    parser.add_argument("--view-meta", action="store_true", help="View metadata")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    global logger
    logger = setup_logging(args.verbose)

    # Direct CLI actions
    if args.create:
        create_exploit_file_interactive(logger)
        return

    if args.run_sqlmap:
        run_sqlmap(logger)
        return

    if args.module:
        run_module(args.module, logger)
        return

    if args.clean:
        clean_up(logger)
        return

    if args.view_meta:
        view_metadata()
        return

    # Default to interactive mode
    interactive_main(verbose=args.verbose)

# ============================
# EXECUTION ENTRYPOINT
# ============================
if __name__ == "__main__":
    cli_main()
