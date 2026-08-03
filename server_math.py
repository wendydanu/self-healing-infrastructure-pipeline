def compute_rate(total, count):
    if count == 0:
        return 0.0  # Return 0.0 to represent no rate when count is zero, preventing ZeroDivisionError.
    return total / count