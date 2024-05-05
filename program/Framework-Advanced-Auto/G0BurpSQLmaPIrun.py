#!/usr/bin/python
import os
import time
from colorama import init, Fore, Back, Style
init(convert=True)

def display_menu():
    print(Fore.YELLOW +"===== G0BurpSQLmaPI Menu =====")
    print("1. Generate PoC")
    print("2. Start PyG0BurpSQLmaPI")
    print("3. Clean")
    print("4. Exit")
print(Style.RESET_ALL)

def execute_command(choice):
    if choice == '1':
        os.system("go run G0BurpSQLmaPI.go")
    elif choice == '2':
        os.system("python G0BurpSQLmaPI.py")
    elif choice == '3':
        os.system("go run executor.go")
        print("Done: you've cleaned the evidence!")
    elif choice == '4':
        print("Exiting...")
    else:
        print("Invalid choice. Please select a valid option.")
if __name__ == "__main__":
    while True:
        display_menu()
        user_choice = input("Enter your choice: ")
        execute_command(user_choice)
        
        if user_choice == '4':
            break
