import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("META_USER_ACCESS_TOKEN")
page_id = os.getenv("META_PAGE_ID")

print("META_APP_ID:", "OK" if os.getenv("META_APP_ID") else "MISSING")
print("META_APP_SECRET:", "OK" if os.getenv("META_APP_SECRET") else "MISSING")
print("META_USER_ACCESS_TOKEN:", "OK" if token else "MISSING")
print("META_PAGE_ID:", "OK" if page_id else "MISSING")
print("THREADS_APP_ID:", "OK" if os.getenv("THREADS_APP_ID") else "MISSING")

if not token:
    raise SystemExit("Missing META_USER_ACCESS_TOKEN")

r = requests.get(
    "https://graph.facebook.com/v20.0/me",
    params={"fields": "id,name", "access_token": token},
    timeout=15
)

print("USER TEST:", r.status_code, r.text[:500])

if page_id:
    r2 = requests.get(
        f"https://graph.facebook.com/v20.0/{page_id}",
        params={"fields": "id,name", "access_token": token},
        timeout=15
    )
    print("PAGE TEST:", r2.status_code, r2.text[:500])
print("\n=== MANAGED PAGES ===")

r3 = requests.get(
    "https://graph.facebook.com/v20.0/me/accounts",
    params={"access_token": token},
    timeout=15
)

data = r3.json()

print("ACCOUNTS TEST:", r3.status_code)

atlas_found = False

for page in data.get("data", []):
    if page.get("name") == "ATLAS for Entrepreneurs":
        atlas_found = True
        print("\n===== ATLAS PAGE FOUND =====")
        print("PAGE NAME:", page.get("name"))
        print("PAGE ID:", page.get("id"))
        print("PAGE ACCESS TOKEN FOUND:", "YES" if page.get("access_token") else "NO")
        print("PAGE ACCESS TOKEN:", page.get("access_token"))
        print("============================")
        break

if not atlas_found:
    print("ATLAS for Entrepreneurs page was not found.")