# G0BurpSQLmaPI

**Author:** nu11secur1ty  
**Years:** 2023–2025  
**Language:** Python (with Go modules)  
**Purpose:** A tool to generate SQLi Proof-of-Concept requests, automate SQLMap attacks, and manage attack modules with ease.

---

## Description

G0BurpSQLmaPI is a command-line utility that simplifies the process of crafting and executing SQL injection Proof-of-Concept (PoC) attacks using sqlmap. It combines Go and Python modules to generate exploit requests, launch SQLMap with advanced parameters, and manage auxiliary attack scripts.

---

## Features

- Generate custom SQLi PoC payload files (`exploit.txt`).
- Launch sqlmap with tailored command-line options.
- Run modular attack scripts like `URLi` and `User-Agent`.
- Clean up generated exploit files to avoid leaving traces.
- Interactive menu for easy workflow control.

---

## Requirements

- Python 3.x  
- Go installed and configured (for Go modules)  
- `colorama` Python package  
- sqlmap script located at your specified path (default: `D:\CVE\sqlmap-nu11secur1ty\sqlmap.py`)

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nu11secur1ty/G0BurpSQLmaPI.git
   cd G0BurpSQLmaPI
Install Python dependencies:

bash
Copy
Edit
pip install colorama
Ensure Go is installed and in your system PATH.

Verify your sqlmap.py path in the Python script (G0BurpSQLmaPI.py) and adjust if needed.

Usage
Run the main Python program:

bash
Copy
Edit
python G0BurpSQLmaPI.py
You will see a menu:

sql
Copy
Edit
===== G0BurpSQLmaPI Menu =====

1. Generate PoC exploit.txt
2. Start SQLi with sqlmap
3. Start G0BurpSQLmaPIURLi (module)
3.1 Start G0BurpSQLmaPIUser-Agent (module)
4. Clean evidence (delete exploit.txt)
5. Exit
Choose an option by typing the corresponding number or sub-number.

How to add your POST/GET request
Open G0BurpSQLmaPI.py in a text editor.

Locate the function create_exploit_file().

Replace the placeholder text inside the triple quotes:

python
Copy
Edit
payload = """Your_POST_Request_here!"""
with your full HTTP POST or GET request payload exactly as you want it.

Example:

python
Copy
Edit
payload = """POST /your/target/path HTTP/1.1
Host: vulnerablehost.com
Content-Type: application/x-www-form-urlencoded

username=admin&password=pass"""
Save the file.

IMPORTANT WARNING
⚠️ Do not run this program without setting a valid POST or GET request payload in the PoC generator function.

The program includes a safety check — if the payload string is empty or unchanged from the placeholder, the program will warn you and quit immediately to prevent accidental execution.

Cleaning up
Option 4 in the menu deletes the generated exploit.txt file to remove evidence of your test payload.

License
This project is released under the MIT License (or specify your license).

Contact
Author: nu11secur1ty
GitHub: https://github.com/nu11secur1ty
Email: your-email@example.com (optional)

Disclaimer
This tool is intended solely for authorized security testing and educational purposes.
Unauthorized use is illegal and unethical. Use responsibly and with explicit permission.
The author assumes no responsibility for misuse or damage caused by this software.

Enjoy hacking responsibly! ☠️
