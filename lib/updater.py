import os
import sys
import shutil
import subprocess
import requests
from datetime import datetime

GITHUB_REPO = "https://api.github.com/repos/nu11secur1ty/G0BurpSQLmaPI"
GIT_URL = "https://github.com/nu11secur1ty/G0BurpSQLmaPI.git"
LOCAL_VERSION_FILE = "version.txt"


def get_local_version():
    if not os.path.exists(LOCAL_VERSION_FILE):
        return "0.0.0"
    with open(LOCAL_VERSION_FILE, "r") as f:
        return f.read().strip()


def get_remote_version():
    try:
        api = requests.get(GITHUB_REPO)
        if api.status_code != 200:
            return None
        data = api.json()
        return data.get("pushed_at", None)
    except:
        return None


def write_local_version(version):
    with open(LOCAL_VERSION_FILE, "w") as f:
        f.write(version)


def update_repository():
    print("[+] Downloading newest update...")

    # If the program itself is a git repo → git pull
    if os.path.isdir(".git"):
        try:
            subprocess.run(["git", "pull"], check=True)
            print("[+] Update completed using git pull.")
            return True
        except:
            print("[!] git pull failed, falling back to full download...")

    # Fallback: full repo download
    TMP_DIR = "_update_tmp"

    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)

    try:
        subprocess.run(["git", "clone", GIT_URL, TMP_DIR], check=True)
    except Exception as e:
        print(f"[!] Git clone failed: {e}")
        return False

    print("[+] Replacing files with repository content...")

    # Copy everything except .git
    for item in os.listdir(TMP_DIR):
        if item == ".git":
            continue
        src = os.path.join(TMP_DIR, item)
        dst = os.path.join(".", item)

        if os.path.exists(dst):
            if os.path.isfile(dst):
                os.remove(dst)
            else:
                shutil.rmtree(dst)

        shutil.move(src, dst)

    shutil.rmtree(TMP_DIR)
    print("[+] Update completed successfully.")
    return True


def check_for_updates():
    print("\n[+] Checking for updates on GitHub...")

    local = get_local_version()
    remote = get_remote_version()

    if remote is None:
        print("[!] Could not connect to GitHub.")
        return

    if local == remote:
        print("[+] You already have the latest version.")
        return

    print(f"[+] New version available: {remote}")
    print("[+] Updating now...\n")

    if update_repository():
        write_local_version(remote)
        print("[+] Updated to latest version!")
        print("[+] Please restart G0BurpSQLmaPI.")
    else:
        print("[!] Update failed.")
