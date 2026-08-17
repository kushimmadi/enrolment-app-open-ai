from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModeConfig:
    key: str
    label: str
    prompt_family: str
    implementation_prompts: tuple[str, ...]
    review_prompts: tuple[str, ...] = ()


def build_mode_config() -> dict[str, ModeConfig]:
    return {
        "db": ModeConfig(
            key="db",
            label="DB",
            prompt_family="service",
            implementation_prompts=(
                "implementation/system_prompt.txt",
                "implementation/task_prompt.txt",
                "implementation/context_prompt.txt",
            ),
        ),
        "endpoints": ModeConfig(
            key="endpoints",
            label="Endpoints",
            prompt_family="service",
            implementation_prompts=(
                "implementation/system_prompt.txt",
                "implementation/task_prompt.txt",
                "implementation/context_prompt.txt",
            ),
        ),
        "architecture": ModeConfig(
            key="architecture",
            label="Architecture",
            prompt_family="lab4",
            implementation_prompts=(
                "implementation/architecture_system_prompt.txt",
                "implementation/architecture_task_prompt.txt",
            ),
            review_prompts=("review/agent_review_prompt.txt",),
        ),
    }


def prompts_root(app_dir: Path) -> Path:
    return app_dir / "prompts"
