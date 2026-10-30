def build_report(request, state):
    return {"requested_by": request["actor"], "count": len(state["orders"])}
