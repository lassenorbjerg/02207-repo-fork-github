"""JSON input configuration for the PyUVM testbench viewer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


class ConfigurationError(ValueError):
    """Raised when a viewer configuration is invalid."""


@dataclass
class ViewerConfig:
    """Resolved viewer input configuration."""

    path: Path
    top_level_uvm_test: Path
    include_dirs: list[Path] = field(default_factory=list)
    instance_rendering: dict[str, str] = field(default_factory=dict)
    experimental: bool = False
    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"


def load_viewer_config(config_file: str | Path) -> ViewerConfig:
    """Load and validate a viewer JSON file."""

    path = Path(config_file).expanduser().resolve()
    if not path.is_file():
        raise ConfigurationError(f"Configuration file does not exist: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ConfigurationError(f"Unable to read {path}: {error}") from error

    if not isinstance(data, dict):
        raise ConfigurationError("The JSON root must be an object")

    top_level = data.get("top_level_uvm_test")
    if not isinstance(top_level, str) or not top_level:
        raise ConfigurationError(
            "'top_level_uvm_test' must be a non-empty relative path"
        )
    top_level_path = _resolve_relative(path.parent, top_level)
    if not top_level_path.is_file():
        raise ConfigurationError(
            f"Top-level PyUVM test does not exist: {top_level_path}"
        )

    include_values = data.get("include_dirs", [])
    if not isinstance(include_values, list) or not all(
        isinstance(item, str) for item in include_values
    ):
        raise ConfigurationError("'include_dirs' must be a list of paths")
    include_dirs = [_resolve_relative(path.parent, item) for item in include_values]
    missing_dirs = [item for item in include_dirs if not item.is_dir()]
    if missing_dirs:
        raise ConfigurationError(
            f"Include directory does not exist: {missing_dirs[0]}"
        )

    rendering = data.get("instance_rendering", {})
    if not isinstance(rendering, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in rendering.items()
    ):
        raise ConfigurationError(
            "'instance_rendering' must map instance paths to string values"
        )
    for instance_path, value in rendering.items():
        if not instance_path:
            raise ConfigurationError("Instance rendering paths cannot be empty")
        if value in {"hide", "grey"}:
            continue
        if value.startswith("conditional:") and value.removeprefix("conditional:"):
            continue
        raise ConfigurationError(
            f"Invalid rendering value for '{instance_path}': {value}"
        )

    experimental = data.get("experimental", False)
    if not isinstance(experimental, bool):
        raise ConfigurationError("'experimental' must be true or false")

    openai_api_key = data.get("openai_api_key", "")
    if not isinstance(openai_api_key, str):
        raise ConfigurationError("'openai_api_key' must be a string")
    if experimental and "openai_api_key" not in data:
        raise ConfigurationError(
            "Experimental analysis requires an 'openai_api_key' entry"
        )

    openai_model = data.get("openai_model", "gpt-5-mini")
    if not isinstance(openai_model, str) or not openai_model.strip():
        raise ConfigurationError("'openai_model' must be a non-empty string")

    return ViewerConfig(
        path=path,
        top_level_uvm_test=top_level_path,
        include_dirs=include_dirs,
        instance_rendering=rendering,
        experimental=experimental,
        openai_api_key=openai_api_key,
        openai_model=openai_model,
    )


def _resolve_relative(base: Path, value: str) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = base / candidate
    return candidate.resolve()
