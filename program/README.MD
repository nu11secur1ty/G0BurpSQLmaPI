### Usage:

- Need to install 

SQLmap:
ORIGINAL_SOURCE:[SQLmap](https://github.com/sqlmapproject/sqlmap)

RECOMMENDED_FOR_G0BurpSQLmaPI:[SQLmap](https://github.com/nu11secur1ty/sqlmap-nu11secur1ty)

- Exploitation:
1. Add your vulnerable POST or GET request from Burp Suite
2. Generate your `exploit.txt`
- - `go run .\generatePoC.go`
3. Execute the program `G0BurpSQLmaPI.py`
- - `python .\G0BurpSQLmaPI.py`
