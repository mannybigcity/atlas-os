from dotenv import load_dotenv
import os
import requests

load_dotenv()

PRINTIFY_API_TOKEN = os.getenv("PRINTIFY_API_TOKEN")
BASE_URL = "https://api.printify.com/v1"

HEADERS = {
    "Authorization": f"Bearer {PRINTIFY_API_TOKEN}",
    "User-Agent": "RAMFAM-KINGDOM-ATLAS",
    "Content-Type": "application/json",
}


def printify_get(endpoint, params=None):
    if not PRINTIFY_API_TOKEN:
        raise ValueError("PRINTIFY_API_TOKEN missing from .env")

    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        raise Exception(f"Printify API error {response.status_code}: {response.text}")

    return response.json()


def get_shops():
    return printify_get("shops.json")


def get_products(shop_id, limit=10):
    data = printify_get(f"shops/{shop_id}/products.json", {"limit": limit})
    return data.get("data", [])


def get_orders(shop_id, limit=10):
    data = printify_get(f"shops/{shop_id}/orders.json", {"limit": limit})
    return data.get("data", [])


if __name__ == "__main__":
    print("Testing Printify Connector...")

    shops = get_shops()
    print("SHOPS:", len(shops))

    for shop in shops:
        shop_id = shop.get("id")
        title = shop.get("title") or "(No title)"
        print(f"\nSHOP: {title} | ID: {shop_id}")

        products = get_products(shop_id)
        print("PRODUCTS:", len(products))
        for product in products:
            print("-", product.get("title"))

        orders = get_orders(shop_id)
        print("ORDERS:", len(orders))

    print("\nPRINTIFY CONNECTOR: SUCCESS")