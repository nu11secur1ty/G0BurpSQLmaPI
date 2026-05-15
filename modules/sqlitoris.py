import os

def sqlitoris_v2():
    print("--- nu11secur1ty Auto-Burp v3 (Realistic Mode) ---")
    
    # 1. Paste URL and go
    raw_url = input("Paste Target URL: ").strip()
    if not raw_url: return

    # 2. Simple input - Press ENTER once and you're done
    print("Paste Payload (JSON/Raw) if any. JUST PRESS ENTER FOR GET:")
    body = input("> ").strip()

    # --- Logic ---
    from urllib.parse import urlparse
    parsed = urlparse(raw_url)
    
    # Auto-Method Detection
    method = "POST" if body else "GET"
    
    # Header Construction (Full Browser Emulation)
    headers = [
        f"{method} {parsed.path or '/'}{'?' + parsed.query if parsed.query else ''} HTTP/1.1",
        f"Host: {parsed.netloc}",
        'Sec-Ch-Ua: "Not-A.Brand";v="24", "Chromium";v="146"',
        'Sec-Ch-Ua-Mobile: ?0',
        'Sec-Ch-Ua-Platform: "Windows"',
        'Upgrade-Insecure-Requests: 1',
        'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site: none',
        'Sec-Fetch-Mode: navigate',
        'Sec-Fetch-User: ?1',
        'Sec-Fetch-Dest: document',
        'Accept-Encoding: gzip, deflate, br',
        'Accept-Language: en-US,en;q=0.9',
        'Priority: u=0, i',
        'Connection: keep-alive'
    ]

    if body:
        c_type = "application/json" if body.startswith(("{", "[")) else "application/x-www-form-urlencoded"
        # Заменяме keep-alive за POST, често е по-добре за Burp
        headers.append(f"Content-Type: {c_type}")
        headers.append(f"Content-Length: {len(body)}")

    raw_request = "\n".join(headers) + "\n\n" + body

    # Save to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "exploit.txt")

    with open(output_path, "w") as f:
        f.write(raw_request)
    
    print("\n" + "="*30)
    print(f"DONE! Method: {method}")
    print(f"File saved to: {output_path}")
    print("="*30 + "\n")
    print(raw_request)

if __name__ == "__main__":
    sqlitoris_v2()
