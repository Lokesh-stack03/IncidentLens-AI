def detect_failure(result):
    """
    Analyze the API execution result and determine
    whether the request failed.
    """

    if result["success"]:
        return {"failed": False, "failure_type": None}

    status_code = result.get("status_code")

    if status_code is None:
        return {"failed": True, "failure_type": "NETWORK_ERROR"}

    if 300 <= status_code < 400:
        return {"failed": True, "failure_type": "REDIRECT"}

    if 400 <= status_code < 500:
        return {"failed": True, "failure_type": "CLIENT_ERROR"}

    if 500 <= status_code < 600:
        return {"failed": True, "failure_type": "SERVER_ERROR"}

    return {"failed": True, "failure_type": "UNKNOWN_ERROR"}
