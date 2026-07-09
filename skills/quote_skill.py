def create_quote(customer, product, quantity, price_each):
    quantity = int(quantity)
    price_each = float(price_each)
    total = quantity * price_each

    return f"""
QUOTE

Customer: {customer}
Product: {product}
Quantity: {quantity}
Price Each: ${price_each:.2f}

Total: ${total:.2f}
"""