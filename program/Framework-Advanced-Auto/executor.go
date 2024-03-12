// Golang program to illustrate how to  
// remove files from the default directory 
package main 
   
import ( 
    "log"
    "os"
) 
   
func main() { 
  
    // Removing file from the directory 
    // Using Remove() function 
     e := os.Remove("exploit.txt") 
    if e != nil { 
        log.Fatal(e) 
    } 
}
