import json
import os

INVOICES_FILE = "memory/invoices.json"


def _ensure_file():
    os.makedirs("memory", exist_ok=True)

    if not os.path.exists(INVOICES_FILE):
        with open(INVOICES_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)


def _load_invoices():
    _ensure_file()

    with open(INVOICES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def _save_invoices(invoices):
    with open(INVOICES_FILE, "w", encoding="utf-8") as file:
        json.dump(invoices, file, indent=4)


def add_invoice(customer, amount, status="Awaiting Payment"):
    invoices = _load_invoices()

    invoice = {
        "id": len(invoices) + 1,
        "customer": customer,
        "amount": amount,
        "status": status
    }

    invoices.append(invoice)
    _save_invoices(invoices)

    return invoice


def list_invoices():
    return _load_invoices()


def outstanding_revenue():
    invoices = _load_invoices()

    total = 0

    for invoice in invoices:
        if invoice["status"] != "Paid":
            total += invoice["amount"]

    return total