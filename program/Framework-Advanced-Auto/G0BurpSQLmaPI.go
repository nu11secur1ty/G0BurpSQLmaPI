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

    val := `Your_vulnerable_POST_ot_GET_Request_from_Burp`

    data := []byte(val)

    _, err2 := f.Write(data)

    if err2 != nil {
        log.Fatal(err2)
    }
		fmt.Println("done..The PoC was created, and the exploit will be continuing...")
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
}

func copyOutput(r io.Reader) {
    scanner := bufio.NewScanner(r)
    for scanner.Scan() {
        fmt.Println(scanner.Text())
    }
}

