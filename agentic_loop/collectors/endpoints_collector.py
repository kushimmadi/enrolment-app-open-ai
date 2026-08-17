import os
import re
from pathlib import Path

import requests


ROUTE_PATTERN = re.compile(r"@\w+_bp\.(get|post)\(\"([^\"]+)\"\)")


def _test_endpoint(base_url: str, method: str, path: str) -> str:
    """Test a single endpoint and return evidence string."""
    url = f"{base_url}{path}"

    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=2)
        elif method.upper() == "POST":
            response = requests.post(url, data={"question": "test"}, timeout=2)
        else:
            return f"{method.upper()} {path} [UNSUPPORTED METHOD]"

        elapsed_ms = int(response.elapsed.total_seconds() * 1000)
        status = response.status_code

        if status == 200:
            return f"{method.upper()} {path} returned {status} in {elapsed_ms}ms"
        else:
            return f"{method.upper()} {path} returned {status} in {elapsed_ms}ms"

    except requests.exceptions.ConnectionError:
        return f"{method.upper()} {path} [CONNECTION REFUSED - app not running]"
    except requests.exceptions.Timeout:
        return f"{method.upper()} {path} [TIMEOUT]"
    except Exception as exc:
        return f"{method.upper()} {path} [ERROR: {type(exc).__name__}]"


def collect(app_dir: Path, repo_root: Path) -> tuple[bool, str]:
    """Collect live endpoint evidence by making real HTTP requests."""
    flask_base_url = os.getenv("FLASK_BASE_URL", "http://localhost:5001")

    route_files = [
        app_dir / "enrolment-service" / "routes" / "normal_ui.py",
        app_dir / "enrolment-service" / "routes" / "ai_mode.py",
    ]

    missing = [str(path.relative_to(app_dir)) for path in route_files if not path.exists()]
    if missing:
        return False, "Missing route files: " + ", ".join(missing)

    endpoints: list[tuple[str, str]] = []

    for route_file in route_files:
        content = route_file.read_text(encoding="utf-8")
        for method, route in ROUTE_PATTERN.findall(content):
            endpoints.append((method, route))

    if not endpoints:
        return False, "No Flask routes found in route files."

    # Test each endpoint with real HTTP requests
    evidence_parts = []
    connection_failures = 0

    for method, route in sorted(set(endpoints)):
        result = _test_endpoint(flask_base_url, method, route)
        evidence_parts.append(result)
        if "CONNECTION REFUSED" in result:
            connection_failures += 1

    evidence = "Live endpoint evidence: " + "; ".join(evidence_parts) + "."

    # If all endpoints failed to connect, warn that app isn't running
    if connection_failures == len(endpoints):
        return False, "Flask app not running. Start the app first, then run the agentic loop."

    return True, evidence
