import json
import re
from pathlib import Path
from string import Template
from typing import Any


class PromptNotFoundError(Exception):
    pass


class PromptRenderError(Exception):
    pass


class PromptLoader:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).parent / "prompt_versions"

    def render(self, version: str, prompt_name: str, **values: Any) -> str:
        if not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", version):
            raise PromptNotFoundError(f"Unsupported prompt version '{version}'")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", prompt_name):
            raise PromptNotFoundError(f"Unsupported prompt name '{prompt_name}'")

        prompt_path = self.root / version / f"{prompt_name}.md"
        if not prompt_path.is_file():
            raise PromptNotFoundError(
                f"Prompt '{prompt_name}' version '{version}' was not found"
            )

        serialized_values = {
            key: (
                json.dumps(value, ensure_ascii=False, indent=2)
                if isinstance(value, (dict, list))
                else str(value)
            )
            for key, value in values.items()
        }
        try:
            return Template(prompt_path.read_text()).substitute(serialized_values)
        except KeyError as exc:
            raise PromptRenderError(
                f"Prompt '{prompt_name}' is missing variable '{exc.args[0]}'"
            ) from exc
