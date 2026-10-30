def save(qty, enabled, limit, rows):
    if not enabled:
        return "disabled"
    if qty <= 0 or qty > limit:
        return "quantity"
    rows.append(qty)
    return "saved"
