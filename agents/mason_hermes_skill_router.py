from dataclasses import dataclass
import shlex


HERMES_EXE = r"C:\Users\User\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe"


@dataclass
class MasonHermesRoute:
    intent: str
    hermes_skill: str
    reason: str


SKILL_MAP = {
    "inspect": MasonHermesRoute("inspect", "official/software-development/codebase-inspector", "Understand files, structure, or existing code before editing."),
    "debug": MasonHermesRoute("debug", "skills-sh/obra/superpowers/systematic-debugging", "Investigate broken, hanging, crashing, or erroring code."),
    "test": MasonHermesRoute("test", "official/software-development/test-driven-development", "Create, improve, or run tests."),
    "simplify": MasonHermesRoute("simplify", "official/software-development/simplify-code", "Clean up messy, duplicated, or over-complicated code."),
    "review": MasonHermesRoute("review", "requesting-code-review", "Review changes before approval."),
    "github_review": MasonHermesRoute("github_review", "github-code-review", "GitHub-style review workflow."),
    "build": MasonHermesRoute("build", "official/software-development/subagent-driven-development", "Plan and execute larger builder tasks."),
    "codex": MasonHermesRoute("codex", "codex", "Optional coding engine."),
    "claude": MasonHermesRoute("claude", "claude-code", "Optional coding engine."),
    "opencode": MasonHermesRoute("opencode", "opencode", "Optional coding engine."),
}


def choose_skill(task_text: str) -> MasonHermesRoute:
    text = task_text.lower()

    if any(word in text for word in ["inspect", "scan", "look at", "understand", "analyze codebase"]):
        return SKILL_MAP["inspect"]

    if any(word in text for word in ["debug", "error", "broken", "crash", "hang", "traceback", "not working"]):
        return SKILL_MAP["debug"]

    if any(word in text for word in ["test", "pytest", "unit test", "verify"]):
        return SKILL_MAP["test"]

    if any(word in text for word in ["simplify", "clean up", "refactor", "too much", "messy"]):
        return SKILL_MAP["simplify"]

    if any(word in text for word in ["github", "pull request", "pr review"]):
        return SKILL_MAP["github_review"]

    if any(word in text for word in ["review", "check my code", "code review"]):
        return SKILL_MAP["review"]

    if any(word in text for word in ["build", "create", "make", "implement", "auto-builder"]):
        return SKILL_MAP["build"]

    return SKILL_MAP["inspect"]


def build_safe_preview_command(task_text: str) -> list[str]:
    route = choose_skill(task_text)

    return [
        HERMES_EXE,
        "skills",
        "inspect",
        route.hermes_skill,
    ]


def describe_route(task_text: str) -> str:
    route = choose_skill(task_text)
    preview_command = build_safe_preview_command(task_text)

    return (
        f"MASON/HERMES ROUTE\n"
        f"Intent: {route.intent}\n"
        f"Hermes skill: {route.hermes_skill}\n"
        f"Reason: {route.reason}\n"
        f"Safe preview command:\n"
        f"{preview_command}\n"
    )


if __name__ == "__main__":
    import sys

    sample_task = " ".join(sys.argv[1:]) or "inspect this project"
    print(describe_route(sample_task))
