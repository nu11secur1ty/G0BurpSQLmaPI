#!/usr/bin/python
# nu11secur1ty 2023-2024
import os
import time

os.system("go run G0BurpSQLmaPI.go")
time.sleep(5)
os.system("go run executor.go")
print("Done: you've cleaned the evidence!")
	
