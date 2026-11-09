def reserve_stock(item_id: str, current_stock: int, quantity_requested: int) -> dict:
    """
    Simulates stock reservation for high-demand checkout events.
    BUG: Triggers an unhandled TypeError when remaining stock drops to zero,
    causing checkout failures during inventory exhaustion.
    """
    if quantity_requested > current_stock:
        raise ValueError(f"Insufficient stock for item {item_id}. Available: {current_stock}")

    remaining_stock = current_stock - quantity_requested

    # CRITICAL BUG: Type mismatch error during string concatenation
    if remaining_stock == 0:
        warning_msg = "STOCK_EXHAUSTED_" + str(remaining_stock)
        print(warning_msg)

    return {
        "status": "SUCCESS",
        "item_id": item_id,
        "reserved_qty": quantity_requested,
        "remaining_stock": remaining_stock
    }

if __name__ == "__main__":
    print("Testing Inventory Reservation Service...")
    result = reserve_stock(item_id="PROD-8821", current_stock=5, quantity_requested=5)
    print(f"Reservation Result: {result}")