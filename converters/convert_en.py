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


def convert_csv_to_translated_json(input_file):
    """Reads the CSV file, handles encoding, translates all Bulgarian values

    to English, and saves a beautifully structured bilingual JSON.
    """
    try:
        if not os.path.exists(input_file):
            print(f"Error: The file '{input_file}' was not found.")
            return

        base_path, _ = os.path.splitext(input_file)
        output_json_file = base_path + "_translated.json"

        csv_data = None

        # Strategy 1: Attempt UTF-8 (SQLMap Default)
        try:
            csv_data = pd.read_csv(
                input_file, encoding="utf-8", sep=None, engine="python"
            )
            print("[*] Successfully read file with UTF-8 encoding.")
        except Exception:
            pass

        # Strategy 2: Fallback to CP1251
        if csv_data is None:
            try:
                with open(input_file, "r", encoding="cp1251", errors="replace") as f:
                    csv_data = pd.read_csv(f, sep=None, engine="python")
                print("[*] Successfully read file with CP1251 encoding.")
            except Exception as e:
                print(f"[-] Failed to read file: {e}")
                return

        csv_data = csv_data.fillna("")
        raw_records = csv_data.to_dict(orient="records")

        print(
            f"[*] Found {len(raw_records)} rows. Translating content to English (this may take a moment)..."
        )

        translated_records = []
        for index, row in enumerate(raw_records):
            translated_row = {}
            for key, value in row.items():
                # Keep the original Bulgarian data
                translated_row[key] = value

                # If the value is text, create an additional translated field (e.g., "status_en")
                if isinstance(value, str) and any(
                    "а" <= char <= "я" or "А" <= char <= "Я" for char in value
                ):
                    translated_row[f"{key}_en"] = translate_text(value)

            translated_records.append(translated_row)

            # Progress indicator for large dumps
            if (index + 1) % 10 == 0 or (index + 1) == len(raw_records):
                print(f"    Processed {index + 1}/{len(raw_records)} rows...")

        # Save to structured JSON
        with open(output_json_file, "w", encoding="utf-8") as f:
            json.dump(translated_records, f, indent=4, ensure_ascii=False)

        print(f"\n[+] Success! The translated JSON has been saved to:")
        print(f"    {output_json_file}")

        if translated_records:
            print("\n--- Preview of the first translated record ---")
            print(json.dumps(translated_records[0], indent=4, ensure_ascii=False))

    except Exception as e:
        print(f"[-] An unexpected error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_1251.py <path_to_csv_file>")
    else:
        convert_csv_to_translated_json(sys.argv[1])
