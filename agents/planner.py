"""Planner Agent - Creates detailed execution plans."""
from .base_agent import BaseAgent
from utils import load_prompt


class PlannerAgent(BaseAgent):
    """Creates detailed step-by-step execution plans."""

    @property
    def agent_name(self) -> str:
        return "Planner"

    @property
    def system_prompt(self) -> str:
        return load_prompt("planner")

    def create_plan(self, enhanced_prompt: str) -> str:
        """
        Create an execution plan from an enhanced prompt.

        Args:
            enhanced_prompt: Enhanced specification

        Returns:
            Detailed execution plan
        """
        print(f"\n📋 Creating execution plan...")

        response = self.chat(
            f"Create a detailed execution plan for this specification:\n\n{enhanced_prompt}",
            display=True
        )

        return response
