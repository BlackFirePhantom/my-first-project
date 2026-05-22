import requests

url = "https://www.linovelib.com/themes/zhpc/js/pctheme.js?v0122.7"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://www.linovelib.com",
}

resp = requests.get(url, headers=headers)
print("Status code:", resp.status_code)
lines = resp.text.split("\n")
print(f"Total lines: {len(lines)}")
# Print lines around 220
start = max(0, 215)
end = min(len(lines), 230)
for i in range(start, end):
    print(f"Line {i+1}: {lines[i][:150]}")
