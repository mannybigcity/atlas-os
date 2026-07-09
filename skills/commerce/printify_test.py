from dotenv import load_dotenv
import os
import requests

load_dotenv()

PRINTIFY_API_TOKEN = os.getenv("PRINTIFY_API_TOKEN")

if not PRINTIFY_API_TOKEN:
    print("ERROR: PRINTIFY_API_TOKEN not found in .env")
    raise SystemExit

BASE_URL = "https://api.printify.com/v1"

headers = {
    "Authorization": f"Bearer {PRINTIFY_API_TOKEN}",
    "User-Agent": "RAMFAM-KINGDOM-ATLAS",
    "Content-Type": "application/json",
}

print("Testing Printify connection...")

# Step 1: Get shops
shops_response = requests.get(f"{BASE_URL}/shops.json", headers=headers)

print("SHOP STATUS:", shops_response.status_code)

if shops_response.status_code != 200:
    print("Printify connection failed.")
    print(shops_response.text)
    raise SystemExit

shops = shops_response.json()

print("PRINTIFY CONNECTION: SUCCESS")
print("SHOPS FOUND:", len(shops))

for shop in shops:
    print(f"- Shop ID: {shop.get('id')} | Title: {shop.get('title')}")

# Step 2: Get products from first shop
if not shops:
    print("No Printify shops found.")
    raise SystemExit

shop_id = shops[0]["id"]

print("\nTesting products for first shop...")
products_response = requests.get(
    f"{BASE_URL}/shops/{shop_id}/products.json",
    headers=headers
)

print("PRODUCT STATUS:", products_response.status_code)

if products_response.status_code != 200:
    print("Product lookup failed.")
    print(products_response.text)
    raise SystemExit

products_data = products_response.json()
products = products_data.get("data", [])

print("PRODUCT LOOKUP: SUCCESS")
print("PRODUCTS FOUND:", len(products))

for product in products[:10]:
    print(f"- {product.get('title')} | ID: {product.get('id')}")