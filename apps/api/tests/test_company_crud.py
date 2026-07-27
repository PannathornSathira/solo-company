from fastapi.testclient import TestClient


def test_get_company_seeds_default_company(client: TestClient) -> None:
    response = client.get("/api/company")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "20000000-0000-4000-8000-000000000001"
    assert data["name"] == "Solo Company"
    assert isinstance(data["working_rules"], list)
    assert len(data["working_rules"]) == 1


def test_patch_company_updates_fields(client: TestClient) -> None:
    update_payload = {
        "name": "Acme Autonomous",
        "mission": "Build world-class AI agents.",
        "working_rules": ["Rule 1", "Rule 2"],
    }
    response = client.patch("/api/company", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Acme Autonomous"
    assert data["mission"] == "Build world-class AI agents."
    assert data["working_rules"] == ["Rule 1", "Rule 2"]

    get_response = client.get("/api/company")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Acme Autonomous"


def test_patch_company_validation_error(client: TestClient) -> None:
    response = client.patch("/api/company", json={})
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
