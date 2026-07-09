from dotenv import load_dotenv
import os
import requests

load_dotenv()

SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2025-01"

BASE_URL = f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}"

HEADERS = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    "Content-Type": "application/json",
}


def shopify_get(endpoint, params=None):
    if not SHOPIFY_STORE:
        raise ValueError("SHOPIFY_STORE missing from .env")

    if not SHOPIFY_ACCESS_TOKEN:
        raise ValueError("SHOPIFY_ACCESS_TOKEN missing from .env")

    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        raise Exception(f"Shopify API error {response.status_code}: {response.text}")

    return response.json()


def get_shop_info():
    return shopify_get("shop.json").get("shop", {})


def get_products(limit=10):
    return shopify_get("products.json", {"limit": limit}).get("products", [])


def get_orders(limit=10):
    return shopify_get("orders.json", {"limit": limit, "status": "any"}).get("orders", [])


def get_customers(limit=10):
    return shopify_get("customers.json", {"limit": limit}).get("customers", [])


if __name__ == "__main__":
    print("Testing Shopify Connector...")

    shop = get_shop_info()
    print("SHOP:", shop.get("name"))

    products = get_products()
    print("PRODUCTS:", len(products))
    for product in products:
        print("-", product.get("title"))

    orders = get_orders()
    print("ORDERS:", len(orders))

    customers = get_customers()
    print("CUSTOMERS:", len(customers))

    print("SHOPIFY CONNECTOR: SUCCESS")