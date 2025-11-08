"""Plan Enhancer Agent - Improves and validates execution plans."""
from .base_agent import BaseAgent
from utils import load_prompt


class PlanEnhancerAgent(BaseAgent):
    """Enhances and validates execution plans for completeness."""

    @property
    def agent_name(self) -> str:
        return "Plan Enhancer"

    @property
    def system_prompt(self) -> str:
        return load_prompt("plan_enhancer")

    def enhance_plan(self, original_plan: str) -> str:
        """
        Enhance and validate an execution plan.

        Args:
            original_plan: Original execution plan

        Returns:
            Enhanced plan
        """
        print(f"\n🔍 Enhancing and validating plan...")

        response = self.chat(
            f"Review and enhance this execution plan. Ensure it's complete and addresses all common pitfalls:\n\n{original_plan}",
            display=True
        )

        return response
