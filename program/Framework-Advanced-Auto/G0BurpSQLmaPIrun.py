#!/usr/bin/python
import os
import time
from colorama import init, Fore, Back, Style
import sys

init(convert=True)

def display_menu():
    print(Fore.BLUE +"===== G0BurpSQLmaPI Menu =====")
    print(Style.RESET_ALL)
    print(Fore.GREEN +"1. Generate PoC")
    print(Style.RESET_ALL)
    print(Fore.GREEN +"2. Start G0BurpSQLmaPI")
    print(Style.RESET_ALL)
    print(Fore.GREEN +"3. Start G0BurpSQLmaPIURLi")
    print(Style.RESET_ALL)
    print(Fore.GREEN +"3.1. Start G0BurpSQLmaPIUser-Agent")
    print(Style.RESET_ALL)
    print(Fore.GREEN +"4. Clean")
    print(Style.RESET_ALL)
    print(Fore.GREEN +"5. Exit")
    print(Style.RESET_ALL)

def execute_command(choice):
    if choice == '1':
        os.system("go run G0BurpSQLmaPI.go")
    elif choice == '2':
        os.system("python G0BurpSQLmaPI.py")
    elif choice == '3':
        os.system("python modules/URLi.py")
    elif choice == '3.1':
        os.system("python modules/User-Agent.py")
    elif choice == '4':
        os.system("go run executor.go")
        print("Done: you've cleaned the evidence!")
    elif choice == '5':
        print("Exiting...")
    else:
        print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    try:
        while True:
            display_menu()
            user_choice = input("Enter your choice: ")
            execute_command(user_choice)

            if user_choice == '5':
                break
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C without error messages
        sys.exit(0)

