# G0BurpSQLmaPI

**Author:** nu11secur1ty  
**Years:** 2023–2025  
**Language:** Python  
**Purpose:** A tool to generate SQLi Proof-of-Concept requests, automate SQLMap attacks, and manage attack modules with ease.

------------------------------------------------------------

## 🧠 Description

G0BurpSQLmaPI is a command-line utility that simplifies the process of crafting and executing SQL injection (SQLi) Proof-of-Concept (PoC) attacks using sqlmap.  
It helps automate advanced SQLMap commands, organize auxiliary modules, and manage evidence — all within an interactive menu.

------------------------------------------------------------

## 🚀 Features

- Generate custom SQLi PoC payload files (`exploit.txt`)  
- Launch `sqlmap` with advanced options automatically  
- Run modular attack scripts (e.g. URLi, User-Agent)  
- Automatic cleanup of generated evidence  
- Interactive and user-friendly CLI menu  

------------------------------------------------------------

## 🧰 Requirements

- Python 3.x  
- `colorama` Python package  
- `sqlmap.py` script (adjustable path in config)  

> ⚠️ Go is no longer required (Go modules deprecated as of v1.0).

------------------------------------------------------------

## 📦 Installation

1. Clone the repo:  
    `git clone https://github.com/nu11secur1ty/G0BurpSQLmaPI.git`

2. Change directory:  
    `cd G0BurpSQLmaPI`

3. Install colorama package:  
    `pip install colorama`

------------------------------------------------------------

## 🧪 Usage

Run the tool:  
`python G0BurpSQLmaPI.py`

You will see this menu:

```
===== G0BurpSQLmaPI Menu =====

Generate PoC exploit.txt

Start SQLi with sqlmap

Start G0BurpSQLmaPIURLi (module)
3.1 Start G0BurpSQLmaPIUser-Agent (module)

Clean evidence (delete exploit.txt)
```



------------------------------------------------------------

## ✍️ Add Your Vulnerable POST/GET Request

- When choosing "Generate PoC exploit.txt", you will be prompted to paste your full vulnerable HTTP request (copied from Burp Suite or a proxy).

Example POST request:

```
POST /vulnerable-path HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

username=admin&password=pass
```


- After pasting, `exploit.txt` will be created automatically and saved inside the `/modules` folder.

------------------------------------------------------------

## ⚠️ WARNING

If you do not paste a valid POST or GET request, the tool will:

- Print an error message in red  
- Exit automatically to protect you from misuse  

✅ Make sure to provide a real, properly formatted request when prompted.

------------------------------------------------------------

## 🧼 Clean Up

To securely remove traces after testing, choose "Clean evidence (delete exploit.txt)" from the menu.

This will:

- Delete `exploit.txt` from the `/modules` directory

------------------------------------------------------------

## 📜 License

------------------------------------------------------------

**👤 Author:** nu11secur1ty  

- 🔗 GitHub: github.com/nu11secur1ty  
- 📧 Email: Ask for it on GitHub issues if needed

------------------------------------------------------------

## ☠️ Legal Disclaimer

- This tool is intended for educational and authorized testing only.  
- Unauthorized use is illegal and unethical.  
- The author assumes no responsibility for damage or misuse.

Happy Hacking — Responsibly. 🧠🔍

