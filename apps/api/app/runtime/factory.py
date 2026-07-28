import os
from contextlib import AbstractContextManager
from typing import Any

from langgraph.checkpoint.postgres import PostgresSaver

from app.config import Settings
from app.db.session import get_session_factory
from app.runtime.model_adapters import (
    FakeModelAdapter,
    GeminiModelAdapter,
    ModelAdapter,
)
from app.runtime.service import RuntimeService


def build_model_adapter(settings: Settings) -> ModelAdapter:
    if settings.runtime_model_backend == "fake":
        return FakeModelAdapter()
    if settings.runtime_model_backend == "gemini":
        return GeminiModelAdapter(
            api_key=settings.gemini_api_key or "",
            model_id=settings.gemini_model_id,
        )
    raise ValueError(
        f"Unsupported RUNTIME_MODEL_BACKEND '{settings.runtime_model_backend}'"
    )


def create_production_runtime(
    settings: Settings,
) -> tuple[RuntimeService, AbstractContextManager[Any]]:
    os.environ.setdefault("LANGGRAPH_STRICT_MSGPACK", "true")
    checkpoint_context = PostgresSaver.from_conn_string(
        settings.langgraph_database_url
    )
    checkpointer = checkpoint_context.__enter__()
    try:
        checkpointer.setup()
        service = RuntimeService(
            session_factory=get_session_factory(),
            model_adapter=build_model_adapter(settings),
            checkpointer=checkpointer,
            graph_version=settings.graph_version,
        )
    except Exception:
        checkpoint_context.__exit__(None, None, None)
        raise
    return service, checkpoint_context
