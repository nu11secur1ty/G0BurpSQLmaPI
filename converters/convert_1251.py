import json
import os
import sys
import pandas as pd


def convert_csv_to_structured_json(input_file):
    """Reads the CSV file, handles the encoding dynamically, and saves it

    as a beautifully structured and indented JSON file with native Bulgarian text.
    """
    try:
        if not os.path.exists(input_file):
            print(f"Error: The file '{input_file}' was not found.")
            return

        # Define output file path (creates 'Applications_structured.json' in the same folder)
        base_path, _ = os.path.splitext(input_file)
        output_json_file = base_path + "_structured.json"

        csv_data = None

        # Strategy 1: Attempt UTF-8 (SQLMap Default)
        try:
            csv_data = pd.read_csv(
                input_file, encoding="utf-8", sep=None, engine="python"
            )
            print("[*] Successfully read file with UTF-8 encoding.")
        except Exception:
            pass

        # Strategy 2: Fallback to CP1251 with character replacement
        if csv_data is None:
            try:
                with open(input_file, "r", encoding="cp1251", errors="replace") as f:
                    csv_data = pd.read_csv(f, sep=None, engine="python")
                print(
                    "[*] Successfully read file with CP1251 encoding (with character replacement)."
                )
            except Exception as e:
                print(f"[-] Failed to read file with fallback strategy: {e}")
                return

        # Clean NaN values so JSON remains clean and valid
        csv_data = csv_data.fillna("")

        # Convert DataFrame to a list of dictionaries (one dictionary per row)
        records = csv_data.to_dict(orient="records")

        # Save to JSON file with indentation and native Cyrillic output (ensure_ascii=False)
        with open(output_json_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=4, ensure_ascii=False)

        print(
            f"\n[+] Success! The beautifully structured JSON has been saved to:"
        )
        print(f"    {output_json_file}")

        # Print a nice preview of the first record if data exists
        if records:
            print("\n--- Preview of the first structured record ---")
            print(json.dumps(records[0], indent=4, ensure_ascii=False))
        else:
            print("\n[!] The file is empty or contains no rows.")

    except Exception as e:
        print(f"[-] An unexpected error occurred during JSON conversion: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_1251.py <path_to_csv_file>")
    else:
        convert_csv_to_structured_json(sys.argv[1])
