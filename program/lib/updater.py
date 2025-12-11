import requests
import sys
import os

# Local version (import your settings)
try:
    from program.lib.settings import VERSION
except Exception:
    VERSION = "0.0.0"


# Correct GitHub RAW settings.py path
GITHUB_RAW_SETTINGS = (
    "https://raw.githubusercontent.com/"
    "nu11secur1ty/G0BurpSQLmaPI/master/program/lib/settings.py"
)


def parse_version(text):
    """
    Extract VERSION = "x.x.x" from the fetched file.
    """
    for line in text.splitlines():
        if line.strip().startswith("VERSION"):
            try:
                return line.split("=")[1].strip().replace('"', "").replace("'", "")
            except Exception:
                return None
    return None


def check_for_updates():
    print("\n[+] Checking for updates on GitHub...")

    try:
        response = requests.get(GITHUB_RAW_SETTINGS, timeout=10)
    except Exception:
        print("[!] Could not connect to GitHub.")
        return

    if response.status_code != 200:
        print(f"[!] GitHub returned HTTP {response.status_code}")
        return

    remote_text = response.text
    remote_version = parse_version(remote_text)

    if not remote_version:
        print("[!] Could not parse VERSION from GitHub file.")
        return

    print(f"[*] Local version : {VERSION}")
    print(f"[*] Remote version: {remote_version}")

    if remote_version.strip() == VERSION.strip():
        print("[✓] You already have the latest version!")
        return

    print("\n[!] UPDATE AVAILABLE!")
    print(f"    Your version: {VERSION}")
    print(f"    New version:  {remote_version}")
    print("    Update here → https://github.com/nu11secur1ty/G0BurpSQLmaPI\n")


if __name__ == "__main__":
    check_for_updates()
