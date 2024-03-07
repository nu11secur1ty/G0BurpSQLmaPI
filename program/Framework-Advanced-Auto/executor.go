// Remove the evidences
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
