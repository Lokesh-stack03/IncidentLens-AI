from backend.app.services.failure_detector import detect_failure


def test_success_response():
    result = {"success": True, "status_code": 200}

    output = detect_failure(result)

    assert output["failed"] is False
    assert output["failure_type"] is None


def test_client_error():
    result = {"success": False, "status_code": 404}

    output = detect_failure(result)

    assert output["failed"] is True
    assert output["failure_type"] == "CLIENT_ERROR"


def test_server_error():
    result = {"success": False, "status_code": 500}

    output = detect_failure(result)

    assert output["failed"] is True
    assert output["failure_type"] == "SERVER_ERROR"


def test_redirect():
    result = {"success": False, "status_code": 302}

    output = detect_failure(result)

    assert output["failed"] is True
    assert output["failure_type"] == "REDIRECT"


def test_network_error():
    result = {"success": False, "status_code": None}

    output = detect_failure(result)

    assert output["failed"] is True
    assert output["failure_type"] == "NETWORK_ERROR"
