from rules import decide

def create_order(request, state):
    allowed, reason = decide(request, state)
    if not allowed:
        return {"status": "rejected", "reason": reason}
    order_id = len(state["orders"]) + 1
    state["orders"][order_id] = request["qty"]
    state["events"].append(order_id)
    return {"status": "queued", "id": order_id}
