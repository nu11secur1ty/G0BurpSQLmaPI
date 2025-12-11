#!/usr/bin/env python3
# G0BurpSQLmaPI — polished + CLI + metadata + logging + auto-detect params
# Author: nu11secur1ty (polished)
# License: GPL-3.0 (preserve your repo license)

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

sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import settings

try:
    from colorama import init, Fore, Style
    init(autoreset=True, convert=True)
except Exception:
    class _C:
        def __getattr__(self, _): return ""
    Fore = Style = _C()

import requests

# ============================
# LOGO / BANNER
# ============================
LOGO = r"""
           '| '|                         
,---..   .  |  |,---.,---.,---..   .,---.  ||--- ,   .
|   ||   |  |  |`---.|---'|    |   ||      ||    |   |
`   '`---'  `  ``---'`---'`---'`---'`      ``---'`---|
                                                 `---'
"""

BANNER = r"""
╔═══════════════════════════════════════════════════════╗
║    G0BurpSQLmaPI - polished CLI + metadata + logging  ║
║    Author: nu11secur1ty | License: GPL-3.0            ║
╚═══════════════════════════════════════════════════════╝
"""

print(Fore.CYAN + LOGO + Style.RESET_ALL)
print(Fore.MAGENTA + BANNER + Style.RESET_ALL)

# ============================
# PATHS & CONSTANTS
# ============================
ROOT = Path.cwd()
MODULES_DIR = ROOT / "modules"
EXPLOIT_PATH = ROOT / "exploit.txt"
MODULES_EXPLOIT_PATH = MODULES_DIR / "exploit.txt"
META_PATH = MODULES_DIR / "exploit_meta.json"
LOG_PATH = ROOT / "g0burpsqlmapi.log"

DEFAULT_SQLMAP_ENV = "G0_SQLMAP_PATH"
DEFAULT_SQLMAP_REL = Path("D:/CVE/sqlmap-nu11secur1ty/sqlmap.py")

# ============================
# LOGGING
# ============================
def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger("G0BurpSQLmaPI")
    logger.setLevel(level)

    fh = RotatingFileHandler(LOG_PATH, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(level)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh.setFormatter(fmt)
    if not logger.handlers:
        logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(fmt)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(ch)
    return logger

logger = setup_logging(False)

# ============================
# UTILITIES
# ============================
def ensure_modules_dir():
    MODULES_DIR.mkdir(parents=True, exist_ok=True)

def input_multiline(prompt=None):
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
# PARAM DETECTION
# ============================
def detect_params_from_payload(payload: str):
    if not payload:
        return []
    params = []
    seen = set()
    lines = payload.splitlines()
    if not lines:
        return []

    # Query string
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

    # Body heuristics
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

    # name="value" patterns
    for match in re.finditer(r'([a-zA-Z0-9_\-\.]{1,50})\s*=\s*["\']', payload):
        key = match.group(1)
        if key and key not in seen:
            params.append(key)
            seen.add(key)

    return params[:50]

# ============================
# EXPLOIT MANAGEMENT
# ============================
def create_exploit_file_interactive(logger):
    ensure_modules_dir()
    payload = input_multiline(Fore.GREEN + "Paste your full POST or GET request below (must start with POST or GET):")
    if payload is None:
        logger.info("User cancelled PoC creation.")
        print(Fore.YELLOW + "Cancelled PoC creation, returning to menu..." + Style.RESET_ALL)
        return
    if not payload.strip():
        logger.warning("Empty payload submitted.")
        print(Fore.RED + "❌ ERROR: Empty payload. Returning to menu..." + Style.RESET_ALL)
        return

    first_line = payload.strip().splitlines()[0].upper()
    if not (first_line.startswith("POST") or first_line.startswith("GET")):
        logger.warning("Payload did not start with POST/GET.")
        print(Fore.RED + "❌ ERROR: Payload must start with POST or GET. Returning to menu..." + Style.RESET_ALL)
        return

    auto = detect_params_from_payload(payload)
    if auto:
        print(Fore.CYAN + f"[Auto-detected] potential params: {auto}" + Style.RESET_ALL)
        use_auto = input(Fore.CYAN + "Use auto-detected parameters? (Y/n) " + Style.RESET_ALL).strip().lower()
        if use_auto in ("", "y", "yes"):
            vuln_params_list = auto
        else:
            vuln_params = input(Fore.CYAN + "Enter vulnerable parameter(s) (comma separated): " + Style.RESET_ALL).strip()
            vuln_params_list = [p.strip() for p in vuln_params.split(",") if p.strip()] if vuln_params else []
    else:
        vuln_params = input(Fore.CYAN + "Enter vulnerable parameter(s) (comma separated): " + Style.RESET_ALL).strip()
        vuln_params_list = [p.strip() for p in vuln_params.split(",") if p.strip()] if vuln_params else []

    header_lines = [f"# VULN_PARAMS: {','.join(vuln_params_list)}"] if vuln_params_list else []
    header_lines.append(f"# Generated by G0BurpSQLmaPI - {time.strftime('%Y-%m-%dT%H:%M:%S')}")
    header = "\n".join(header_lines) + "\n\n"

    try:
        EXPLOIT_PATH.write_text(header + payload, encoding="utf-8")
        MODULES_EXPLOIT_PATH.write_text(header + payload, encoding="utf-8")
        logger.info("exploit files written")
        print(Fore.GREEN + f"✅ PoC saved to '{EXPLOIT_PATH}' and '{MODULES_EXPLOIT_PATH}'" + Style.RESET_ALL)
    except Exception as e:
        logger.exception("Failed to write exploit files")
        print(Fore.RED + f"❌ Failed to write exploit files: {e}" + Style.RESET_ALL)
        return

    meta = {"vuln_params": vuln_params_list, "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    try:
        META_PATH.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        logger.info("metadata saved")
        print(Fore.GREEN + f"🔒 Metadata saved to '{META_PATH}'" + Style.RESET_ALL)
    except Exception as e:
        logger.warning("Failed to save metadata: %s", e)
        print(Fore.YELLOW + f"⚠️ Failed to save metadata file: {e}" + Style.RESET_ALL)

# ============================
# SQLMAP MANAGEMENT
# ============================
def find_sqlmap():
    env_path = os.getenv(DEFAULT_SQLMAP_ENV)
    if env_path:
        p = Path(env_path)
        if p.exists():
            return str(p)
    if DEFAULT_SQLMAP_REL.exists():
        return str(DEFAULT_SQLMAP_REL)
    for candidate in ("sqlmap.py", "sqlmap"):
        found = shutil.which(candidate)
        if found:
            return found
    return None

def run_sqlmap(logger):
    ensure_modules_dir()
    if not MODULES_EXPLOIT_PATH.exists():
        logger.error("exploit file missing for sqlmap")
        print(Fore.RED + f"❌ ERROR: '{MODULES_EXPLOIT_PATH}' not found. Generate PoC first." + Style.RESET_ALL)
        return

    sqlmap_path = find_sqlmap()
    if not sqlmap_path:
        logger.error("sqlmap not found")
        print(Fore.RED + f"❌ ERROR: sqlmap not found. Install or set '{DEFAULT_SQLMAP_ENV}'." + Style.RESET_ALL)
        return

    params_flag = []
    if META_PATH.exists():
        try:
            meta = json.loads(META_PATH.read_text(encoding="utf-8"))
            vuln_params = meta.get("vuln_params") or []
            if vuln_params:
                params_flag = ["-p", ",".join(vuln_params)]
                logger.info("Using vulnerable params: %s", vuln_params)
                print(Fore.GREEN + f"[+] Using vulnerable params: {vuln_params}" + Style.RESET_ALL)
        except Exception as e:
            logger.warning("Could not parse metadata: %s", e)

    cmd = [sys.executable, sqlmap_path] if sqlmap_path.endswith(".py") else [sqlmap_path]
    cmd += ["-r", str(MODULES_EXPLOIT_PATH)] + params_flag
    cmd += [
        "--tamper=space2comment",
        "--dbms=mysql",
        "--time-sec=11",
        "--random-agent",
        "--level=5",
        "--risk=3",
        "--batch",
        "--flush-session",
        "--technique=BEUSTQ",
        "--union-char=UCHAR",
        '--answers=crack=Y,dict=Y,continue=Y,quit=N',
        "--dump"
    ]

    cmd = [c for c in cmd if c]
    logger.debug("Running sqlmap command: %s", " ".join(cmd))
    print(Fore.YELLOW + "\n[+] Starting sqlmap with exploit file..." + Style.RESET_ALL)
    try:
        subprocess.run(cmd, check=False)
    except KeyboardInterrupt:
        logger.info("sqlmap interrupted by user")
        print(Fore.RED + "\nInterrupted by user." + Style.RESET_ALL)
    except Exception as e:
        logger.exception("Failed to run sqlmap: %s", e)
        print(Fore.RED + f"❌ Failed to start sqlmap: {e}" + Style.RESET_ALL)
    finally:
        print(Fore.RED + "\nHappy hunting with nu11secur1ty =)\n" + Style.RESET_ALL)

# ============================
# MODULES
# ============================
def run_module(module_filename, logger):
    ensure_modules_dir()
    module_path = MODULES_DIR / module_filename
    if not module_path.exists():
        logger.error("Module not found: %s", module_path)
        print(Fore.RED + f"❌ ERROR: Module '{module_path}' not found." + Style.RESET_ALL)
        return
    logger.info("Running module: %s", module_path)
    print(Fore.YELLOW + f"\n[+] Running module {module_path}...\n" + Style.RESET_ALL)
    try:
        subprocess.run([sys.executable, str(module_path)], check=False)
    except KeyboardInterrupt:
        logger.info("Module interrupted by user")
        print(Fore.RED + "\nInterrupted by user." + Style.RESET_ALL)
    except Exception as e:
        logger.exception("Failed to run module: %s", e)
        print(Fore.RED + f"❌ Failed to run module: {e}" + Style.RESET_ALL)
    finally:
        print(Fore.RED + "\nModule finished. Happy hunting =)\n" + Style.RESET_ALL)

# ============================
# METADATA & CLEANUP
# ============================
def view_metadata():
    if not META_PATH.exists():
        print(Fore.YELLOW + "No metadata found. Generate PoC first." + Style.RESET_ALL)
        return
    try:
        meta = json.loads(META_PATH.read_text(encoding="utf-8"))
        print(Fore.CYAN + "\n== exploit_meta.json ==" + Style.RESET_ALL)
        print(json.dumps(meta, indent=2))
    except Exception as e:
        print(Fore.RED + f"Could not read/parse metadata: {e}" + Style.RESET_ALL)

def clean_up(logger):
    deleted_any = False
    for path in (EXPLOIT_PATH, MODULES_EXPLOIT_PATH, META_PATH):
        if path.exists():
            try:
                path.unlink()
                logger.info("Deleted: %s", path)
                print(Fore.GREEN + f"🧹 Deleted: {path}" + Style.RESET_ALL)
                deleted_any = True
            except Exception as e:
                logger.exception("Error deleting %s: %s", path, e)
                print(Fore.RED + f"❌ ERROR deleting '{path}': {e}" + Style.RESET_ALL)
    try:
        if MODULES_DIR.exists() and not any(MODULES_DIR.iterdir()):
            MODULES_DIR.rmdir()
    except Exception:
        pass
    if not deleted_any:
        print(Fore.YELLOW + "⚠️ No exploit files or metadata found to delete." + Style.RESET_ALL)

# ============================
# GITHUB UPDATE CHECK
# ============================
def check_for_updates():
    print("\n[+] Checking for updates on GitHub...")
    try:
        response = requests.get(settings.GITHUB_RAW_SETTINGS, timeout=10)
        if response.status_code != 200:
            print("[!] Could not connect to GitHub.")
            return

        latest_version = None
        for line in response.text.splitlines():
            if line.startswith("VERSION"):
                latest_version = line.split("=")[1].strip().replace('"', "").replace("'", "")
                break

        print(f"[+] Installed version: {settings.VERSION}")
        print(f"[+] Latest version:    {latest_version}")

        if latest_version and latest_version != settings.VERSION:
            print("\n🔥 UPDATE AVAILABLE!")
            print(f"Run: git pull https://github.com/{settings.GITHUB_REPO}.git")
        else:
            print("✔ You are up-to-date!")

    except Exception as e:
        print("[ERROR] Update check failed:", str(e))

# ============================
# MENU
# ============================
def display_menu():
    print(Fore.CYAN + "\n===== G0BurpSQLmaPI Menu =====\n" + Style.RESET_ALL)
    print("1. Generate PoC (exploit.txt)")
    print("2. Start sqlmap with PoC")
    print("3. Run module: modules/URLi.py")
    print("4. Run module: modules/User-Agent.py")
    print("5. Run module: modules/HashCracker.py")
    print("6. View metadata (modules/exploit_meta.json)")
    print("7. Clean evidence (delete exploit.txt and metadata)")
    print("8. Check for updates")
    print("9. Exit\n")

def interactive_main(verbose=False):
    global logger
    logger = setup_logging(verbose)
    valid_choices = {str(i) for i in range(1, 10)}
    try:
        while True:
            display_menu()
            choice = input(Fore.YELLOW + "Enter your choice: " + Style.RESET_ALL).strip()
            if choice not in valid_choices:
                print(Fore.RED + "❌ Invalid choice." + Style.RESET_ALL)
                continue
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
                check_for_updates()
            elif choice == '9':
                print(Fore.GREEN + "Exiting... Happy hunting ☠️" + Style.RESET_ALL)
                break
    except KeyboardInterrupt:
        print(Fore.RED + "\nInterrupted. Exiting cleanly." + Style.RESET_ALL)
        sys.exit(0)

# ============================
# CLI
# ============================
def cli_main():
    parser = argparse.ArgumentParser(prog="G0BurpSQLmaPI", description="G0BurpSQLmaPI - polished CLI + menu")
    parser.add_argument("--create", action="store_true", help="Create PoC (interactive input)")
    parser.add_argument("--run-sqlmap", action="store_true", help="Run sqlmap using modules/exploit.txt")
    parser.add_argument("--module", type=str, help="Run a module (filename inside modules/)")
    parser.add_argument("--clean", action="store_true", help="Delete exploit files and metadata")
    parser.add_argument("--view-meta", action="store_true", help="Print metadata JSON")
    parser.add_argument("--update", action="store_true", help="Check for updates on GitHub")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    global logger
    logger = setup_logging(args.verbose)

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
    if args.update:
        check_for_updates()
        return

    interactive_main(verbose=args.verbose)

if __name__ == "__main__":
    cli_main()
