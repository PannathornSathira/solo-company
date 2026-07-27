from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.contracts.objectives import ObjectiveCreate
from app.repositories import objective_repo
from app.repositories.exceptions import ConflictError, NotFoundError


def test_create_and_get_objective(client: TestClient) -> None:
    payload = {
        "title": "Launch new service",
        "desired_outcome": "Acquire 10 beta customers",
        "context": "Q3 priority",
        "constraints": ["No paid ads"],
    }
    response = client.post("/api/objectives", json=payload)
    assert response.status_code == 201
    objective = response.json()
    assert objective["title"] == "Launch new service"
    assert objective["status"] == "draft"
    assert "id" in objective

    objective_id = objective["id"]
    get_response = client.get(f"/api/objectives/{objective_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == objective_id


def test_list_objectives_newest_first(client: TestClient) -> None:
    client.post(
        "/api/objectives",
        json={"title": "First", "desired_outcome": "Outcome 1"},
    )
    client.post(
        "/api/objectives",
        json={"title": "Second", "desired_outcome": "Outcome 2"},
    )
    response = client.get("/api/objectives")
    assert response.status_code == 200
    objectives = response.json()
    assert len(objectives) == 2
    assert objectives[0]["title"] == "Second"
    assert objectives[1]["title"] == "First"


def test_list_work_items_empty_and_filtering(client: TestClient) -> None:
    response = client.get("/api/work-items")
    assert response.status_code == 200
    assert response.json() == []


def test_objective_state_transition_validation(db_session: Session) -> None:
    create_data = ObjectiveCreate(title="Test", desired_outcome="Outcome")
    objective = objective_repo.create_objective(db_session, create_data)
    assert objective.status == "draft"

    with pytest.raises(ConflictError, match="Cannot transition objective"):
        objective_repo.update_objective_status(
            db_session, objective.id, "completed"
        )


def test_company_id_scoping(db_session: Session) -> None:
    create_data = ObjectiveCreate(title="Scoping", desired_outcome="Test")
    objective = objective_repo.create_objective(db_session, create_data)

    other_company_id = uuid4()
    with pytest.raises(NotFoundError):
        objective_repo.get_objective(
            db_session, objective.id, company_id=other_company_id
        )

    other_objectives = objective_repo.list_objectives(
        db_session, company_id=other_company_id
    )
    assert len(other_objectives) == 0
