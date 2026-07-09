# skills/gideon_report.py

from orders.order_skill import load_orders


def generate_gideon_report():
    orders = load_orders()

    report = "🐂 GIDEON MONEY REPORT\n\n"

    if not orders:
        report += "No orders found."
        return report

    paid_total = 0
    outstanding_total = 0

    report += f"Total Orders: {len(orders)}\n\n"

    for order in orders:
        customer = order.get("customer", "Unknown")
        product = order.get("product", "Unknown")
        total = float(order.get("total", 0))
        status = order.get("status", "Unknown")

        report += (
            f"Customer: {customer}\n"
            f"Product: {product}\n"
            f"Amount: ${total:.2f}\n"
            f"Status: {status}\n\n"
        )

        status_lower = status.lower()

        if "paid" in status_lower:
            paid_total += total

        elif (
            "outstanding" in status_lower
            or "invoice" in status_lower
            or "awaiting" in status_lower
            or "unpaid" in status_lower
            or "due" in status_lower
        ):
            outstanding_total += total

    report += "SUMMARY\n\n"
    report += f"Paid Revenue: ${paid_total:.2f}\n"
    report += f"Outstanding Revenue: ${outstanding_total:.2f}\n"

    if outstanding_total > 0:
        report += "\nACTION REQUIRED:\n"
        report += "Follow up on outstanding invoices.\n"

    return report