from collections.abc import Callable
from typing import Any, Literal, TypedDict
from uuid import UUID

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from sqlalchemy.orm import Session

from app.contracts.runtime import AgentRun, Plan
from app.contracts.work_items import WorkItem
from app.db.models import AgentDefinitionModel
from app.repositories import (
    agent_repo,
    artifact_repo,
    company_repo,
    event_repo,
    objective_repo,
    run_repo,
    work_item_repo,
)
from app.repositories.exceptions import ConflictError
from app.runtime.contracts import ArtifactDraft, PlanDraft
from app.runtime.model_adapters import ModelAdapter, ModelAdapterError
from app.runtime.prompts import (
    PromptLoader,
    PromptNotFoundError,
    PromptRenderError,
)

SPECIALIST_SLUGS = ("marketing-specialist", "operations-manager")


class RuntimeState(TypedDict, total=False):
    company_id: str
    objective_id: str
    run_id: str
    decision: str
    revision_feedback: str
    current_work_item_id: str | None
    pending_artifact: dict[str, Any] | None
    error_code: str | None


RouteAfterPlan = Literal["wait_for_plan_approval", "fail"]
RouteAfterApproval = Literal[
    "create_plan", "execute_next_work_item", "fail"
]
RouteAfterWork = Literal[
    "persist_artifact", "synthesize_executive_brief", "fail"
]
RouteAfterBrief = Literal["complete", "fail"]


class RuntimeService:
    def __init__(
        self,
        *,
        session_factory: Callable[[], Session],
        model_adapter: ModelAdapter,
        checkpointer: BaseCheckpointSaver,
        graph_version: str,
        prompt_loader: PromptLoader | None = None,
    ) -> None:
        self.session_factory = session_factory
        self.model_adapter = model_adapter
        self.graph_version = graph_version
        self.prompt_loader = prompt_loader or PromptLoader()
        self.graph = self._build_graph(checkpointer)

    def _build_graph(self, checkpointer: BaseCheckpointSaver):
        builder = StateGraph(RuntimeState)
        builder.add_node("intake", self._intake)
        builder.add_node("validate_objective", self._validate_objective)
        builder.add_node("create_plan", self._create_plan)
        builder.add_node(
            "wait_for_plan_approval", self._wait_for_plan_approval
        )
        builder.add_node(
            "execute_next_work_item", self._execute_next_work_item
        )
        builder.add_node("persist_artifact", self._persist_artifact)
        builder.add_node(
            "synthesize_executive_brief",
            self._synthesize_executive_brief,
        )
        builder.add_node("complete", self._complete)
        builder.add_node("fail", self._fail)

        builder.add_edge(START, "intake")
        builder.add_edge("intake", "validate_objective")
        builder.add_edge("validate_objective", "create_plan")
        builder.add_conditional_edges(
            "create_plan",
            self._route_after_plan,
            {
                "wait_for_plan_approval": "wait_for_plan_approval",
                "fail": "fail",
            },
        )
        builder.add_conditional_edges(
            "wait_for_plan_approval",
            self._route_after_approval,
            {
                "create_plan": "create_plan",
                "execute_next_work_item": "execute_next_work_item",
                "fail": "fail",
            },
        )
        builder.add_conditional_edges(
            "execute_next_work_item",
            self._route_after_work,
            {
                "persist_artifact": "persist_artifact",
                "synthesize_executive_brief": "synthesize_executive_brief",
                "fail": "fail",
            },
        )
        builder.add_edge("persist_artifact", "execute_next_work_item")
        builder.add_conditional_edges(
            "synthesize_executive_brief",
            self._route_after_brief,
            {"complete": "complete", "fail": "fail"},
        )
        builder.add_edge("complete", END)
        builder.add_edge("fail", END)
        return builder.compile(
            checkpointer=checkpointer,
            name=self.graph_version,
        )

    @staticmethod
    def _config(run_id: UUID) -> dict[str, dict[str, str]]:
        return {"configurable": {"thread_id": str(run_id)}}

    @staticmethod
    def _uuid(state: RuntimeState, key: str) -> UUID:
        return UUID(state[key])

    def create_plan(self, objective_id: UUID) -> Plan:
        with self.session_factory() as db:
            objective = objective_repo.get_objective(db, objective_id)
            run = run_repo.create_run(
                db,
                objective_id=objective.id,
                graph_version=self.graph_version,
                company_id=objective.company_id,
            )
            run_id = run.id
            company_id = run.company_id
            run_objective_id = run.objective_id
            event_repo.append_event(
                db,
                run_id=run_id,
                event_type="run.created",
                summary=f"Created run for objective: {objective.title}",
                payload_json={"objective_id": str(objective.id)},
                company_id=company_id,
            )

        self.graph.invoke(
            {
                "company_id": str(company_id),
                "objective_id": str(run_objective_id),
                "run_id": str(run_id),
                "revision_feedback": "",
                "pending_artifact": None,
                "current_work_item_id": None,
                "error_code": None,
            },
            self._config(run_id),
        )
        with self.session_factory() as db:
            persisted_run = run_repo.get_run(
                db, run_id, company_id=company_id
            )
            if persisted_run.status == "failed":
                raise ConflictError(
                    "Plan generation failed",
                    code=persisted_run.error_code or "PLAN_GENERATION_FAILED",
                )
            if persisted_run.status != "awaiting_approval":
                raise ConflictError("Plan did not reach owner approval")
            return self._load_plan(db, persisted_run.objective_id)

    def revise_plan(self, objective_id: UUID, feedback: str) -> Plan:
        with self.session_factory() as db:
            run = run_repo.get_awaiting_approval_run(db, objective_id)
            company_id = run.company_id

        self.graph.invoke(
            Command(resume={"action": "revise", "feedback": feedback}),
            self._config(run.id),
        )
        with self.session_factory() as db:
            persisted_run = run_repo.get_run(
                db, run.id, company_id=company_id
            )
            if persisted_run.status == "failed":
                raise ConflictError(
                    "Plan revision failed",
                    code=persisted_run.error_code or "PLAN_GENERATION_FAILED",
                )
            return self._load_plan(db, objective_id)

    def approve_plan(
        self, objective_id: UUID, idempotency_key: str
    ) -> AgentRun:
        with self.session_factory() as db:
            existing = run_repo.get_run_by_idempotency_key(
                db,
                objective_id=objective_id,
                idempotency_key=idempotency_key,
            )
            if existing is not None:
                return AgentRun.model_validate(existing)
            run = run_repo.claim_approval(
                db,
                objective_id=objective_id,
                idempotency_key=idempotency_key,
            )
            company_id = run.company_id

        self.graph.invoke(
            Command(resume={"action": "approve"}),
            self._config(run.id),
        )
        with self.session_factory() as db:
            persisted_run = run_repo.get_run(
                db, run.id, company_id=company_id
            )
            return AgentRun.model_validate(persisted_run)

    @staticmethod
    def _load_plan(db: Session, objective_id: UUID) -> Plan:
        items = work_item_repo.list_work_items(
            db, objective_id=objective_id
        )
        return Plan(
            objective_id=objective_id,
            work_items=[WorkItem.model_validate(item) for item in items],
        )

    def _intake(self, state: RuntimeState) -> RuntimeState:
        return {
            "decision": "",
            "current_work_item_id": None,
            "pending_artifact": None,
        }

    def _validate_objective(self, state: RuntimeState) -> RuntimeState:
        company_id = self._uuid(state, "company_id")
        objective_id = self._uuid(state, "objective_id")
        try:
            with self.session_factory() as db:
                objective = objective_repo.get_objective(
                    db, objective_id, company_id=company_id
                )
                if objective.status not in {"draft", "planning"}:
                    return {"error_code": "INVALID_OBJECTIVE_STATE"}
                chief = agent_repo.get_agent_by_slug(
                    db, "chief-of-staff", company_id=company_id
                )
                specialists = self._enabled_specialists(db, company_id)
                if not chief.enabled or len(specialists) != len(
                    SPECIALIST_SLUGS
                ):
                    return {"error_code": "AGENT_CONFIGURATION_INVALID"}
        except Exception:
            return {"error_code": "OBJECTIVE_VALIDATION_FAILED"}
        return {"error_code": None}

    def _create_plan(self, state: RuntimeState) -> RuntimeState:
        if state.get("error_code"):
            return {}
        company_id = self._uuid(state, "company_id")
        objective_id = self._uuid(state, "objective_id")
        run_id = self._uuid(state, "run_id")
        try:
            with self.session_factory() as db:
                company = company_repo.get_company(db, company_id)
                objective = objective_repo.get_objective(
                    db, objective_id, company_id=company_id
                )
                chief = agent_repo.get_agent_by_slug(
                    db, "chief-of-staff", company_id=company_id
                )
                specialists = self._enabled_specialists(db, company_id)
                objective_repo.update_objective_status(
                    db, objective_id, "planning", company_id=company_id
                )
                prompt = self.prompt_loader.render(
                    chief.prompt_version,
                    "chief_of_staff_plan",
                    company_name=company.name,
                    company_mission=company.mission,
                    working_rules=company.working_rules,
                    agent_objective=chief.objective,
                    agent_responsibilities=chief.responsibilities,
                    objective_title=objective.title,
                    desired_outcome=objective.desired_outcome,
                    objective_context=objective.context,
                    objective_constraints=objective.constraints,
                    revision_feedback=state.get("revision_feedback") or "None",
                    specialists=[
                        {
                            "slug": agent.slug,
                            "name": agent.name,
                            "role": agent.role,
                            "objective": agent.objective,
                            "responsibilities": agent.responsibilities,
                        }
                        for agent in specialists
                    ],
                )
                plan = self.model_adapter.propose_plan(
                    prompt=prompt,
                    model_alias=chief.runtime_model_alias,
                    specialist_slugs=[agent.slug for agent in specialists],
                )
                agents_by_slug = {agent.slug: agent for agent in specialists}
                self._validate_plan_assignments(plan, set(agents_by_slug))
                work_items = work_item_repo.replace_proposed_work_items(
                    db,
                    objective_id=objective_id,
                    plan=plan,
                    agents_by_slug=agents_by_slug,
                    company_id=company_id,
                )
                objective_repo.update_objective_status(
                    db,
                    objective_id,
                    "awaiting_approval",
                    company_id=company_id,
                )
                run_repo.update_run_status(
                    db,
                    run_id,
                    "awaiting_approval",
                    company_id=company_id,
                )
                event_repo.append_event(
                    db,
                    run_id=run_id,
                    event_type="plan.proposed",
                    summary=(
                        f"Chief of Staff proposed {len(work_items)} "
                        "sequential work items"
                    ),
                    payload_json={"work_items_count": len(work_items)},
                    company_id=company_id,
                )
        except PromptNotFoundError:
            return {"error_code": "PROMPT_VERSION_NOT_FOUND"}
        except (PromptRenderError, ModelAdapterError):
            return {"error_code": "PLAN_GENERATION_FAILED"}
        except Exception:
            return {"error_code": "PLAN_PERSISTENCE_FAILED"}
        return {
            "error_code": None,
            "decision": "",
            "pending_artifact": None,
        }

    def _wait_for_plan_approval(
        self, state: RuntimeState
    ) -> RuntimeState:
        response = interrupt(
            {
                "run_id": state["run_id"],
                "objective_id": state["objective_id"],
                "status": "awaiting_approval",
            }
        )
        if not isinstance(response, dict):
            return {"error_code": "INVALID_APPROVAL_DECISION"}
        action = response.get("action")
        company_id = self._uuid(state, "company_id")
        objective_id = self._uuid(state, "objective_id")
        run_id = self._uuid(state, "run_id")
        if action == "revise":
            feedback = response.get("feedback")
            if (
                not isinstance(feedback, str)
                or not feedback.strip()
                or len(feedback) > 4000
            ):
                return {"error_code": "INVALID_REVISION_FEEDBACK"}
            with self.session_factory() as db:
                event_repo.append_event(
                    db,
                    run_id=run_id,
                    event_type="plan.revision_requested",
                    summary="Owner requested a plan revision",
                    payload_json={"feedback_length": len(feedback)},
                    company_id=company_id,
                )
                objective_repo.update_objective_status(
                    db, objective_id, "planning", company_id=company_id
                )
                run_repo.update_run_status(
                    db,
                    run_id,
                    "pending",
                    company_id=company_id,
                )
            return {
                "decision": "revise",
                "revision_feedback": feedback.strip(),
                "error_code": None,
            }
        if action == "approve":
            try:
                with self.session_factory() as db:
                    work_item_repo.approve_work_items(
                        db,
                        objective_id=objective_id,
                        company_id=company_id,
                    )
                    objective_repo.update_objective_status(
                        db,
                        objective_id,
                        "approved",
                        company_id=company_id,
                    )
                    objective_repo.update_objective_status(
                        db,
                        objective_id,
                        "running",
                        company_id=company_id,
                    )
                    run_repo.update_run_status(
                        db,
                        run_id,
                        "running",
                        company_id=company_id,
                    )
                    event_repo.append_event(
                        db,
                        run_id=run_id,
                        event_type="plan.approved",
                        summary="Owner approved the sequential work plan",
                        payload_json={"approved_by": "owner"},
                        company_id=company_id,
                    )
            except Exception:
                return {"error_code": "PLAN_APPROVAL_FAILED"}
            return {"decision": "approve", "error_code": None}
        return {"error_code": "INVALID_APPROVAL_DECISION"}

    def _execute_next_work_item(
        self, state: RuntimeState
    ) -> RuntimeState:
        company_id = self._uuid(state, "company_id")
        objective_id = self._uuid(state, "objective_id")
        run_id = self._uuid(state, "run_id")
        with self.session_factory() as db:
            work_item = work_item_repo.get_next_approved_work_item(
                db,
                objective_id=objective_id,
                company_id=company_id,
            )
            if work_item is None:
                return {
                    "current_work_item_id": None,
                    "pending_artifact": None,
                    "error_code": None,
                }
            work_item_repo.update_work_item_status(
                db,
                work_item.id,
                "running",
                company_id=company_id,
            )
            agent = agent_repo.get_agent(
                db, work_item.assigned_agent_id, company_id=company_id
            )
            objective = objective_repo.get_objective(
                db, objective_id, company_id=company_id
            )
            company = company_repo.get_company(db, company_id)
            prior_artifacts = artifact_repo.list_run_artifacts(
                db, run_id=run_id, company_id=company_id
            )
            event_repo.append_event(
                db,
                run_id=run_id,
                event_type="work.started",
                summary=f"{agent.name} started: {work_item.title}",
                payload_json={
                    "work_item_id": str(work_item.id),
                    "assigned_agent_id": str(agent.id),
                    "position": work_item.position,
                },
                company_id=company_id,
            )
            try:
                prompt = self.prompt_loader.render(
                    agent.prompt_version,
                    "specialist_work",
                    agent_name=agent.name,
                    agent_role=agent.role,
                    company_name=company.name,
                    company_mission=company.mission,
                    working_rules=company.working_rules,
                    agent_objective=agent.objective,
                    agent_responsibilities=agent.responsibilities,
                    work_item_title=work_item.title,
                    work_item_instructions=work_item.instructions,
                    deliverable_type=work_item.deliverable_type,
                    objective_context={
                        "title": objective.title,
                        "desired_outcome": objective.desired_outcome,
                        "context": objective.context,
                        "constraints": objective.constraints,
                    },
                    prior_artifacts=[
                        {
                            "title": artifact.title,
                            "artifact_type": artifact.artifact_type,
                            "content_markdown": artifact.content_markdown,
                        }
                        for artifact in prior_artifacts
                    ],
                )
                draft = self.model_adapter.execute_work_item(
                    prompt=prompt,
                    model_alias=agent.runtime_model_alias,
                    agent_name=agent.name,
                    work_item_title=work_item.title,
                    deliverable_type=work_item.deliverable_type,
                )
            except PromptNotFoundError:
                return self._mark_work_failed(
                    db,
                    work_item.id,
                    run_id,
                    company_id,
                    "PROMPT_VERSION_NOT_FOUND",
                )
            except (PromptRenderError, ModelAdapterError):
                return self._mark_work_failed(
                    db,
                    work_item.id,
                    run_id,
                    company_id,
                    "SPECIALIST_EXECUTION_FAILED",
                )
            except Exception:
                return self._mark_work_failed(
                    db,
                    work_item.id,
                    run_id,
                    company_id,
                    "SPECIALIST_EXECUTION_FAILED",
                )
            return {
                "current_work_item_id": str(work_item.id),
                "pending_artifact": draft.model_dump(mode="json"),
                "error_code": None,
            }

    def _persist_artifact(self, state: RuntimeState) -> RuntimeState:
        company_id = self._uuid(state, "company_id")
        run_id = self._uuid(state, "run_id")
        work_item_id = self._uuid(state, "current_work_item_id")
        try:
            draft = ArtifactDraft.model_validate(state["pending_artifact"])
            with self.session_factory() as db:
                work_item = work_item_repo.get_work_item(
                    db, work_item_id, company_id=company_id
                )
                artifact = artifact_repo.create_artifact(
                    db,
                    run_id=run_id,
                    work_item_id=work_item_id,
                    draft=draft,
                    company_id=company_id,
                )
                event_repo.append_event(
                    db,
                    run_id=run_id,
                    event_type="artifact.created",
                    summary=f"Created artifact: {artifact.title}",
                    payload_json={
                        "artifact_id": str(artifact.id),
                        "work_item_id": str(work_item_id),
                        "artifact_type": artifact.artifact_type,
                    },
                    company_id=company_id,
                )
                work_item_repo.update_work_item_status(
                    db, work_item_id, "done", company_id=company_id
                )
                event_repo.append_event(
                    db,
                    run_id=run_id,
                    event_type="work.completed",
                    summary=f"Completed work item: {work_item.title}",
                    payload_json={
                        "work_item_id": str(work_item_id),
                        "artifact_id": str(artifact.id),
                    },
                    company_id=company_id,
                )
        except Exception:
            with self.session_factory() as db:
                return self._mark_work_failed(
                    db,
                    work_item_id,
                    run_id,
                    company_id,
                    "ARTIFACT_PERSISTENCE_FAILED",
                )
        return {
            "current_work_item_id": None,
            "pending_artifact": None,
            "error_code": None,
        }

    def _synthesize_executive_brief(
        self, state: RuntimeState
    ) -> RuntimeState:
        company_id = self._uuid(state, "company_id")
        objective_id = self._uuid(state, "objective_id")
        run_id = self._uuid(state, "run_id")
        try:
            with self.session_factory() as db:
                company = company_repo.get_company(db, company_id)
                objective = objective_repo.get_objective(
                    db, objective_id, company_id=company_id
                )
                chief = agent_repo.get_agent_by_slug(
                    db, "chief-of-staff", company_id=company_id
                )
                artifacts = artifact_repo.list_run_artifacts(
                    db, run_id=run_id, company_id=company_id
                )
                prompt = self.prompt_loader.render(
                    chief.prompt_version,
                    "chief_of_staff_brief",
                    company_name=company.name,
                    agent_objective=chief.objective,
                    objective_title=objective.title,
                    desired_outcome=objective.desired_outcome,
                    objective_constraints=objective.constraints,
                    artifacts=[
                        {
                            "title": artifact.title,
                            "artifact_type": artifact.artifact_type,
                            "content_markdown": artifact.content_markdown,
                        }
                        for artifact in artifacts
                    ],
                )
                brief = self.model_adapter.synthesize_brief(
                    prompt=prompt,
                    model_alias=chief.runtime_model_alias,
                    objective_title=objective.title,
                    artifact_titles=[
                        artifact.title for artifact in artifacts
                    ],
                )
                artifact = artifact_repo.create_artifact(
                    db,
                    run_id=run_id,
                    work_item_id=None,
                    draft=ArtifactDraft(
                        artifact_type="executive_brief",
                        title=brief.title,
                        content_markdown=brief.content_markdown,
                    ),
                    company_id=company_id,
                )
                event_repo.append_event(
                    db,
                    run_id=run_id,
                    event_type="brief.created",
                    summary=f"Created executive brief: {artifact.title}",
                    payload_json={"artifact_id": str(artifact.id)},
                    company_id=company_id,
                )
        except PromptNotFoundError:
            return {"error_code": "PROMPT_VERSION_NOT_FOUND"}
        except (PromptRenderError, ModelAdapterError):
            return {"error_code": "BRIEF_SYNTHESIS_FAILED"}
        except Exception:
            return {"error_code": "BRIEF_SYNTHESIS_FAILED"}
        return {"error_code": None}

    def _complete(self, state: RuntimeState) -> RuntimeState:
        company_id = self._uuid(state, "company_id")
        objective_id = self._uuid(state, "objective_id")
        run_id = self._uuid(state, "run_id")
        with self.session_factory() as db:
            objective_repo.update_objective_status(
                db, objective_id, "completed", company_id=company_id
            )
            run_repo.update_run_status(
                db, run_id, "completed", company_id=company_id
            )
            event_repo.append_event(
                db,
                run_id=run_id,
                event_type="run.completed",
                summary="Completed the approved objective run",
                payload_json={"objective_id": str(objective_id)},
                company_id=company_id,
            )
        return {}

    def _fail(self, state: RuntimeState) -> RuntimeState:
        company_id = self._uuid(state, "company_id")
        objective_id = self._uuid(state, "objective_id")
        run_id = self._uuid(state, "run_id")
        error_code = state.get("error_code") or "RUNTIME_FAILED"
        with self.session_factory() as db:
            objective = objective_repo.get_objective(
                db, objective_id, company_id=company_id
            )
            if objective.status != "failed":
                objective_repo.update_objective_status(
                    db, objective_id, "failed", company_id=company_id
                )
            run_repo.update_run_status(
                db,
                run_id,
                "failed",
                error_code=error_code,
                company_id=company_id,
            )
            event_repo.append_event(
                db,
                run_id=run_id,
                event_type="run.failed",
                summary=f"Run stopped with error code {error_code}",
                payload_json={"error_code": error_code},
                company_id=company_id,
            )
        return {}

    def _mark_work_failed(
        self,
        db: Session,
        work_item_id: UUID,
        run_id: UUID,
        company_id: UUID,
        error_code: str,
    ) -> RuntimeState:
        work_item = work_item_repo.get_work_item(
            db, work_item_id, company_id=company_id
        )
        if work_item.status != "failed":
            work_item_repo.update_work_item_status(
                db, work_item_id, "failed", company_id=company_id
            )
            event_repo.append_event(
                db,
                run_id=run_id,
                event_type="work.failed",
                summary=f"Work item failed: {work_item.title}",
                payload_json={
                    "work_item_id": str(work_item_id),
                    "error_code": error_code,
                },
                company_id=company_id,
            )
        return {
            "current_work_item_id": str(work_item_id),
            "pending_artifact": None,
            "error_code": error_code,
        }

    @staticmethod
    def _validate_plan_assignments(
        plan: PlanDraft, enabled_slugs: set[str]
    ) -> None:
        assigned_slugs = {
            item.assigned_agent_slug for item in plan.work_items
        }
        unavailable = assigned_slugs - enabled_slugs
        if unavailable:
            raise ModelAdapterError(
                "Plan assigned one or more unavailable specialists"
            )

    @staticmethod
    def _enabled_specialists(
        db: Session, company_id: UUID
    ) -> list[AgentDefinitionModel]:
        agents = {
            agent.slug: agent
            for agent in agent_repo.list_agents(db, company_id=company_id)
            if agent.enabled
        }
        return [
            agents[slug] for slug in SPECIALIST_SLUGS if slug in agents
        ]

    @staticmethod
    def _route_after_plan(state: RuntimeState) -> RouteAfterPlan:
        return (
            "fail"
            if state.get("error_code")
            else "wait_for_plan_approval"
        )

    @staticmethod
    def _route_after_approval(
        state: RuntimeState,
    ) -> RouteAfterApproval:
        if state.get("error_code"):
            return "fail"
        return (
            "create_plan"
            if state.get("decision") == "revise"
            else "execute_next_work_item"
        )

    @staticmethod
    def _route_after_work(state: RuntimeState) -> RouteAfterWork:
        if state.get("error_code"):
            return "fail"
        if state.get("pending_artifact") is not None:
            return "persist_artifact"
        return "synthesize_executive_brief"

    @staticmethod
    def _route_after_brief(state: RuntimeState) -> RouteAfterBrief:
        return "fail" if state.get("error_code") else "complete"
