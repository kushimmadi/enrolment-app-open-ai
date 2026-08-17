from pathlib import Path

from dotenv import load_dotenv

from config.review_config import build_mode_config
from core.ai_runner import AIRunner
from core.orchestrator import run_mode
from core.prompt_registry import PromptRegistry
from core.reporter import print_menu, print_prompt_map, print_result


def _resolve_roots() -> tuple[Path, Path]:
    module_dir = Path(__file__).resolve().parent
    app_dir = module_dir.parent
    repo_root = app_dir.parent
    return app_dir, repo_root


def _menu_choice_to_key(choice: str) -> str | None:
    return {
        "1": "db",
        "2": "endpoints",
        "3": "architecture",
    }.get(choice)


def _print_mode_mapping(app_dir: Path) -> None:
    prompt_map = {
        "DB": app_dir / "prompts" / "service",
        "Endpoints": app_dir / "prompts" / "service",
        "Architecture": app_dir / "prompts" / "lab4",
    }
    print_prompt_map({key: str(path) for key, path in prompt_map.items()})


def main() -> None:
    app_dir, repo_root = _resolve_roots()
    load_dotenv(dotenv_path=app_dir / ".env")

    mode_config = build_mode_config()
    prompts = PromptRegistry(app_dir)
    ai = AIRunner()

    print("AGENTIC LOOP (MODULAR)")
    _print_mode_mapping(app_dir)

    while True:
        print_menu()
        choice = input("Choose a review target: ").strip()

        if choice == "0":
            print("Loop closed.")
            break

        if choice == "4":
            for key in ("db", "endpoints", "architecture"):
                result = run_mode(mode_config[key], app_dir, repo_root, prompts, ai)
                print_result(mode_config[key].label, result)
            continue

        mode_key = _menu_choice_to_key(choice)
        if not mode_key:
            print("Invalid choice. Select 0, 1, 2, 3, or 4.")
            continue

        result = run_mode(mode_config[mode_key], app_dir, repo_root, prompts, ai)
        print_result(mode_config[mode_key].label, result)
