import json
import os

ORDERS_FILE = "orders/orders.json"

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []

    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_orders(orders):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=2)

def create_order(customer, product, quantity, total):
    orders = load_orders()

    new_order = {
        "customer": customer,
        "product": product,
        "quantity": quantity,
        "total": total,
        "status": "Awaiting Payment"
    }

    orders.append(new_order)
    save_orders(orders)

    return f"Order created for {customer}."

def show_orders():
    orders = load_orders()

    if not orders:
        return "No orders found."

    lines = []

    for order in orders:
        lines.append(
            f"{order['customer']} | {order['product']} | Qty: {order['quantity']} | ${order['total']} | {order['status']}"
        )

    return "\n".join(lines)