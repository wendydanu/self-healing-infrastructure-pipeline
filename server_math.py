def calculate_server_ratio(total_users, active_users):
    if active_users == 0:
        return 0.0  # Handle division by zero by returning 0.0 or raising an appropriate error
    ratio = total_users / active_users
    return ratio