from fastapi.testclient import TestClient


def test_list_agents_seeds_default_agents(client: TestClient) -> None:
    response = client.get("/api/agents")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) == 2
    slugs = {agent["slug"] for agent in agents}
    assert slugs == {"chief-of-staff", "marketing-specialist"}


def test_get_agent_by_id(client: TestClient) -> None:
    client.get("/api/agents")
    response = client.get("/api/agents/a1000000-0000-4000-8000-000000000001")
    assert response.status_code == 200
    agent = response.json()
    assert agent["slug"] == "chief-of-staff"
    assert agent["enabled"] is True


def test_get_agent_not_found(client: TestClient) -> None:
    response = client.get("/api/agents/00000000-0000-0000-0000-000000000404")
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == "NOT_FOUND"


def test_patch_agent_updates_fields(client: TestClient) -> None:
    client.get("/api/agents")
    update_payload = {
        "role": "Executive Chief of Staff",
        "enabled": False,
    }
    response = client.patch(
        "/api/agents/a1000000-0000-4000-8000-000000000001", json=update_payload
    )
    assert response.status_code == 200
    agent = response.json()
    assert agent["role"] == "Executive Chief of Staff"
    assert agent["enabled"] is False

    get_response = client.get("/api/agents/a1000000-0000-4000-8000-000000000001")
    assert get_response.json()["enabled"] is False
