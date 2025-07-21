# G0BurpSQLmaPI

**Author:** nu11secur1ty  
**Years:** 2023–2025  
**Language:** Python  
**Purpose:** A tool to generate SQLi Proof-of-Concept requests, automate SQLMap attacks, and manage attack modules with ease.



## 🧠 Description

**G0BurpSQLmaPI** is a command-line utility that simplifies the process of crafting and executing SQL injection (SQLi) Proof-of-Concept (PoC) attacks using [sqlmap](https://github.com/sqlmapproject/sqlmap). It helps automate advanced SQLMap commands, organize auxiliary modules, and manage evidence — all within an interactive menu.



## 🚀 Features

- Generate custom SQLi PoC payload files (`exploit.txt`)
- Launch `sqlmap` with advanced options automatically
- Run modular attack scripts (e.g. `URLi`, `User-Agent`)
- Automatic cleanup of generated evidence
- Interactive and user-friendly CLI menu


## 🧰 Requirements

- Python 3.x  
- [`colorama`](https://pypi.org/project/colorama/) Python package  
- `sqlmap.py` script (adjustable path in config)

> ⚠️ Go is no longer required (Go modules deprecated as of v1.0).


## 📦 Installation

```bash
git clone https://github.com/nu11secur1ty/G0BurpSQLmaPI.git
cd G0BurpSQLmaPI
pip install colorama
```

🧪 Usage
Start the tool from the main script:

```
python G0BurpSQLmaPI.py
```

. You’ll see this menu:

```
===== G0BurpSQLmaPI Menu =====

1. Generate PoC exploit.txt
2. Start SQLi with sqlmap
3. Start G0BurpSQLmaPIURLi (module)
3.1 Start G0BurpSQLmaPIUser-Agent (module)
4. Clean evidence (delete exploit.txt)
5. Exit
```

✍️ Add Your Vulnerable POST/GET Request
. You’ll be prompted to paste your full vulnerable request (copied from Burp Suite or a proxy):
. Example POST:

```
POST /vulnerable-path HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

username=admin&password=pass
```

After pasting, exploit.txt will be created automatically and copied to the /modules folder.


⚠️ WARNING


If you do not paste a valid POST or GET request, the tool will:

. Print a red error

. Exit automatically to protect you from misuse

✅ Make sure you provide a real, formatted request when prompted.


🧼 Clean Up

To securely remove traces after testing:

```
Choose option 4 in the menu
```


This will:

. Delete exploit.txt from the main directory
. Delete any leftover copies inside /modules


📜 License

----------------------------------------------------------------------


👤 Author: nu11secur1ty
. 🔗 GitHub: github.com/nu11secur1ty
. 📧 Email: Ask for it on GitHub issues if needed


----------------------------------------------------------------------

☠️ Legal Disclaimer
    This tool is intended for educational and authorized testing only.
    Unauthorized use is illegal and unethical.
    The author assumes no responsibility for damage or misuse.


Happy Hacking — Responsibly. 🧠🔍
