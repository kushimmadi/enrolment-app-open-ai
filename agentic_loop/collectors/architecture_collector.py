from pathlib import Path


REQUIRED_SERVICES = ["frontend-service", "enrolment-service", "database-service"]


def collect(app_dir: Path, repo_root: Path) -> tuple[bool, str]:
    required_paths = [
        app_dir / "frontend-service" / "templates" / "index.html",
        app_dir / "frontend-service" / "css" / "styles.css",
        app_dir / "enrolment-service" / "app.py",
        app_dir / "database-service" / "app.py",
        app_dir / "database-service" / "init_db.py",
        app_dir / "docker-compose.yml",
    ]

    missing = [str(path.relative_to(app_dir)) for path in required_paths if not path.exists()]
    if missing:
        return False, "Architecture evidence incomplete. Missing: " + ", ".join(missing)

    compose_text = (app_dir / "docker-compose.yml").read_text(encoding="utf-8")
    present = [name for name in REQUIRED_SERVICES if name in compose_text]
    if len(present) != len(REQUIRED_SERVICES):
        return False, "docker-compose does not define all required services."

    return True, (
        "Architecture evidence: frontend, backend, database service files and "
        "three-service compose topology are present."
    )
