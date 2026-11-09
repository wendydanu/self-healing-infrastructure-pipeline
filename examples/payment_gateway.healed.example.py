def process_checkout(cart_items: list, discount_code: str = None) -> dict:
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)

    # Patch: Handle ZeroDivisionError for an empty cart_items list
    if len(cart_items) > 0:
        average_item_price = total_amount / len(cart_items)
    else:
        average_item_price = 0.0  # Set average to 0.0 if there are no items

    # Initialize discount to prevent NameError if the discount_code is not "PROMO2026"
    discount = 0.0

    if discount_code == "PROMO2026":
        discount = total_amount * 0.20

    final_amount = total_amount - discount
    return {
        "status": "SUCCESS",
        "total_amount": final_amount,
        "average_item_price": average_item_price
    }

if __name__ == "__main__":
    result = process_checkout(cart_items=[], discount_code="INVALID_CODE")
    print("Checkout Result:", result)