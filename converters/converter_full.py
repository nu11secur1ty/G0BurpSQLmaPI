import json
import os
import sys
from deep_translator import GoogleTranslator
import pandas as pd


def translate_text(text):
    """Translates Cyrillic text to English.

    Returns the original if it's a number, empty, or already English.
    """
    if not text or str(text).strip() == "" or str(text).isdigit():
        return text
    try:
        # Automatically detects Bulgarian and translates to English
        return GoogleTranslator(source="auto", target="en").translate(str(text))
    except Exception:
        return text  # Fallback to original text if translation fails


def process_single_csv(input_file):
    """Processes a single CSV file: handles encoding, translates, and saves as JSON."""
    base_path, _ = os.path.splitext(input_file)
    output_json_file = base_path + "_translated.json"

    csv_data = None

    # Strategy 1: Attempt UTF-8 (SQLMap Default)
    try:
        csv_data = pd.read_csv(
            input_file, encoding="utf-8", sep=None, engine="python"
        )
    except Exception:
        pass

    # Strategy 2: Fallback to CP1251
    if csv_data is None:
        try:
            with open(input_file, "r", encoding="cp1251", errors="replace") as f:
                csv_data = pd.read_csv(f, sep=None, engine="python")
        except Exception as e:
            print(f"  [-] Failed to read file {input_file}: {e}")
            return False

    csv_data = csv_data.fillna("")
    raw_records = csv_data.to_dict(orient="records")

    if not raw_records:
        print(f"  [!] File is empty: {input_file}")
        return False

    print(
        f"  [*] Found {len(raw_records)} rows. Translating content (Cyrillic -> English)..."
    )

    translated_records = []
    for index, row in enumerate(raw_records):
        translated_row = {}
        for key, value in row.items():
            translated_row[key] = value

            # If the value contains Cyrillic characters, create a translated field
            if isinstance(value, str) and any(
                "а" <= char <= "я" or "А" <= char <= "Я" for char in value
            ):
                translated_row[f"{key}_en"] = translate_text(value)

        translated_records.append(translated_row)

        # Progress tracking for larger dumps
        if (index + 1) % 20 == 0 or (index + 1) == len(raw_records):
            print(f"    Progress: {index + 1}/{len(raw_records)} rows...")

    # Save to structured JSON
    with open(output_json_file, "w", encoding="utf-8") as f:
        json.dump(translated_records, f, indent=4, ensure_ascii=False)

    print(f"  [+] Success! Saved JSON to: {output_json_file}")
    return True


def scan_and_convert(target_path):
    """Scans a path.

    If it's a file, processes it. If it's a directory, processes all CSV files
    inside it.
    """
    if not os.path.exists(target_path):
        print(f"[-] Error: The path '{target_path}' does not exist.")
        return

    # Case 1: The user provided a single file directly
    if os.path.isfile(target_path):
        if target_path.lower().endswith(".csv"):
            print(f"[+] Processing single file...")
            process_single_csv(target_path)
        else:
            print("[-] Error: The provided file is not a CSV file.")

    # Case 2: The user provided a folder path
    elif os.path.isdir(target_path):
        print(f"[+] Scanning directory for CSV files: {target_path}")
        csv_files = []

        # Recursively find all CSV files in the folder and subfolders
        for root, dirs, files in os.walk(target_path):
            for file in files:
                if file.lower().endswith(".csv"):
                    csv_files.append(os.path.join(root, file))

        if not csv_files:
            print("[-] No CSV files found in this directory.")
            return

        print(f"[+] Found {len(csv_files)} CSV file(s) to process.\n")

        for idx, csv_file in enumerate(csv_files, 1):
            print(f"[{idx}/{len(csv_files)}] Processing: {csv_file}")
            process_single_csv(csv_file)
            print("-" * 50)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_1251.py <path_to_csv_file_or_directory>")
    else:
        scan_and_convert(sys.argv[1])
