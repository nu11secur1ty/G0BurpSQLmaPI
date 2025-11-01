# tests/test_detect_params.py
from g0burpsqlmapi import detect_params_from_payload

def test_detect_query_params():
    payload = "GET /search.php?q=test&user=alice HTTP/1.1\nHost: example.com\n\n"
    assert detect_params_from_payload(payload) == ["q", "user"]

def test_detect_body_params():
    payload = "POST /login HTTP/1.1\nHost: x\nContent-Type: application/x-www-form-urlencoded\n\nusername=admin&password=1234"
    params = detect_params_from_payload(payload)
    assert "username" in params and "password" in params

def test_detect_name_equals_quotes():
    payload = """POST /submit HTTP/1.1
Host: example
Content-Type: multipart/form-data; boundary=----WebKit
------WebKit
Content-Disposition: form-data; name="email"

test@example.com
"""
    params = detect_params_from_payload(payload)
    assert "email" in params
