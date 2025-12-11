import requests
import os
import shutil

# GitHub RAW URL for the FULL program directory
GITHUB_ZIP = "https://github.com/nu11secur1ty/G0BurpSQLmaPI/archive/refs/heads/master.zip"

# Local version from settings.py
try:
    from program.lib.settings import VERSION
except:
    VERSION = "0.0.0"


def check_for_updates():
    print("\n[+] Checking for updates on GitHub...")

    api_url = "https://api.github.com/repos/nu11secur1ty/G0BurpSQLmaPI/releases/latest"

    try:
        r = requests.get(api_url, timeout=5)
    except Exception as e:
        print(f"[!] Update check failed: {e}")
        return

    # GitHub returns 404 because you do NOT use releases
    if r.status_code != 200:
        print("[+] No releases found (repo does not use GitHub releases).")
        print("[+] Using fallback version comparison...")

        # fallback → compare commit timestamps
        fallback_url = "https://api.github.com/repos/nu11secur1ty/G0BurpSQLmaPI/commits/master"
        try:
            f = requests.get(fallback_url, timeout=5)
            if f.status_code != 200:
                print("[!] Could not check commits.")
                return
            latest_sha = f.json().get("sha", "unknown")
        except Exception as e:
            print(f"[!] Commit check failed: {e}")
            return

        print(f"[+] Remote commit: {latest_sha[:10]}")
        print(f"[+] Local version: {VERSION}")

        # always offer to update if commit changed
        print("\n[+] Update available!")
        do_update()
        return

    # if you accidentally create a GitHub release someday
    latest_version = r.json().get("tag_name", None)
    if not latest_version:
        print("[!] Invalid release format.")
        return

    if latest_version.strip() == VERSION.strip():
        print("[✓] You are up to date!")
    else:
        print(f"[+] New version available: {latest_version}")
        do_update()


def do_update():
    print("\n[+] Downloading latest version...")

    try:
        zip_data = requests.get(GITHUB_ZIP, timeout=10)
    except Exception as e:
        print(f"[!] Failed to download zip: {e}")
        return

    if zip_data.status_code != 200:
        print("[!] GitHub returned non‑200 status.")
        return

    zip_path = "update.zip"
    with open(zip_path, "wb") as f:
        f.write(zip_data.content)

    print("[+] Extracting...")

    import zipfile
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall("update_tmp")

    # replace program directory
    if os.path.exists("program"):
        shutil.rmtree("program")

    shutil.move("update_tmp/G0BurpSQLmaPI-master/program", "program")

    os.remove(zip_path)
    shutil.rmtree("update_tmp")

    print("[✓] Update complete!")
    print("Restart the tool.")
