from dotenv import load_dotenv
import os
import requests

load_dotenv()

SHOPIFY_STORE = os.getenv("SHOPIFY_STORE", "fresh-apparel-and-design.myshopify.com")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

if not SHOPIFY_ACCESS_TOKEN:
    print("ERROR: SHOPIFY_ACCESS_TOKEN not found in .env")
    raise SystemExit

API_VERSION = "2025-01"
BASE_URL = f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}"

headers = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    "Content-Type": "application/json",
}

print("Testing Shopify connection...")

shop_response = requests.get(f"{BASE_URL}/shop.json", headers=headers)

print("SHOP STATUS:", shop_response.status_code)

if shop_response.status_code != 200:
    print("SHOPIFY CONNECTION: FAILED")
    print(shop_response.text)
    raise SystemExit

shop_data = shop_response.json().get("shop", {})

print("SHOPIFY CONNECTION: SUCCESS")
print("SHOP NAME:", shop_data.get("name"))
print("SHOP DOMAIN:", shop_data.get("domain"))
print("SHOP EMAIL:", shop_data.get("email"))

print("\nTesting products...")

products_response = requests.get(
    f"{BASE_URL}/products.json",
    headers=headers,
    params={"limit": 10}
)

print("PRODUCT STATUS:", products_response.status_code)

if products_response.status_code != 200:
    print("PRODUCT LOOKUP: FAILED")
    print(products_response.text)
    raise SystemExit

products = products_response.json().get("products", [])

print("PRODUCT LOOKUP: SUCCESS")
print("PRODUCTS FOUND:", len(products))

for product in products:
    print(f"- {product.get('title')} | ID: {product.get('id')}")