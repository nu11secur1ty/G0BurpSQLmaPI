#!/usr/bin/env python3
# HashCracker module for G0BurpSQLmaPI by nu11secur1ty 2023–2025

import hashlib
import os
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

try:
    import bcrypt
except ImportError:
    print("bcrypt module not found. Install with: pip install bcrypt")
    sys.exit(1)

# Wordlist and threading
WORDLIST = os.path.join(os.path.dirname(__file__), "HashCracker_wordlist/nu11secur1ty.txt")
THREADS = 8  # adjust for your CPU
CRACKED_FILE = os.path.join(os.path.dirname(__file__), "cracked_hashes.txt")

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

# Hashing function
def hash_text(word: str, hash_type: str, salt: str = "") -> str:
    text = (salt + word).encode("utf-8")
    hash_type = hash_type.lower()
    if hash_type == "md5":
        return hashlib.md5(text).hexdigest()
    elif hash_type == "sha1":
        return hashlib.sha1(text).hexdigest()
    elif hash_type == "sha256":
        return hashlib.sha256(text).hexdigest()
    elif hash_type == "sha512":
        return hashlib.sha512(text).hexdigest()
    elif hash_type == "mysql_old":
        h = hashlib.sha1(text).digest()[:16]
        return h.hex()
    else:
        raise ValueError("Unsupported hash type")

# Generate word variants
def generate_variants(word: str):
    variants = set()
    w = word.strip("\r\n")
    variants.add(w)
    variants.add(w.lower())
    variants.add(w.upper())
    variants.add(w.capitalize())
    variants.add(w + " ")
    variants.add(w + "\n")
    variants.add(w + "\r\n")
    return variants

# Word check
def check_word(word, target_hash, hash_type, salt=""):
    for variant in generate_variants(word):
        if hash_text(variant, hash_type, salt) == target_hash:
            return variant
    return None

# Bcrypt check
def check_bcrypt(word, target_hash):
    for variant in generate_variants(word):
        try:
            if bcrypt.checkpw(variant.encode('utf-8'), target_hash.encode('utf-8')):
                return variant
        except ValueError:
            continue
    return None

# Save cracked password with timestamp and optional source
def save_cracked(target_hash, plaintext, hash_type, source="local"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(CRACKED_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [{source}] {hash_type.upper()} | {target_hash} | {plaintext}\n")
        print(f"{Colors.GREEN}[i] Saved cracked password to '{CRACKED_FILE}'{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}[!] Failed to save cracked password: {e}{Colors.END}")

# Auto-detect hash type
def detect_hash_type(target_hash):
    target_hash = target_hash.strip()
    if target_hash.startswith(("$2a$", "$2b$", "$2y$")):
        return "bcrypt"
    length = len(target_hash)
    if length == 32 and all(c in "0123456789abcdefABCDEF" for c in target_hash):
        return "md5"
    if length == 40 and all(c in "0123456789abcdefABCDEF" for c in target_hash):
        return "sha1"
    if length == 64 and all(c in "0123456789abcdefABCDEF" for c in target_hash):
        return "sha256"
    if length == 128 and all(c in "0123456789abcdefABCDEF" for c in target_hash):
        return "sha512"
    if length == 32:
        return "mysql_old"
    return None

# Parallel hash cracking
def crack_hash_parallel(target_hash: str, hash_type: str = None, wordlist_path: str = WORDLIST, salt: str = "", source: str = "local"):
    if not os.path.exists(wordlist_path):
        print(f"{Colors.RED}[-] Wordlist not found: {wordlist_path}{Colors.END}")
        return None

    if hash_type is None:
        detected = detect_hash_type(target_hash)
        hash_type = detected if detected else "md5"

    print(f"{Colors.CYAN}[i] Using wordlist: {wordlist_path}{Colors.END}")
    print(f"{Colors.CYAN}[i] Hash type: {hash_type.upper()}{Colors.END}")
    if salt:
        print(f"{Colors.CYAN}[i] Using salt: {salt}{Colors.END}")

    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        words = [line.strip() for line in f]

    try:
        if hash_type == "bcrypt":
            for word in words:
                result = check_bcrypt(word, target_hash)
                if result:
                    print(f"{Colors.GREEN}[+] Found match: {repr(result)}{Colors.END}")
                    save_cracked(target_hash, result, hash_type, source)
                    return result
        else:
            executor = ThreadPoolExecutor(max_workers=THREADS)
            futures = [executor.submit(check_word, w, target_hash, hash_type, salt) for w in words]

            while futures:
                done, not_done = as_completed(futures, timeout=0.1), []
                for future in done:
                    try:
                        result = future.result(timeout=0.1)
                        if result:
                            print(f"{Colors.GREEN}[+] Found match: {repr(result)}{Colors.END}")
                            save_cracked(target_hash, result, hash_type, source)
                            executor.shutdown(wait=False, cancel_futures=True)
                            return result
                    except TimeoutError:
                        not_done.append(future)
                futures = list(not_done)

    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[!] Interrupted by user. Shutting down...{Colors.END}")
        if hash_type != "bcrypt":
            executor.shutdown(wait=False, cancel_futures=True)
        sys.exit(0)
    finally:
        if hash_type != "bcrypt":
            executor.shutdown(wait=False, cancel_futures=True)

    print(f"{Colors.RED}[-] No match found in the wordlist (with variants).{Colors.END}")
    return None

# Main menu
def main_menu():
    try:
        print(f"{Colors.HEADER}{Colors.BOLD}=== Wordlist Hash Cracker ==={Colors.END}")
        print(f"{Colors.BLUE}1.{Colors.END} MD5")
        print(f"{Colors.BLUE}2.{Colors.END} SHA-1")
        print(f"{Colors.BLUE}3.{Colors.END} SHA-256")
        print(f"{Colors.BLUE}4.{Colors.END} SHA-512")
        print(f"{Colors.BLUE}5.{Colors.END} MySQL OLD_PASSWORD()")
        print(f"{Colors.BLUE}6.{Colors.END} Bcrypt")
        choice = input("Choose hash type (1-6, leave empty for auto-detect): ").strip()

        mapping = {
            "1": "md5",
            "2": "sha1",
            "3": "sha256",
            "4": "sha512",
            "5": "mysql_old",
            "6": "bcrypt"
        }

        hash_type = mapping.get(choice) if choice else None
        target_hash = input(f"Enter hash to crack: ").strip()
        salt = ""
        if hash_type not in ["md5", "sha1", "sha256", "sha512", "bcrypt"]:
            salt = input("Enter salt (leave empty if none): ").strip()

        source = input("Enter optional source/host info (or leave empty): ").strip() or "local"

        crack_hash_parallel(target_hash, hash_type, WORDLIST, salt, source)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[!] Exiting cleanly...{Colors.END}")
        sys.exit(0)

if __name__ == "__main__":
    main_menu()
