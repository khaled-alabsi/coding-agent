"""Agent Orchestrator - Coordinates the multi-agent workflow."""
import json
from pathlib import Path
from typing import Optional
from datetime import datetime
from ..config import AgentConfig
from .llm_client import LLMClient
from .file_operations import FileOperations
from ..utils import AgentLogger, play_completion_sound, play_error_sound
from ..agents import (
    PromptEnhancerAgent,
    PlannerAgent,
    PlanEnhancerAgent,
    CoderAgent,
    ResultValidatorAgent
)


class AgentOrchestrator:
    """Orchestrates the multi-agent workflow."""

    def __init__(self, config: AgentConfig):
        """
        Initialize the orchestrator.

        Args:
            config: Agent configuration
        """
        self.config = config

        # Initialize logger
        log_filename = f"agent_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.logger = AgentLogger(config.project_dir / log_filename)

        # Initialize core components with logger
        self.llm_client = LLMClient(config, logger=self.logger)
        self.file_ops = FileOperations(config, logger=self.logger)

        # Initialize all agents
        self.prompt_enhancer = PromptEnhancerAgent(config, self.llm_client)
        self.planner = PlannerAgent(config, self.llm_client)
        self.plan_enhancer = PlanEnhancerAgent(config, self.llm_client)
        self.coder = CoderAgent(config, self.llm_client, self.file_ops)
        self.validator = ResultValidatorAgent(config, self.llm_client, self.file_ops)

        # Workflow state
        self.current_prompt = ""
        self.enhanced_prompt = ""
        self.plan = ""
        self.enhanced_plan = ""
        self.implementation_result = ""
        self.validation_result = {}

        print(f"📝 Logging to: {self.logger.log_file}")

    def execute_workflow(
        self,
        user_prompt: str,
        output_directory: Optional[Path] = None,
        skip_prompt_enhancement: bool = False,
        skip_plan_enhancement: bool = False,
        max_fix_iterations: int = 3
    ) -> dict:
        """
        Execute the complete multi-agent workflow.

        Args:
            user_prompt: User's initial prompt
            output_directory: Custom output directory (default: config.output_dir)
            skip_prompt_enhancement: Skip prompt enhancement step
            skip_plan_enhancement: Skip plan enhancement step
            max_fix_iterations: Maximum number of fix iterations

        Returns:
            Dict with workflow results
        """
        print("=" * 70)
        print("🚀 MULTI-AGENT CODING WORKFLOW")
        print("=" * 70)

        # Log workflow start
        self.logger.log_workflow_start(user_prompt)

        # Set output directory
        if output_directory:
            self.file_ops.set_working_directory(output_directory)
            print(f"\n📁 Output Directory: {output_directory}")
        else:
            print(f"\n📁 Output Directory: {self.config.output_dir}")

        self.current_prompt = user_prompt

        # PHASE 1: Prompt Enhancement
        if not skip_prompt_enhancement:
            print("\n" + "=" * 70)
            print("PHASE 1: PROMPT ENHANCEMENT")
            print("=" * 70)
            self.enhanced_prompt = self.prompt_enhancer.enhance_prompt(user_prompt)
        else:
            print("\n⏭️  Skipping prompt enhancement")
            self.enhanced_prompt = user_prompt

        # PHASE 2: Planning
        print("\n" + "=" * 70)
        print("PHASE 2: PLANNING")
        print("=" * 70)
        self.plan = self.planner.create_plan(self.enhanced_prompt)

        # PHASE 3: Plan Enhancement
        if not skip_plan_enhancement:
            print("\n" + "=" * 70)
            print("PHASE 3: PLAN ENHANCEMENT")
            print("=" * 70)
            self.enhanced_plan = self.plan_enhancer.enhance_plan(self.plan)
        else:
            print("\n⏭️  Skipping plan enhancement")
            self.enhanced_plan = self.plan

        # PHASE 4: Implementation
        print("\n" + "=" * 70)
        print("PHASE 4: IMPLEMENTATION")
        print("=" * 70)
        self.implementation_result = self.coder.execute_plan(self.enhanced_plan)

        # PHASE 5: Validation and Iterative Fixing
        print("\n" + "=" * 70)
        print("PHASE 5: VALIDATION")
        print("=" * 70)

        fix_iteration = 0
        while fix_iteration < max_fix_iterations:
            self.validation_result = self.validator.validate_results(
                self.enhanced_plan,
                self.implementation_result
            )

            # Display validation results
            self._display_validation_results(self.validation_result)

            # Check if fixes are needed
            if not self.validation_result.get("requires_fix", False):
                print("\n✅ Validation passed! No fixes needed.")
                break

            fix_iteration += 1
            if fix_iteration >= max_fix_iterations:
                print(f"\n⚠️  Reached maximum fix iterations ({max_fix_iterations})")
                print("Some issues may remain. Manual review recommended.")
                break

            # Generate fix instructions
            print(f"\n🔧 Fix Iteration {fix_iteration}/{max_fix_iterations}")
            fix_instructions = self.validator.generate_fix_instructions(
                self.validation_result
            )

            # Re-execute with fixes
            print("\n" + "=" * 70)
            print(f"RE-IMPLEMENTATION (Attempt {fix_iteration})")
            print("=" * 70)

            # Reset coder conversation and apply fixes
            self.coder.reset_conversation()
            self.implementation_result = self.coder.execute_plan(
                f"FIX THE FOLLOWING ISSUES:\n\n{fix_instructions}\n\n"
                f"Original Plan for reference:\n{self.enhanced_plan}"
            )

        # PHASE 6: Summary
        print("\n" + "=" * 70)
        print("WORKFLOW COMPLETE")
        print("=" * 70)

        workflow_results = {
            "user_prompt": user_prompt,
            "enhanced_prompt": self.enhanced_prompt,
            "plan": self.plan,
            "enhanced_plan": self.enhanced_plan,
            "implementation_result": self.implementation_result,
            "validation_result": self.validation_result,
            "output_directory": str(self.file_ops.working_directory),
            "fix_iterations": fix_iteration,
            "final_status": self.validation_result.get("status", "UNKNOWN")
        }

        # Log workflow completion
        self.logger.log_workflow_complete(
            status=workflow_results["final_status"],
            output_directory=workflow_results["output_directory"],
            validation_score=self.validation_result.get("score", 0)
        )

        # Save workflow results
        self._save_workflow_results(workflow_results)

        # Display summary
        self._display_workflow_summary(workflow_results)

        # Play completion sound
        if workflow_results["final_status"] == "PASS":
            print("\n🔔 Playing success sound...")
            play_completion_sound()
        else:
            print("\n🔔 Playing completion sound...")
            play_error_sound()

        # Print log summary
        log_summary = self.logger.get_summary()
        print(f"\n📊 Log Summary:")
        print(f"   Total Entries: {log_summary['total_entries']}")
        print(f"   LLM Requests: {log_summary['llm_requests']}")
        print(f"   Tool Calls: {log_summary['tool_calls']}")
        print(f"   Duration: {log_summary['duration']:.1f}s")
        print(f"   Log File: {self.logger.log_file}")

        return workflow_results

    def _display_validation_results(self, validation_result: dict):
        """Display validation results in a readable format."""
        print("\n📊 VALIDATION RESULTS")
        print("-" * 70)

        status = validation_result.get("status", "UNKNOWN")
        score = validation_result.get("score", 0)

        if status == "PASS":
            print(f"✅ Status: {status} (Score: {score}/100)")
        else:
            print(f"❌ Status: {status} (Score: {score}/100)")

        passed = validation_result.get("passed_checks", [])
        if passed:
            print(f"\n✅ Passed Checks ({len(passed)}):")
            for check in passed:
                print(f"   • {check}")

        failed = validation_result.get("failed_checks", [])
        if failed:
            print(f"\n❌ Failed Checks ({len(failed)}):")
            for check in failed:
                print(f"   • {check}")

        critical = validation_result.get("critical_issues", [])
        if critical:
            print(f"\n🔴 Critical Issues ({len(critical)}):")
            for issue in critical:
                print(f"   • {issue}")

        suggestions = validation_result.get("suggestions", [])
        if suggestions:
            print(f"\n💡 Suggestions ({len(suggestions)}):")
            for suggestion in suggestions:
                print(f"   • {suggestion}")

        print("-" * 70)

    def _display_workflow_summary(self, results: dict):
        """Display workflow summary."""
        print("\n📋 WORKFLOW SUMMARY")
        print("=" * 70)
        print(f"User Prompt: {results['user_prompt'][:100]}...")
        print(f"Output Directory: {results['output_directory']}")
        print(f"Fix Iterations: {results['fix_iterations']}")
        print(f"Final Status: {results['final_status']}")
        print(f"Final Score: {results['validation_result'].get('score', 0)}/100")
        print("=" * 70)

        if results['final_status'] == "PASS":
            print("\n🎉 SUCCESS! Your project is ready!")
            print(f"📁 Location: {results['output_directory']}")
            print("\n📖 Next steps:")
            print("   1. Navigate to the output directory")
            print("   2. Run: npm install (or pip install -r requirements.txt)")
            print("   3. Run: npm run dev (or python main.py)")
        else:
            print("\n⚠️  Project created with some issues")
            print("Please review the validation results above for details")
            print(f"📁 Location: {results['output_directory']}")

    def _save_workflow_results(self, results: dict):
        """Save workflow results to a JSON file."""
        try:
            results_file = self.file_ops.working_directory / "workflow_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Workflow results saved to: {results_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save workflow results: {e}")

    def load_prompt_from_file(self, filepath: Path) -> str:
        """
        Load prompt from a file.

        Args:
            filepath: Path to prompt file

        Returns:
            Prompt content
        """
        try:
            return filepath.read_text(encoding="utf-8")
        except Exception as e:
            raise RuntimeError(f"Could not load prompt from {filepath}: {e}")
