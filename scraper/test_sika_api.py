import urllib.request
import json
import urllib.parse

def test_api():
    url = "https://www.sikafinance.com/api/general/Search?q=" + urllib.parse.quote("SONA")
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print("Search result:")
            print(data)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_api()
