from dotenv import load_dotenv
import os
import requests

load_dotenv(r"C:\Users\User\Desktop\PUTER\.env")

ETSY_KEYSTRING = os.getenv("ETSY_KEYSTRING")
ETSY_SHARED_SECRET = os.getenv("ETSY_SHARED_SECRET")

if not ETSY_KEYSTRING:
    print("ERROR: ETSY_KEYSTRING not found in .env")
    raise SystemExit

if not ETSY_SHARED_SECRET:
    print("ERROR: ETSY_SHARED_SECRET not found in .env")
    raise SystemExit

BASE_URL = "https://openapi.etsy.com/v3"

headers = {
    "x-api-key": ETSY_KEYSTRING,
    "User-Agent": "RAMFAM-KINGDOM-ATLAS",
}

print("Testing Etsy public API connection...")

ping_response = requests.get(f"{BASE_URL}/public/ping", headers=headers)

print("PING STATUS:", ping_response.status_code)
print("PING RESPONSE:", ping_response.text)

if ping_response.status_code == 200:
    print("ETSY PUBLIC API: SUCCESS")
else:
    print("ETSY PUBLIC API: FAILED")
