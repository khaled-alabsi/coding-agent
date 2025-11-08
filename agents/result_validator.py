"""Result Validator Agent - Validates implementation against plan."""
from .base_agent import BaseAgent

from core.file_operations import FileOperations
from utils import load_prompt


class ResultValidatorAgent(BaseAgent):
    """Validates implementation results against the plan."""

    def __init__(self, config, llm_client, file_ops: FileOperations):
        """
        Initialize the result validator agent.

        Args:
            config: Agent configuration
            llm_client: Shared LLM client
            file_ops: File operations handler
        """
        super().__init__(config, llm_client)
        self.file_ops = file_ops

    @property
    def agent_name(self) -> str:
        return "Result Validator"

    @property
    def system_prompt(self) -> str:
        return load_prompt("result_validator")

    def validate_results(self, plan: str, implementation_summary: str) -> dict:
        """
        Validate implementation results against the plan.

        Args:
            plan: Original execution plan
            implementation_summary: Summary from coder agent

        Returns:
            Validation results dict
        """
        print(f"\n🔍 Validating implementation against plan...")

        # Scan the output directory
        files = list(self.file_ops.working_directory.rglob("*"))
        file_list = "\n".join([f"- {f.relative_to(self.file_ops.working_directory)}" for f in files if f.is_file()])

        validation_prompt = f"""Validate this implementation against the plan.

ORIGINAL PLAN:
{plan}

IMPLEMENTATION SUMMARY:
{implementation_summary}

FILES CREATED:
{file_list}

Analyze whether the implementation matches the plan and meets quality standards.
Return your validation in the specified JSON format."""

        response = self.chat(validation_prompt, display=True)

        # Parse the validation result
        import json
        from utils.helpers import extract_json

        try:
            validation_result = extract_json(response)
            if not validation_result:
                # Fallback if JSON parsing fails
                validation_result = {
                    "status": "UNKNOWN",
                    "score": 50,
                    "passed_checks": [],
                    "failed_checks": ["Could not parse validation results"],
                    "critical_issues": [],
                    "suggestions": [],
                    "requires_fix": False
                }
        except Exception as e:
            print(f"⚠️  Error parsing validation: {e}")
            validation_result = {
                "status": "ERROR",
                "score": 0,
                "passed_checks": [],
                "failed_checks": [str(e)],
                "critical_issues": [str(e)],
                "suggestions": [],
                "requires_fix": False
            }

        return validation_result

    def generate_fix_instructions(self, validation_result: dict) -> str:
        """
        Generate instructions to fix issues found in validation.

        Args:
            validation_result: Validation results dict

        Returns:
            Fix instructions for the coder agent
        """
        if not validation_result.get("requires_fix", False):
            return ""

        print(f"\n🔧 Generating fix instructions...")

        fix_prompt = f"""Based on these validation results, create specific fix instructions for the coder.

FAILED CHECKS:
{chr(10).join(validation_result.get('failed_checks', []))}

CRITICAL ISSUES:
{chr(10).join(validation_result.get('critical_issues', []))}

Generate clear, actionable instructions to fix these issues. Be specific about which files need changes and what exactly should be fixed."""

        response = self.chat(fix_prompt, display=True)
        return response
