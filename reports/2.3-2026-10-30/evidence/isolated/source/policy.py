def permitted(qty, enabled, limit):
    if not enabled:
        return False, "disabled"
    if qty <= 0 or qty > limit:
        return False, "quantity"
    return True, "ok"
