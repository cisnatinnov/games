import requests
import sys

url = 'http://127.0.0.1:5000/provider'
provider = sys.argv[1] if len(sys.argv) > 1 else 'genai'
api_key = sys.argv[2] if len(sys.argv) > 2 else None
payload = {'provider': provider}
if api_key:
    payload['api_key'] = api_key

r = requests.post(url, json=payload)
print(r.status_code)
print(r.text)
