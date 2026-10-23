import requests


def execute_api(integration):
    """
    Execute an HTTP request using the configured Integration.
    """
    # Think of it like a package containing the API server's reply.
    try:
        response = requests.request(
            method=integration.http_method, url=integration.base_url, timeout=10
        )

        return {
            "success": 200 <= response.status_code < 300,
            "status_code": response.status_code,
            "response": response.text,
        }
    # If the API request takes longer than the allowed timeout, execute this code.
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "status_code": None,  # We don't have a status code.
            "error": "Request timed out",
        }
    # This handles connection problems.
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "status_code": None,
            "error": "Unable to connect to the API",
        }
    # This catches other exceptions related to the requests library.
    except requests.exceptions.RequestException as e:
        return {"success": False, "status_code": None, "error": str(e)}
