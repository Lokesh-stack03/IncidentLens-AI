from backend.app.services.api_executor import execute_api
from types import SimpleNamespace
def test_execute_api_service():
    integration=SimpleNamespace(
        http_method="GET",
        base_url="https://httpbin.org/status/200"
    )
    result=execute_api(integration)
    assert result["success"] is True
    assert result["status_code"] == 200