import os, requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("META_USER_ACCESS_TOKEN")

r = requests.get(
    "https://graph.facebook.com/v20.0/me/accounts",
    params={"fields": "id,name,access_token", "access_token": token},
    timeout=15
)

print(r.status_code)
print(r.text[:2000])
