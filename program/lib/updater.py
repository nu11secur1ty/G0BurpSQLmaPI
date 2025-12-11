# ============================================================
#  updater.py — SAFE GITHUB VERSION CHECKER
# ============================================================

import requests
from packaging import version
from lib.settings import VERSION, GITHUB_RAW_SETTINGS

def check_for_update():
    """
    Safe update checker.
    - Reads remote settings.py
    - Extracts VERSION string
    - Compares with local VERSION
    Does NOT download or execute anything.
    """
    print("[i] Checking for updates...")

    try:
        response = requests.get(GITHUB_RAW_SETTINGS, timeout=5)

        if response.status_code != 200:
            print("[!] GitHub returned an error.")
            return

        remote_ver = None
        for line in response.text.splitlines():
            if line.startswith("VERSION"):
                remote_ver = line.split("=")[1].strip().strip('"')
                break

        if not remote_ver:
            print("[!] Could not detect remote version.")
            return

        if version.parse(remote_ver) > version.parse(VERSION):
            print(f"[+] New version available: {remote_ver}")
            print("[!] Please update manually from GitHub.")
        else:
            print(f"[✓] You are up to date ({VERSION}).")

    except Exception as e:
        print(f"[!] Update check failed: {e}")
