import os
import requests
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
CLIENT_ID = os.getenv("SHOPIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SHOPIFY_CLIENT_SECRET")

url = f"https://{SHOPIFY_STORE}/admin/oauth/access_token"

payload = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
}

response = requests.post(url, data=payload)

print("STATUS:", response.status_code)
print("RESPONSE:", response.text[:500])