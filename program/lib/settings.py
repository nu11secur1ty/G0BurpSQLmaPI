# ============================================================
#  G0BurpSQLmaPI SETTINGS MODULE (inside /lib/settings.py)
#  Modular configuration for attack profiles + version control
# ============================================================

VERSION = "1.0.0"

# GitHub repo for update checking
GITHUB_REPO = "nu11secur1ty/G0BurpSQLmaPI"
GITHUB_RAW_SETTINGS = (
    f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/lib/settings.py"
)

# Default tamper scripts
TAMPERS = "between,randomcase,space2comment"

# ============================================================
# SQLMAP ATTACK PROFILES
# ============================================================

ATTACK_PROFILES = {
    "aggressive": {
        "name": "🔥 AGGRESSIVE",
        "description": "Default fast attack",
        "options": [
            "--batch",
            "--risk=2",
            "--level=3",
            f"--tamper={TAMPERS}",
        ],
    },

    "time_based": {
        "name": "⏱️ TIME-BASED",
        "description": "Blind SQLi (timing)",
        "options": [
            "--batch",
            "--technique=T",
            "--risk=3",
            "--level=5",
        ],
    },

    "stealth": {
        "name": "🛡️ STEALTH",
        "description": "Low noise, WAF bypass",
        "options": [
            "--batch",
            "--level=1",
            "--risk=1",
            "--technique=E",
            f"--tamper={TAMPERS}",
        ],
    },

    "fast": {
        "name": "🚀 FAST",
        "description": "Quick recon",
        "options": [
            "--batch",
            "--level=1",
            "--risk=1",
        ],
    },

    "full_dump": {
        "name": "📊 FULL DUMP",
        "description": "Extract all DB data",
        "options": [
            "--batch",
            "--dump-all",
            "--risk=3",
            "--level=5",
            f"--tamper={TAMPERS}",
        ],
    },

    "ultimate": {
        "name": "💀 ULTIMATE",
        "description": "Max power (OS shell, full takeover)",
        "options": [
            "--batch",
            "--dbms=mysql",
            "--risk=3",
            "--level=5",
            "--threads=10",
            "--technique=BEUSTQ",
            "--privileges",
            "--roles",
            "--dbs",
            "--os-shell",
            f"--tamper={TAMPERS}",
        ],
    },

    "custom": {
        "name": "⚙️ CUSTOM",
        "description": "User-provided sqlmap flags",
        "options": [],
    },
}
