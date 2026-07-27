from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.contracts.agents import AgentDefinition, AgentUpdate
from app.db.session import get_db
from app.repositories import agent_repo

router = APIRouter(tags=["agents"])


@router.get(
    "/api/agents",
    response_model=list[AgentDefinition],
    operation_id="listAgents",
    summary="List fixed agent profiles",
)
def list_agents(db: Session = Depends(get_db)) -> list[AgentDefinition]:
    agents = agent_repo.list_agents(db)
    return [AgentDefinition.model_validate(agent) for agent in agents]


@router.get(
    "/api/agents/{agent_id}",
    response_model=AgentDefinition,
    operation_id="getAgent",
    summary="Get agent profile",
)
def get_agent(
    agent_id: UUID, db: Session = Depends(get_db)
) -> AgentDefinition:
    agent = agent_repo.get_agent(db, agent_id=agent_id)
    return AgentDefinition.model_validate(agent)


@router.patch(
    "/api/agents/{agent_id}",
    response_model=AgentDefinition,
    operation_id="updateAgent",
    summary="Update agent profile",
)
def update_agent(
    agent_id: UUID, update_data: AgentUpdate, db: Session = Depends(get_db)
) -> AgentDefinition:
    agent = agent_repo.update_agent(db, agent_id=agent_id, update_data=update_data)
    return AgentDefinition.model_validate(agent)
