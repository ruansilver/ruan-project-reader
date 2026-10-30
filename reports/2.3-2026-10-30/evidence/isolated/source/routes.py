from service import create_order

ROUTES = {"POST /orders": "submit", "POST /reports": "report"}

def submit(request, state):
    return create_order(request, state)

def report(request, state):
    from reporting import build_report
    return build_report(request, state)
