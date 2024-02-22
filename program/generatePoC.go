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

    val := `your_POST_or_GET_Request_from_Burp_Suite_here`

    data := []byte(val)

    _, err2 := f.Write(data)

    if err2 != nil {
        log.Fatal(err2)
    }
		fmt.Println("done..The PoC was created, execute python exploit.py...")
}
