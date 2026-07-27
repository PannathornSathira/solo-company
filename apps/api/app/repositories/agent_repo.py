from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.contracts.agents import AgentUpdate
from app.db.models import AgentDefinitionModel, utcnow
from app.repositories.company_repo import DEFAULT_COMPANY_ID, seed_default_company_if_empty
from app.repositories.exceptions import NotFoundError

DEFAULT_AGENTS_DATA = [
    {
        "id": UUID("a1000000-0000-4000-8000-000000000001"),
        "slug": "chief-of-staff",
        "name": "Chief of Staff / Business Strategist",
        "role": "Chief of Staff",
        "objective": "Coordinate specialist agents and synthesize executive briefs.",
        "responsibilities": [
            "Objective intake and validation",
            "Structured plan generation with owners and deliverables",
            "Executive brief synthesis and follow-up recommendations",
        ],
        "runtime_model_alias": "gemini-3.1-pro",
        "prompt_version": "v1.0.0",
        "enabled": True,
    },
    {
        "id": UUID("a2000000-0000-4000-8000-000000000002"),
        "slug": "marketing-specialist",
        "name": "Marketing Specialist",
        "role": "Marketing Specialist",
        "objective": "Create compelling marketing briefs, messaging, and go-to-market assets.",
        "responsibilities": [
            "Market research and competitive positioning",
            "Copywriting and messaging framework design",
            "Launch campaign brief creation",
        ],
        "runtime_model_alias": "gemini-3.1-pro",
        "prompt_version": "v1.0.0",
        "enabled": True,
    },
]


def seed_default_agents_if_empty(
    db: Session, company_id: UUID = DEFAULT_COMPANY_ID
) -> list[AgentDefinitionModel]:
    seed_default_company_if_empty(db)
    existing = list(
        db.scalars(
            select(AgentDefinitionModel).where(
                AgentDefinitionModel.company_id == company_id
            )
        )
    )
    if existing:
        return existing

    agents = []
    for data in DEFAULT_AGENTS_DATA:
        agent = AgentDefinitionModel(
            id=data["id"],
            company_id=company_id,
            slug=data["slug"],
            name=data["name"],
            role=data["role"],
            objective=data["objective"],
            responsibilities=data["responsibilities"],
            runtime_model_alias=data["runtime_model_alias"],
            prompt_version=data["prompt_version"],
            enabled=data["enabled"],
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        db.add(agent)
        agents.append(agent)
    db.commit()
    for agent in agents:
        db.refresh(agent)
    return agents


def list_agents(
    db: Session, company_id: UUID = DEFAULT_COMPANY_ID
) -> list[AgentDefinitionModel]:
    agents = list(
        db.scalars(
            select(AgentDefinitionModel)
            .where(AgentDefinitionModel.company_id == company_id)
            .order_by(AgentDefinitionModel.created_at.asc())
        )
    )
    if not agents and company_id == DEFAULT_COMPANY_ID:
        return seed_default_agents_if_empty(db, company_id=company_id)
    return agents


def get_agent(
    db: Session, agent_id: UUID, company_id: UUID = DEFAULT_COMPANY_ID
) -> AgentDefinitionModel:
    agent = db.scalar(
        select(AgentDefinitionModel).where(
            AgentDefinitionModel.id == agent_id,
            AgentDefinitionModel.company_id == company_id,
        )
    )
    if agent is None:
        raise NotFoundError("Agent profile not found")
    return agent


def update_agent(
    db: Session,
    agent_id: UUID,
    update_data: AgentUpdate,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> AgentDefinitionModel:
    agent = get_agent(db, agent_id=agent_id, company_id=company_id)
    if update_data.name is not None:
        agent.name = update_data.name
    if update_data.role is not None:
        agent.role = update_data.role
    if update_data.objective is not None:
        agent.objective = update_data.objective
    if update_data.responsibilities is not None:
        agent.responsibilities = update_data.responsibilities
    if update_data.runtime_model_alias is not None:
        agent.runtime_model_alias = update_data.runtime_model_alias
    if update_data.prompt_version is not None:
        agent.prompt_version = update_data.prompt_version
    if update_data.enabled is not None:
        agent.enabled = update_data.enabled
    agent.updated_at = utcnow()
    db.commit()
    db.refresh(agent)
    return agent
