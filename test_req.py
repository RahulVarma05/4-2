import requests

resp = requests.post("http://127.0.0.1:5000/generate")
print(f"Status Code: {resp.status_code}")
print(f"Body: {resp.text}")
