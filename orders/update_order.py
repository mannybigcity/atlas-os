from orders.order_skill import load_orders, save_orders

def update_order_status(customer, new_status):
    orders = load_orders()

    updated_count = 0

    for order in orders:
        if order["customer"].lower() == customer.lower():
            order["status"] = new_status
            updated_count += 1

    if updated_count == 0:
        return f"No order found for {customer}."

    save_orders(orders)

    return f"Updated {updated_count} order(s) for {customer} to status: {new_status}"