#!/usr/bin/env python3
# HashCracker module for G0BurpSQLmaPI by nu11secur1ty 2023–2025

import hashlib
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

# Wordlist and threading
WORDLIST = os.path.join(os.path.dirname(__file__), "HashCracker_wordlist/nu11secur1ty.txt")
THREADS = 8  # adjust for your CPU

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

def check_word(word, target_hash, hash_type, salt=""):
    for variant in generate_variants(word):
        if hash_text(variant, hash_type, salt) == target_hash:
            return variant
    return None

def crack_hash_parallel(target_hash: str, hash_type: str, wordlist_path: str = WORDLIST, salt: str = ""):
    if not os.path.exists(wordlist_path):
        print(f"{Colors.RED}[-] Wordlist not found: {wordlist_path}{Colors.END}")
        return None

    print(f"{Colors.CYAN}[i] Using wordlist: {wordlist_path}{Colors.END}")
    print(f"{Colors.CYAN}[i] Hash type: {hash_type.upper()}{Colors.END}")
    if salt:
        print(f"{Colors.CYAN}[i] Using salt: {salt}{Colors.END}")

    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        words = [line.strip() for line in f]

    executor = ThreadPoolExecutor(max_workers=THREADS)
    futures = [executor.submit(check_word, w, target_hash, hash_type, salt) for w in words]

    try:
        while futures:
            done, not_done = as_completed(futures, timeout=0.1), []
            for future in done:
                try:
                    result = future.result(timeout=0.1)
                    if result:
                        print(f"{Colors.GREEN}[+] Found match: {repr(result)}{Colors.END}")
                        executor.shutdown(wait=False, cancel_futures=True)
                        return result
                except TimeoutError:
                    not_done.append(future)
            futures = list(not_done)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[!] Interrupted by user. Shutting down threads...{Colors.END}")
        executor.shutdown(wait=False, cancel_futures=True)
        sys.exit(0)
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

    print(f"{Colors.RED}[-] No match found in the wordlist (with variants).{Colors.END}")
    return None

# Colorized menu
def main_menu():
    try:
        print(f"{Colors.HEADER}{Colors.BOLD}=== Wordlist Hash Cracker ==={Colors.END}")
        print(f"{Colors.BLUE}1.{Colors.END} MD5")
        print(f"{Colors.BLUE}2.{Colors.END} SHA-1")
        print(f"{Colors.BLUE}3.{Colors.END} SHA-256")
        print(f"{Colors.BLUE}4.{Colors.END} SHA-512")
        print(f"{Colors.BLUE}5.{Colors.END} MySQL OLD_PASSWORD()")
        choice = input("Choose hash type (1-5): ").strip()

        mapping = {
            "1": "md5",
            "2": "sha1",
            "3": "sha256",
            "4": "sha512",
            "5": "mysql_old"
        }

        hash_type = mapping.get(choice, "md5")
        target_hash = input(f"Enter {hash_type.upper()} hash to crack: ").strip()
        salt = ""
        if hash_type not in ["md5", "sha1", "sha256", "sha512"]:
            salt = input("Enter salt (leave empty if none): ").strip()

        crack_hash_parallel(target_hash, hash_type, WORDLIST, salt)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[!] Exiting cleanly...{Colors.END}")
        sys.exit(0)

if __name__ == "__main__":
    main_menu()
