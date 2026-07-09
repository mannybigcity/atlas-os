import json
import os

ORDERS_FILE = "orders/orders.json"


def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []

    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


# Backward-compatible old name
def load_revenue():
    return load_orders()


def save_orders(orders):
    os.makedirs(os.path.dirname(ORDERS_FILE), exist_ok=True)

    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=2)


# Backward-compatible old name
def save_revenue(items):
    save_orders(items)


def get_amount(order):
    if "total" in order:
        return float(order.get("total", 0))

    if "amount" in order:
        return float(order.get("amount", 0))

    return 0.0


def get_source(order):
    return order.get("product") or order.get("source") or "Unknown Source"


def categorize_revenue_status(status):
    status_text = str(status).lower().strip()

    if any(word in status_text for word in ["paid", "complete", "completed", "collected", "received"]):
        return "paid"

    if any(word in status_text for word in ["outstanding", "invoice", "invoiced", "invoice sent", "awaiting", "awaiting payment", "sent", "due", "unpaid"]):
        return "outstanding"

    if any(word in status_text for word in ["potential", "prospect", "quoted", "quote", "lead", "interested", "pending", "maybe"]):
        return "potential"

    return "potential"


def add_revenue_opportunity(customer, source, amount, status):
    orders = load_orders()

    new_order = {
        "customer": customer,
        "product": source,
        "quantity": 1,
        "total": float(amount),
        "status": status
    }

    orders.append(new_order)
    save_orders(orders)

    return f"Revenue/order added: {customer} | {source} | ${float(amount):.2f} | {status}"


def show_revenue_report():
    orders = load_orders()

    if not orders:
        return "No orders or revenue opportunities saved yet."

    paid_total = 0
    outstanding_total = 0
    potential_total = 0

    paid_count = 0
    outstanding_count = 0
    potential_count = 0

    lines = []

    for order in orders:
        amount = get_amount(order)
        status = order.get("status", "Potential")
        category = categorize_revenue_status(status)

        if category == "paid":
            paid_total += amount
            paid_count += 1
        elif category == "outstanding":
            outstanding_total += amount
            outstanding_count += 1
        else:
            potential_total += amount
            potential_count += 1

        customer = order.get("customer", "Unknown Customer")
        source = get_source(order)

        lines.append(f"{customer} | {source} | ${amount:.2f} | {status}")

    report = "🦇 ALFRED'S UNIFIED MONEY REPORT\n\n"
    report += "SUMMARY\n"
    report += f"Paid Revenue: ${paid_total:.2f} ({paid_count})\n"
    report += f"Outstanding Revenue: ${outstanding_total:.2f} ({outstanding_count})\n"
    report += f"Potential Revenue: ${potential_total:.2f} ({potential_count})\n\n"
    report += "MONEY ITEMS\n"
    report += "\n".join(lines)

    return report