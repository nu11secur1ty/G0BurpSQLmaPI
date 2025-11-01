# G0BurpSQLmaPI by nu11secur1ty

---

**Full Automated Python Version — G0BurpSQLmaPI-2025.x.x**

Link: https://github.com/nu11secur1ty/G0BurpSQLmaPI/tree/master/program/Full_Python_Automated

---

## Overview

G0BurpSQLmaPI is a focused penetration-testing utility designed to help security professionals automate exploitation workflows for SQL injection vulnerabilities discovered with Burp Suite Professional. It’s a tool for experienced testers who understand the legal and ethical constraints of offensive security.

> ⚠️ **Important:** Use this software **only** with explicit permission from the systems’ owners. Any misuse is your responsibility.

---

## Supported platforms & requirements

- **Operating systems:** Kali Linux (latest), Ubuntu (latest), Windows 10 / 11  
- **Python:** `3.13.x` (recommended)  
- **Optional / legacy:** `go1.24.x` (if using Go modules in the repo)  
- **Other dependencies:** Burp Suite Professional, sqlmap (recommended fork: `sqlmap-nu11secur1ty`)

---

## Quick links

- Burp Suite Professional: https://portswigger.net/burp/releases#professional  
- Python: https://www.python.org/  
- Official sqlmap: https://github.com/sqlmapproject/sqlmap  
- Recommended sqlmap fork: https://github.com/nu11secur1ty/sqlmap-nu11secur1ty

---

## Features (high level)

- Interactive menu and CLI for creating PoC `exploit.txt` files.  
- Auto-detection of likely vulnerable parameters from request payloads.  
- Saves metadata (`modules/exploit_meta.json`) with discovered vulnerable params and timestamps.  
- Integrates with sqlmap and can pass parsed vuln params to it (`-p`).  
- Simple module runner (`modules/URLi.py`, `modules/User-Agent.py`, `modules/HashCracker.py`, etc.).  
- Verbose logging with rotating log file support.  
- CLI flags for headless operation and automation (`--create`, `--run-sqlmap`, `--module`, `--clean`, `--view-meta`, `--verbose`).  
- Unit tests for core parsing logic (pytest).

---

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/nu11secur1ty/G0BurpSQLmaPI.git
   cd G0BurpSQLmaPI/program/Full_Python_Automated
   ```

2. Install Python dependencies (if any):
   ```bash
   python -m pip install -r requirements.txt
   ```
   > If `colorama` or other optional libs are missing, the script falls back gracefully.

3. Ensure `sqlmap` is installed or set environment variable:
   ```bash
   export G0_SQLMAP_PATH="/path/to/sqlmap.py"
   ```
   On Windows use `setx` (or set the variable in System settings).

---

## Usage

### Interactive menu
```bash
python g0burpsqlmapi.py
```

### CLI examples
- Create PoC (interactive):
  ```bash
  python g0burpsqlmapi.py --create
  ```
- Run sqlmap with the saved PoC:
  ```bash
  python g0burpsqlmapi.py --run-sqlmap
  ```
- Run a module:
  ```bash
  python g0burpsqlmapi.py --module URLi.py
  ```
- View saved metadata:
  ```bash
  python g0burpsqlmapi.py --view-meta
  ```
- Clean generated files:
  ```bash
  python g0burpsqlmapi.py --clean
  ```
- Enable verbose logging:
  ```bash
  python g0burpsqlmapi.py --verbose
  ```

---

## PoC & metadata

- Primary PoC file: `exploit.txt` (root) and `modules/exploit.txt`  
- Metadata file: `modules/exploit_meta.json` — contains `vuln_params` and `created_at` timestamp

When creating a PoC the tool:
- Validates that the payload starts with `POST` or `GET`.  
- Attempts to auto-detect parameters from the request and body (you can accept or edit).  
- Stores both the PoC and a small metadata JSON for later use (e.g., passing `-p` to sqlmap).

---

## Tests

A small pytest test set is included for core parsing logic.

Run tests:
```bash
pip install pytest
pytest -q
```

---

## Licensing & redistribution

This project is licensed under **GPL-3.0** (preserve the license file and notices when redistributing). See `LICENSE` in the repository root for full terms.

---

## Professional services

If you want demos, corporate integration, or custom work:

- Corporate demo: **$5000** for 2 days (installation, customization, demonstrations across SQLi types).  
- Public demo / training: **$50 per attendee** (ticketed event).

Contact/arrangements via the repo or the maintainer’s preferred channels.

---

## Notes / attribution

- This tool is built for experienced penetration testers and security researchers. Not intended for beginners or misuse.  
- Respect targets: get written authorization before testing. Laws vary by country — act responsibly.

---

## Contact & credits

Maintainer: **nu11secur1ty** — please see the GitHub repository for more details, issues, and contributions.

---

Thank you for using G0BurpSQLmaPI — keep it legal, ethical, and professional.
