def calculate_invoice(cart_items, tax_rate, discount_code=None):
    if not isinstance(cart_items, list):
        raise TypeError("cart_items must be a list")
    subtotal = sum(item["price"] * item["qty"] for item in cart_items)
    discount_amount = 0
    if discount_code == "SAVE10":
        discount_amount = subtotal * 0.10
    discounted_subtotal = subtotal - discount_amount
    tax_amount = discounted_subtotal * tax_rate
    total = discounted_subtotal + tax_amount
    return round(total, 2)