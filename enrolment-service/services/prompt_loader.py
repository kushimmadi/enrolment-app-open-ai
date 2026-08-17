from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR.parent
PROMPT_DIR = APP_DIR / "prompts"
LAB4_IMPLEMENTATION_PROMPT_DIR = PROMPT_DIR / "lab4" / "implementation"
LAB4_REVIEW_PROMPT_DIR = PROMPT_DIR / "lab4" / "review"


def load_prompt(filename):
    return (PROMPT_DIR / filename).read_text(encoding="utf-8").strip()


def load_lab4_prompt(filename):
    prompt_dirs = [LAB4_IMPLEMENTATION_PROMPT_DIR, LAB4_REVIEW_PROMPT_DIR]

    for prompt_dir in prompt_dirs:
        candidate = prompt_dir / filename
        if candidate.exists():
            return candidate.read_text(encoding="utf-8").strip()

    return (LAB4_IMPLEMENTATION_PROMPT_DIR / filename).read_text(encoding="utf-8").strip()
