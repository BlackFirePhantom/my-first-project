import socket
import urllib.parse
import requests

def test_dns(host):
    print(f"Resolving DNS for {host}...")
    try:
        ips = socket.gethostbyname_ex(host)
        print(f" -> IPs found: {ips[2]}")
        return ips[2]
    except Exception as e:
        print(f" -> DNS Resolution failed: {e}")
        return []

def test_http_get(url):
    print(f"GET request to {url} (timeout=5)...")
    try:
        resp = requests.get(url, timeout=5, verify=False, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        print(f" -> Status: {resp.status_code}, Length: {len(resp.content)} bytes")
        return True
    except Exception as e:
        print(f" -> Request failed: {e}")
        return False

print("=== START CONNECTION DIAGNOSTIC ===")
target_host = "m.00shu.la"
ips = test_dns(target_host)

test_http_get(f"https://{target_host}/")
test_http_get(f"http://{target_host}/")

print("\n=== Checking other sources ===")
test_http_get("https://www.22biqu.com/")
test_http_get("https://www.jkwxw.cc/")
test_http_get("https://www.mayiwsk.com/")
print("=== END DIAGNOSTIC ===")
