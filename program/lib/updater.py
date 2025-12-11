import os
import ssl
import shutil
import urllib.request
import zipfile
import tempfile

# ============================================================
#   G0BurpSQLmaPI - AUTO UPDATER (FULL VERSION)
#   Put this file in: program/lib/updater.py
# ============================================================

LOCAL_VERSION = "1.0.0"
REPO = "nu11secur1ty/G0BurpSQLmaPI"

# RAW version file
URL_VERSION = (
    "https://raw.githubusercontent.com/nu11secur1ty/"
    "G0BurpSQLmaPI/master/program/lib/settings.py"
)

# FULL ZIP for updating
URL_ZIP = (
    f"https://github.com/{REPO}/archive/refs/heads/master.zip"
)

# Fallback RAW IP mirror (GitHub IP)
URL_VERSION_IP = (
    "https://185.199.108.133/nu11secur1ty/G0BurpSQLmaPI/master/program/lib/settings.py"
)


def print_banner():
    print("\n===============================")
    print("      G0BurpSQLmaPI Updater")
    print("===============================")


def fetch(url, insecure=False):
    """Download content from URL with optional SSL-bypass."""
    ctx = None
    if insecure:
        ctx = ssl._create_unverified_context()

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0"
    })

    with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
        return r.read().decode("utf-8")


def extract_version(text):
    """Parse VERSION from remote settings.py."""
    for line in text.splitlines():
        if "VERSION" in line and "=" in line:
            return line.split("=")[1].strip().replace('"', "").replace("'", "")
    return None


def download_zip(url, dest):
    """Download the ZIP file to a destination."""
    print("[+] Downloading update ZIP...")
    urllib.request.urlretrieve(url, dest)
    print("[+] ZIP downloaded.")


def apply_update(zip_path):
    """Extract and overwrite local installation."""
    print("[+] Extracting update...")

    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(tmp)

    extracted_folder = os.path.join(tmp, "G0BurpSQLmaPI-master")
    dest_folder = os.getcwd()

    print("[+] Overwriting current installation...")
    for item in os.listdir(extracted_folder):
        s = os.path.join(extracted_folder, item)
        d = os.path.join(dest_folder, item)

        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

    print("[✓] Update installed successfully.")


def check_for_updates():
    print_banner()
    print("[*] Checking for updates...")

    # STEP 1 — NORMAL HTTPS
    try:
        remote = fetch(URL_VERSION)
        print("[+] HTTPS OK")
    except Exception as e1:
        print(f"[!] HTTPS failed: {e1}")

        # STEP 2 — DISABLE SSL VALIDATION
        try:
            print("[*] Retrying with SSL bypass...")
            remote = fetch(URL_VERSION, insecure=True)
            print("[+] SSL bypass OK")
        except Exception as e2:
            print(f"[!] SSL bypass failed: {e2}")

            # STEP 3 — RAW IP FALLBACK
            try:
                print("[*] Trying IP fallback mirror...")
                remote = fetch(URL_VERSION_IP, insecure=True)
                print("[+] IP fallback OK")
            except Exception as e3:
                print("[!!!] ALL CONNECTION METHODS FAILED")
                print(f"LATEST ERROR: {e3}")
                return

    remote_ver = extract_version(remote)
    if not remote_ver:
        print("[!] Failed to parse remote version!")
        return

    print(f"\n[*] Local version : {LOCAL_VERSION}")
    print(f"[*] Remote version: {remote_ver}")

    if remote_ver == LOCAL_VERSION:
        print("[✓] You are already up to date.\n")
        return

    print("\n[!] UPDATE AVAILABLE!")
    print(f"    Installed: {LOCAL_VERSION}")
    print(f"    Latest:    {remote_ver}")

    # DOWNLOAD NEW ZIP
    print("\n[*] Preparing update...")
    temp_zip = os.path.join(tempfile.gettempdir(), "g0burp_update.zip")

    try:
        download_zip(URL_ZIP, temp_zip)
    except Exception as e:
        print(f"[!] Could not download update ZIP: {e}")
        return

    try:
        apply_update(temp_zip)
        print("\n[✓] Updated to latest version!")
    except Exception as e:
        print(f"[!] Failed to apply update: {e}")
    finally:
        if os.path.exists(temp_zip):
            os.remove(temp_zip)


if __name__ == "__main__":
    check_for_updates()
