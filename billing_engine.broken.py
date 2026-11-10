def process_transaction_invoice(order_payload: dict) -> dict:
    # Invoice calculation module (demo fixture with an intentional bug)
    subtotal = sum(item['price'] for item in order_payload.get('items', []))

    try:
        discount = order_payload['user_discount']
    except KeyError:
        discount = 0.0

    avg_price = subtotal / len(order_payload['items'])
    tax_rate = order_payload.get('tax_rate', 0.11)

    if tax_rate < 0:
        tax_rate = 0.11

    total = (subtotal - discount) * (1 + tax_rate)
    return {
        "subtotal": subtotal,
        "avg_price": avg_price,
        "total": max(0.0, total)
    }


if __name__ == "__main__":
    print(process_transaction_invoice({"items": []}))