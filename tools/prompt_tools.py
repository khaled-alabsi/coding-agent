"""Prompt/Plan tools for the Coder agent.

These thin wrappers use the shared LLM client with agent-specific system prompts.
"""
from typing import Optional

from utils import load_prompt
from typing import TYPE_CHECKING
from config import AgentConfig

if TYPE_CHECKING:
    from core.llm_client import LLMClient


def enhance_prompt(llm: 'LLMClient', config: AgentConfig, user_prompt: str) -> str:
    system = load_prompt("prompt_enhancer")
    return llm.chat(
        messages=[
            {
                "role": "user",
                "content": f"Enhance this user request into a detailed specification:\n\n{user_prompt}",
            }
        ],
        system_message=system,
        agent_name="PromptEnhancerTool",
    )


def create_plan(llm: 'LLMClient', config: AgentConfig, enhanced_prompt: str) -> str:
    system = load_prompt("planner")
    return llm.chat(
        messages=[
            {
                "role": "user",
                "content": (
                    "Create a detailed execution plan for this specification:\n\n"
                    f"{enhanced_prompt}"
                ),
            }
        ],
        system_message=system,
        agent_name="PlannerTool",
    )


def enhance_plan(llm: 'LLMClient', config: AgentConfig, plan: str) -> str:
    system = load_prompt("plan_enhancer")
    return llm.chat(
        messages=[
            {
                "role": "user",
                "content": (
                    "Review and enhance this execution plan. Ensure it's complete and"
                    " addresses all common pitfalls:\n\n" f"{plan}"
                ),
            }
        ],
        system_message=system,
        agent_name="PlanEnhancerTool",
    )
