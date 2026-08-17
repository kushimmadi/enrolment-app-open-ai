def build_user_prompt(task_prompt: str, context_prompt: str, evidence: str) -> str:
    """Build user prompt for endpoints review, injecting placeholders."""

    # Replace placeholders in task_prompt
    task_with_evidence = task_prompt.replace("{{REVIEW_TARGET}}", "Endpoints")
    task_with_evidence = task_with_evidence.replace("{{VALIDATION_EVIDENCE}}", evidence)

    return f"""
{task_with_evidence}

Application Context:
{context_prompt}
""".strip()
