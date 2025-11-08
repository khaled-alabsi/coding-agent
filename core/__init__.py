"""Core package for Azure Code Agent.

Intentionally keeps __init__ lightweight to avoid importing heavy
dependencies (e.g., OpenAI client) at package import time.
Import submodules directly as needed, e.g.:
  from core.llm_client import LLMClient
  from core.file_operations import FileOperations
  from core.orchestrator import AgentOrchestrator
"""

__all__: list[str] = []
