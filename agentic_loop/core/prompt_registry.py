from pathlib import Path


class PromptRegistry:
    def __init__(self, app_dir: Path):
        self.app_dir = app_dir
        self.root = app_dir / "prompts"

    def resolve(self, family: str, relative_file: str) -> Path:
        candidate = self.root / family / relative_file
        if not candidate.exists():
            rel = candidate.relative_to(self.app_dir)
            raise FileNotFoundError(f"Missing prompt file: {rel}")
        return candidate

    def read(self, family: str, relative_file: str) -> str:
        return self.resolve(family, relative_file).read_text(encoding="utf-8").strip()

    def family_path(self, family: str) -> Path:
        return self.root / family
