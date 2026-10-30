def save(store, value, allowed):
    if not allowed:
        raise PermissionError("denied")
    store.append(value)
    return value
