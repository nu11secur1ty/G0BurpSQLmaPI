# G0BurpSQLmaPI by nu11secur1ty

The G0BurpSQLmaPI is a very strong Penetration Testing application for SQLi vulnerabilities detected by [Burp Suite Proffesional](https://portswigger.net/burp/releases#professional).
This application uses the latest Python3.x, etc. The users can modify their exploits and many more.
There will never be a number version! This is very important to know it, dear all. You can redistribute this software by following the stricted rules!!!

![](https://github.com/nu11secur1ty/G0BurpSQLmaPI/blob/main/Docs/G0BurpSQLmaPI.png)

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

### No colored Framework-Advanced-Auto 
- NOTE: For advanced users!
```go
go run .\G0BurpSQLmaPI.go
```

[Demo](https://www.youtube.com/watch?v=PCyHeFP_gKI)
