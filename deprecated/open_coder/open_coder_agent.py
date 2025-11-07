from pathlib import Path
import os
from typing import Optional


def _get_client(base_url: Optional[str] = None):
    try:
        from opencode_ai import Opencode  # type: ignore
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "Missing dependency 'opencode_ai'. Install with `pip install opencode-ai` "
            "and ensure your OpenCode server is running."
        ) from e

    resolved_base = (
        base_url
        or os.environ.get("OPENCODE_BASE_URL")
        or "http://127.0.0.1:4096"
    )
    return Opencode(base_url=resolved_base)


def run(*, base_url: Optional[str] = None, title: Optional[str] = None, **_kwargs) -> None:
    client = _get_client(base_url)

    session = client.session.create(
        body={"title": title or "Qwen3 Coder 30B – OpenCode demo"}
    )
    print("Session ID:", session.id)

    spec_path = Path("prompt.md")
    spec_text = spec_path.read_text(encoding="utf-8") if spec_path.exists() else ""

    user_message = (
        "You are an AI coding agent running on Qwen3 Coder 30B.\n"
        "You are attached to this repository. Read the project spec below and\n"
        "plan + implement the required changes step by step.\n\n"
        "--- PROJECT SPEC (prompt.md) ---\n"
        f"{spec_text or '(no spec file found, just help me in general)'}"
    )

    result = client.session.prompt(
        path={"id": session.id},
        body={
            "model": {
                "providerID": "lmstudio",
                "modelID": "qwen3-coder-30b",
            },
            "parts": [
                {"type": "text", "text": user_message}
            ],
        },
    )

    print(result.to_json(indent=2))
