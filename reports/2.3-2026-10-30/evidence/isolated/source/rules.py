from policy import permitted

def decide(request, state):
    return permitted(request["qty"], state["enabled"], state["limit"])
