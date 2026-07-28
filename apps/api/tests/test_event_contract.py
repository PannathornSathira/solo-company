import json
from pathlib import Path
from typing import get_args

import pytest
import yaml
from fastapi.openapi.models import OpenAPI
from pydantic import ValidationError

from app.contracts.events import EventType, MAX_EVENT_PAYLOAD_BYTES, RunEvent
from app.main import app

FIXTURE = Path(__file__).parent / "fixtures" / "run-event.json"
OPENAPI = Path(__file__).parents[3] / "contracts" / "openapi.yaml"


def test_fake_event_fixture_matches_contract() -> None:
    event = RunEvent.model_validate_json(FIXTURE.read_text())

    assert event.event_type == "artifact.created"
    assert event.summary == "Created marketing brief"

    data = json.loads(FIXTURE.read_text())
    data["payload_json"] = {"content": "x" * (MAX_EVENT_PAYLOAD_BYTES + 1)}
    with pytest.raises(ValidationError, match="payload_json exceeds"):
        RunEvent.model_validate(data)


def test_openapi_and_runtime_event_types_match() -> None:
    document = yaml.safe_load(OPENAPI.read_text())

    OpenAPI.model_validate(document)
    assert set(document["components"]["schemas"]["EventType"]["enum"]) == set(
        get_args(EventType)
    )


def test_runtime_operations_match_approved_openapi_contract() -> None:
    approved = yaml.safe_load(OPENAPI.read_text())
    generated = app.openapi()
    operations = {
        ("/api/objectives/{objective_id}/plan", "post"),
        ("/api/objectives/{objective_id}/plan/revise", "post"),
        ("/api/objectives/{objective_id}/plan/approve", "post"),
        ("/api/runs/{run_id}", "get"),
        ("/api/runs/{run_id}/events", "get"),
        ("/api/runs/{run_id}/artifacts", "get"),
    }
    for path, method in operations:
        assert generated["paths"][path][method]["operationId"] == (
            approved["paths"][path][method]["operationId"]
        )
