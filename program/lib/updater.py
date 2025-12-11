import os
import ssl
import urllib.request

RAW_SETTINGS_URL = "https://raw.githubusercontent.com/nu11secur1ty/G0BurpSQLmaPI/master/program/lib/settings.py"
LOCAL_VERSION = "1.0.0"


def check_for_updates():
    print("[+] Checking for updates on GitHub...")

    try:
        # Disable SSL validation (GitHub sometimes fails on proxies/tunnels)
        ctx = ssl._create_unverified_context()

        req = urllib.request.Request(
            RAW_SETTINGS_URL,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            data = response.read().decode("utf-8")

    except Exception as e:
        print(f"[!] Could not connect to GitHub: {e}")
        return

    # Extract remote version
    remote_version = None
    for line in data.splitlines():
        if "VERSION" in line and "=" in line:
            remote_version = line.split("=")[1].strip().replace('"', "").replace("'", "")
            break

    if not remote_version:
        print("[!] ERROR: Could not parse remote version!")
        return

    print(f"[*] Local version:  {LOCAL_VERSION}")
    print(f"[*] Remote version: {remote_version}")

    if remote_version == LOCAL_VERSION:
        print("[✓] You already have the latest version.")
    else:
        print("[!] UPDATE AVAILABLE!")
        print("    > You must pull manually for now.")
        print("    Repo: https://github.com/nu11secur1ty/G0BurpSQLmaPI")


if __name__ == "__main__":
    check_for_updates()
