# G0BurpSQLmaPI

![](https://github.com/nu11secur1ty/G0BurpSQLmaPI/blob/master/Docs/G0BurpSQLmaPI.png)

**Author:** nu11secur1ty  
**Years:** 2023–2025  
**Language:** Python (with optional Go modules)  
**Purpose:** Generate SQLi Proof-of-Concept requests, automate sqlmap attacks, and manage attack modules with ease.

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
   ```

2. **Install Python dependencies:**

   ```bash
   pip install colorama
   ```

3. Ensure Go is installed and in your system PATH.

4. Verify your `sqlmap.py` path in the Python script (`G0BurpSQLmaPI.py`) and adjust it if needed.

---

## Usage

Run the main Python program:

```bash
python g0burpsqlmapi.py
```

You will see a menu:

```
===== G0BurpSQLmaPI Menu =====

1. Generate PoC (exploit.txt)
2. Start sqlmap with PoC
3. Run module: modules/URLi.py
4. Run module: modules/User-Agent.py
5. Run module: modules/HashCracker.py
6. View metadata (modules/exploit_meta.json)
7. Clean evidence (delete exploit.txt and metadata)
8. Exit
```

Choose an option by typing the corresponding number.

---

## How to add your POST/GET request

When using `--create` or the interactive menu, paste the full raw HTTP request. The tool expects the payload to start with `POST` or `GET` (first line) and a blank line separating headers from body.

**Example PoC payload:**
```
POST /login.php HTTP/1.1
Host: vulnerablehost.com
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=123456

username=admin&password=pass
```

The tool will:
- Validate the first line (must be POST or GET).  
- Try to auto-detect parameters from the query string and form body (you can accept or edit).  
- Save `exploit.txt` (root) and `modules/exploit.txt` with a small comment header.  
- Save metadata to `modules/exploit_meta.json` for later use.

---

## Passing detected params to sqlmap

If `modules/exploit_meta.json` contains `vuln_params`, the tool will include:
```
-p param1,param2
```
when starting sqlmap, focusing tests on those parameters.

---

## Cleaning up

Use the menu option or CLI `--clean` to delete:
- `exploit.txt` (root)  
- `modules/exploit.txt`  
- `modules/exploit_meta.json`

This helps remove quick evidence of the test payloads. Note: some system logs may still remain outside this tool’s control.

---

## Tests

A small pytest suite is included for the parameter detection routine.

Run tests:
```bash
pip install pytest
pytest -q
```

---

## Logging

- Default log file: `g0burpsqlmapi.log` (rotating).  
- Enable verbose mode (`--verbose`) to increase log detail and stream logs to console.

---

## Contributing & development

- Fork the repo, make changes on a feature branch, and open a pull request.  
- Add tests for new parsing or file behaviors.  
- Keep API and metadata backward compatible where possible.

---

## Changelog (high level)

**2023–2025** — Initial project, CLI + interactive menu, PoC creation, sqlmap integration.  
**2025** — Polished: metadata file, auto parameter detection, logging, argparse CLI, unit tests.

---

## License

This project is licensed under **GPL-3.0**. Preserve license notices and attribution when redistributing.

---

## Contact

- **Author:** nu11secur1ty  
- **GitHub:** https://github.com/nu11secur1ty  
- **Issues / PRs:** Use the repository Issue tracker for bug reports and PRs.

---

## Disclaimer

This software is intended exclusively for authorized security testing and education. The author is not responsible for misuse. Always obtain explicit, written permission before testing any target systems.

Enjoy hacking responsibly. ☠️
