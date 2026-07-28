from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import InMemorySaver
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import Base
from app.db import session as db_session_module
from app.db.session import get_db
from app.main import app
from app.runtime.model_adapters import FakeModelAdapter
from app.runtime.service import RuntimeService


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    old_engine = db_session_module._engine
    old_factory = db_session_module._session_factory

    db_session_module._engine = engine
    db_session_module._session_factory = testing_session_local

    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        db_session_module._engine = old_engine
        db_session_module._session_factory = old_factory


@pytest.fixture(scope="function")
def fake_model() -> FakeModelAdapter:
    return FakeModelAdapter()


@pytest.fixture(scope="function")
def runtime_service(
    db_session: Session, fake_model: FakeModelAdapter
) -> RuntimeService:
    return RuntimeService(
        session_factory=db_session_module.get_session_factory(),
        model_adapter=fake_model,
        checkpointer=InMemorySaver(),
        graph_version="p1-v1",
    )


@pytest.fixture(scope="function")
def client(
    db_session: Session, runtime_service: RuntimeService
) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.state.runtime_service = runtime_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    del app.state.runtime_service
