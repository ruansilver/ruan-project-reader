def consume(state):
    order_id = state["events"].pop(0)
    if order_id not in state["orders"]:
        return "missing"
    state["notices"].append(order_id)
    return "notified"
