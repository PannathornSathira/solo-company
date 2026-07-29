from typing import Protocol

from app.runtime.contracts import (
    ArtifactDraft,
    ExecutiveBriefDraft,
    PlanDraft,
    PlanItemDraft,
)


class ModelAdapterError(Exception):
    pass


class ModelAdapter(Protocol):
    def propose_plan(
        self,
        *,
        prompt: str,
        model_alias: str,
        specialist_slugs: list[str],
    ) -> PlanDraft: ...

    def execute_work_item(
        self,
        *,
        prompt: str,
        model_alias: str,
        agent_name: str,
        work_item_title: str,
        deliverable_type: str,
    ) -> ArtifactDraft: ...

    def synthesize_brief(
        self,
        *,
        prompt: str,
        model_alias: str,
        objective_title: str,
        artifact_titles: list[str],
    ) -> ExecutiveBriefDraft: ...


class FakeModelAdapter:
    def __init__(
        self,
        fail_on_position: int | None = None,
        *,
        fail_brief_once: bool = False,
    ) -> None:
        self.fail_on_position = fail_on_position
        self.fail_brief_once = fail_brief_once
        self.plan_calls = 0
        self.work_calls = 0
        self.brief_calls = 0

    def propose_plan(
        self,
        *,
        prompt: str,
        model_alias: str,
        specialist_slugs: list[str],
    ) -> PlanDraft:
        self.plan_calls += 1
        if len(specialist_slugs) < 2:
            raise ModelAdapterError(
                "The fake runtime requires two enabled specialist agents"
            )
        first, second = specialist_slugs[:2]
        return PlanDraft(
            work_items=[
                PlanItemDraft(
                    assigned_agent_slug=first,
                    title="Develop the market positioning brief",
                    instructions=(
                        "Define the target audience, positioning, key messages, "
                        "and a practical launch sequence."
                    ),
                    deliverable_type="marketing_brief",
                ),
                PlanItemDraft(
                    assigned_agent_slug=second,
                    title="Design the operating checklist",
                    instructions=(
                        "Create a sequential operating checklist with owners, "
                        "quality gates, and completion criteria."
                    ),
                    deliverable_type="operations_checklist",
                ),
                PlanItemDraft(
                    assigned_agent_slug=first,
                    title="Prepare the launch action plan",
                    instructions=(
                        "Combine the approved direction into a concise, "
                        "time-ordered launch action plan."
                    ),
                    deliverable_type="launch_action_plan",
                ),
            ]
        )

    def execute_work_item(
        self,
        *,
        prompt: str,
        model_alias: str,
        agent_name: str,
        work_item_title: str,
        deliverable_type: str,
    ) -> ArtifactDraft:
        self.work_calls += 1
        if self.fail_on_position == self.work_calls:
            raise ModelAdapterError("Deterministic fake-model work failure")
        title = f"{work_item_title} — Deliverable"
        return ArtifactDraft(
            artifact_type=deliverable_type,
            title=title,
            content_markdown=(
                f"# {title}\n\n"
                f"Prepared by **{agent_name}**.\n\n"
                "## Recommended approach\n\n"
                "1. Confirm the intended outcome and constraints.\n"
                "2. Execute the work in the approved sequence.\n"
                "3. Validate the deliverable against its completion criteria.\n\n"
                "## Completion criteria\n\n"
                "- The output is actionable and owner-readable.\n"
                "- Assumptions and follow-up decisions are explicit.\n"
            ),
        )

    def synthesize_brief(
        self,
        *,
        prompt: str,
        model_alias: str,
        objective_title: str,
        artifact_titles: list[str],
    ) -> ExecutiveBriefDraft:
        self.brief_calls += 1
        if self.fail_brief_once and self.brief_calls == 1:
            raise ModelAdapterError(
                "Deterministic fake-model brief failure"
            )
        artifact_list = "\n".join(f"- {title}" for title in artifact_titles)
        title = f"Executive brief: {objective_title}"
        return ExecutiveBriefDraft(
            title=title,
            content_markdown=(
                f"# {title}\n\n"
                "## Completed deliverables\n\n"
                f"{artifact_list}\n\n"
                "## Executive recommendation\n\n"
                "Proceed with the approved sequence and review the recorded "
                "completion criteria before committing additional resources.\n\n"
                "## Follow-up suggestions\n\n"
                "- Confirm the owner and due date for each next action.\n"
                "- Review outcomes after the first execution cycle.\n"
            ),
        )


class GeminiModelAdapter:
    def __init__(self, *, api_key: str, model_id: str) -> None:
        if not api_key:
            raise ModelAdapterError(
                "GEMINI_API_KEY is required when RUNTIME_MODEL_BACKEND=gemini"
            )
        from google import genai

        self.client = genai.Client(api_key=api_key)
        self.model_aliases = {"gemini-3.1-pro": model_id}

    def _generate(
        self,
        prompt: str,
        model_alias: str,
        schema: (
            type[PlanDraft]
            | type[ArtifactDraft]
            | type[ExecutiveBriefDraft]
        ),
    ):
        from google.genai import types

        model_id = self.model_aliases.get(model_alias)
        if model_id is None:
            raise ModelAdapterError(
                f"Unsupported Phase 1 runtime model alias '{model_alias}'"
            )
        try:
            response = self.client.models.generate_content(
                model=model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )
            if response.parsed is None:
                raise ModelAdapterError("Gemini returned no structured output")
            return schema.model_validate(response.parsed)
        except ModelAdapterError:
            raise
        except Exception as exc:
            raise ModelAdapterError("Gemini model request failed") from exc

    def propose_plan(
        self,
        *,
        prompt: str,
        model_alias: str,
        specialist_slugs: list[str],
    ) -> PlanDraft:
        return self._generate(prompt, model_alias, PlanDraft)

    def execute_work_item(
        self,
        *,
        prompt: str,
        model_alias: str,
        agent_name: str,
        work_item_title: str,
        deliverable_type: str,
    ) -> ArtifactDraft:
        return self._generate(prompt, model_alias, ArtifactDraft)

    def synthesize_brief(
        self,
        *,
        prompt: str,
        model_alias: str,
        objective_title: str,
        artifact_titles: list[str],
    ) -> ExecutiveBriefDraft:
        return self._generate(prompt, model_alias, ExecutiveBriefDraft)
