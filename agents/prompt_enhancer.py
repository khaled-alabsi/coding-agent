"""Prompt Enhancer Agent - Improves user prompts for better clarity."""
from .base_agent import BaseAgent
from utils import load_prompt


class PromptEnhancerAgent(BaseAgent):
    """Enhances user prompts with more detail and context."""

    @property
    def agent_name(self) -> str:
        return "Prompt Enhancer"

    @property
    def system_prompt(self) -> str:
        return load_prompt("prompt_enhancer")

    def enhance_prompt(self, user_prompt: str) -> str:
        """
        Enhance a user prompt with more detail and context.

        Args:
            user_prompt: Original user prompt

        Returns:
            Enhanced prompt
        """
        print(f"\n💡 Enhancing prompt...")
        print(f"Original: {user_prompt}\n")

        response = self.chat(
            f"Enhance this user request into a detailed specification:\n\n{user_prompt}",
            display=True
        )

        return response
