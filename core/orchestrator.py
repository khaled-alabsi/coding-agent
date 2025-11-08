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
        self.session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"agent_log_{self.session_timestamp}.json"
        self.logger = AgentLogger(config.project_dir / log_filename)

        # Create workflow steps directory for clean outputs
        self.steps_dir = config.project_dir / f"workflow_steps_{self.session_timestamp}"
        self.steps_dir.mkdir(exist_ok=True)

        # Create README for the steps directory
        self._create_steps_readme()

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
        print(f"📂 Step results: {self.steps_dir}")

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

        # Save original user prompt
        self._save_step_result(0, "user_prompt", user_prompt)

        # PHASE 1: Prompt Enhancement
        if not skip_prompt_enhancement:
            print("\n" + "=" * 70)
            print("PHASE 1: PROMPT ENHANCEMENT")
            print("=" * 70)
            self.enhanced_prompt = self.prompt_enhancer.enhance_prompt(user_prompt)
            self._save_step_result(1, "prompt_enhanced", self.enhanced_prompt)
        else:
            print("\n⏭️  Skipping prompt enhancement")
            self.enhanced_prompt = user_prompt

        # PHASE 2: Planning
        print("\n" + "=" * 70)
        print("PHASE 2: PLANNING")
        print("=" * 70)
        self.plan = self.planner.create_plan(self.enhanced_prompt)
        self._save_step_result(2, "plan", self.plan)

        # PHASE 3: Plan Enhancement
        if not skip_plan_enhancement:
            print("\n" + "=" * 70)
            print("PHASE 3: PLAN ENHANCEMENT")
            print("=" * 70)
            self.enhanced_plan = self.plan_enhancer.enhance_plan(self.plan)
            self._save_step_result(3, "plan_enhanced", self.enhanced_plan)
        else:
            print("\n⏭️  Skipping plan enhancement")
            self.enhanced_plan = self.plan

        # PHASE 4: Implementation
        print("\n" + "=" * 70)
        print("PHASE 4: IMPLEMENTATION")
        print("=" * 70)
        self.implementation_result = self.coder.execute_plan(self.enhanced_plan)
        self._save_step_result(4, "implementation_result", self.implementation_result)

        # PHASE 5: Validation and Iterative Fixing
        print("\n" + "=" * 70)
        print("PHASE 5: VALIDATION")
        print("=" * 70)

        fix_iteration = 0
        iteration_history = []  # Track all iterations for fail log

        while fix_iteration < max_fix_iterations:
            self.validation_result = self.validator.validate_results(
                self.enhanced_plan,
                self.implementation_result
            )

            # Save validation result
            validation_json = json.dumps(self.validation_result, indent=2, ensure_ascii=False)
            if fix_iteration == 0:
                self._save_step_result(5, "validation_result", validation_json, "json")
            else:
                self._save_step_result(5 + fix_iteration, f"validation_result_iteration_{fix_iteration}", validation_json, "json")

            # Display validation results
            self._display_validation_results(self.validation_result)

            # Track this iteration
            iteration_data = {
                "iteration": fix_iteration,
                "validation_result": self.validation_result.copy(),
                "implementation_result": self.implementation_result,
                "timestamp": datetime.now().isoformat()
            }

            # Check if fixes are needed
            if not self.validation_result.get("requires_fix", False):
                print("\n✅ Validation passed! No fixes needed.")
                iteration_data["outcome"] = "PASSED"
                iteration_history.append(iteration_data)
                break

            fix_iteration += 1
            if fix_iteration >= max_fix_iterations:
                print(f"\n⚠️  Reached maximum fix iterations ({max_fix_iterations})")
                print("Some issues may remain. Manual review recommended.")

                # Save comprehensive fail log
                iteration_data["outcome"] = "MAX_RETRIES_REACHED"
                iteration_history.append(iteration_data)
                self._save_fail_log(iteration_history, user_prompt, max_fix_iterations)
                break

            # Generate fix instructions
            print(f"\n🔧 Fix Iteration {fix_iteration}/{max_fix_iterations}")
            fix_instructions = self.validator.generate_fix_instructions(
                self.validation_result
            )

            iteration_data["outcome"] = "REQUIRES_FIX"
            iteration_data["fix_instructions"] = fix_instructions
            iteration_history.append(iteration_data)

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

            # Save the fixed implementation result
            self._save_step_result(4 + fix_iteration, f"implementation_result_fixed_{fix_iteration}", self.implementation_result)

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
        print(f"\n📂 Files Generated:")
        print(f"   Workflow Steps: {self.steps_dir}")
        print(f"   Detailed Log: {self.logger.log_file}")

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

    def _create_steps_readme(self):
        """Create a README in the steps directory explaining the files."""
        readme_content = """# Workflow Step Results

This directory contains the clean output from each agent in the multi-agent workflow.
These files make it easy to review what each agent produced without parsing through the detailed JSON log.

## Files

- **0_user_prompt.md** - Original user prompt
- **1_prompt_enhanced.md** - Enhanced prompt (from Prompt Enhancer Agent)
- **2_plan.md** - Execution plan (from Planner Agent)
- **3_plan_enhanced.md** - Enhanced and validated plan (from Plan Enhancer Agent)
- **4_implementation_result.md** - Implementation output (from Coder Agent)
- **5_validation_result.json** - Validation results (from Result Validator Agent)

If fix iterations occurred:
- **4_implementation_result_fixed_N.md** - Fixed implementation (iteration N)
- **5_validation_result_iteration_N.json** - Validation after fix (iteration N)

## Usage

1. **Review the workflow progression** - Read files in order (0 → 1 → 2 → 3 → 4 → 5)
2. **Check validation** - Look at validation_result.json for quality score and issues
3. **See fixes applied** - If fixes were needed, compare original vs fixed implementations

## Related Files

- **agent_log_{timestamp}.json** - Detailed log with all LLM requests/responses and tool calls
- **workflow_results.json** - Complete workflow summary with all results

## Notes

- Step results contain CLEAN output (thinking tags removed)
- Full LLM responses WITH thinking tags are in the detailed log file
- This separation makes it easier to review the actual deliverables vs the reasoning process
"""
        try:
            readme_path = self.steps_dir / "README.md"
            readme_path.write_text(readme_content, encoding='utf-8')
        except Exception as e:
            print(f"⚠️  Could not create steps README: {e}")

    def _save_step_result(self, step_number: int, step_name: str, content: str, extension: str = "md"):
        """
        Save a workflow step's output to a file for easy reading.

        Args:
            step_number: Step number (1, 2, 3, etc.)
            step_name: Name of the step (e.g., "prompt_enhanced")
            content: Content to save
            extension: File extension (default: md)
        """
        try:
            filename = f"{step_number}_{step_name}.{extension}"
            filepath = self.steps_dir / filename
            filepath.write_text(content, encoding='utf-8')
            print(f"   💾 Saved to: {filename}")
        except Exception as e:
            print(f"   ⚠️  Could not save step result: {e}")

    def _save_fail_log(self, iteration_history: list, user_prompt: str, max_iterations: int):
        """
        Save comprehensive fail log when max retries is reached.

        Args:
            iteration_history: List of all iteration data
            user_prompt: Original user prompt
            max_iterations: Maximum iterations allowed
        """
        try:
            # Create fail log directory
            fail_log_dir = self.config.project_dir / "fail_logs"
            fail_log_dir.mkdir(exist_ok=True)

            # Generate fail log filename
            fail_log_file = fail_log_dir / f"fail_log_{self.session_timestamp}.md"

            # Build comprehensive fail log
            fail_log = self._build_fail_log_content(iteration_history, user_prompt, max_iterations)

            # Save fail log
            fail_log_file.write_text(fail_log, encoding='utf-8')

            # Also save as JSON for programmatic analysis
            fail_log_json = fail_log_dir / f"fail_log_{self.session_timestamp}.json"
            fail_data = {
                "timestamp": self.session_timestamp,
                "user_prompt": user_prompt,
                "max_iterations": max_iterations,
                "total_attempts": len(iteration_history),
                "iteration_history": iteration_history,
                "final_validation": iteration_history[-1]["validation_result"] if iteration_history else {},
                "output_directory": str(self.file_ops.working_directory),
                "workflow_steps_dir": str(self.steps_dir),
                "agent_log": str(self.logger.log_file)
            }
            with open(fail_log_json, 'w', encoding='utf-8') as f:
                json.dump(fail_data, f, indent=2, ensure_ascii=False)

            print(f"\n📋 FAIL LOG SAVED")
            print(f"   Readable: {fail_log_file}")
            print(f"   JSON: {fail_log_json}")

        except Exception as e:
            print(f"\n⚠️  Could not save fail log: {e}")

    def _build_fail_log_content(self, iteration_history: list, user_prompt: str, max_iterations: int) -> str:
        """
        Build the fail log content in markdown format.

        Args:
            iteration_history: List of all iteration data
            user_prompt: Original user prompt
            max_iterations: Maximum iterations allowed

        Returns:
            Fail log content as markdown string
        """
        content = f"""# CODING FAILURE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Session: {self.session_timestamp}

## SUMMARY

**Status**: ❌ FAILED - Reached maximum retry limit ({max_iterations} iterations)
**Total Attempts**: {len(iteration_history)}
**Output Directory**: {self.file_ops.working_directory}
**Workflow Steps**: {self.steps_dir}
**Agent Log**: {self.logger.log_file}

---

## ORIGINAL REQUEST

```
{user_prompt}
```

---

## ITERATION HISTORY

"""

        # Add each iteration
        for iteration in iteration_history:
            content += f"""### Iteration {iteration['iteration']} - {iteration['outcome']}

**Timestamp**: {iteration['timestamp']}

#### Validation Results

"""
            val_result = iteration['validation_result']
            content += f"- **Status**: {val_result.get('status', 'UNKNOWN')}\n"
            content += f"- **Score**: {val_result.get('score', 0)}/100\n"
            content += f"- **Requires Fix**: {val_result.get('requires_fix', False)}\n\n"

            # Failed checks
            failed = val_result.get('failed_checks', [])
            if failed:
                content += f"**❌ Failed Checks ({len(failed)})**:\n"
                for check in failed:
                    content += f"- {check}\n"
                content += "\n"

            # Critical issues
            critical = val_result.get('critical_issues', [])
            if critical:
                content += f"**🔴 Critical Issues ({len(critical)})**:\n"
                for issue in critical:
                    content += f"- {issue}\n"
                content += "\n"

            # Passed checks
            passed = val_result.get('passed_checks', [])
            if passed:
                content += f"**✅ Passed Checks ({len(passed)})**:\n"
                for check in passed:
                    content += f"- {check}\n"
                content += "\n"

            # Suggestions
            suggestions = val_result.get('suggestions', [])
            if suggestions:
                content += f"**💡 Suggestions ({len(suggestions)})**:\n"
                for suggestion in suggestions:
                    content += f"- {suggestion}\n"
                content += "\n"

            # Fix instructions if generated
            if 'fix_instructions' in iteration:
                content += f"""#### Fix Instructions Given

```
{iteration['fix_instructions']}
```

"""

            # Implementation result preview
            impl_preview = iteration['implementation_result'][:500]
            content += f"""#### Implementation Result (Preview)

```
{impl_preview}...
```

"""

            content += "---\n\n"

        # Add final analysis section
        final_validation = iteration_history[-1]['validation_result'] if iteration_history else {}
        content += f"""## FINAL STATE ANALYSIS

### Why It Failed

The coder agent could not resolve all validation issues within {max_iterations} iterations.

**Final Score**: {final_validation.get('score', 0)}/100

**Remaining Issues**:
"""

        # List all final issues
        final_failed = final_validation.get('failed_checks', [])
        final_critical = final_validation.get('critical_issues', [])

        if final_critical:
            content += "\n**Critical Issues**:\n"
            for issue in final_critical:
                content += f"- {issue}\n"

        if final_failed:
            content += "\n**Failed Validation Checks**:\n"
            for check in final_failed:
                content += f"- {check}\n"

        content += f"""

---

## NEXT STEPS TO FIX

1. **Review the iteration history** above to see what the coder tried
2. **Check the output files** in `{self.file_ops.working_directory}`
3. **Look at the final validation** to understand remaining issues
4. **Manual fixes**:
   - Review generated code files
   - Fix critical issues manually
   - Test the application

5. **Configuration tuning** (if needed):
   - Increase `max_fix_iterations` (current: {max_iterations})
   - Check `max_tokens` setting - coder responses may be truncated
   - Review `context_window` - context may be too small

6. **Prompt improvements**:
   - Make requirements more specific
   - Break down complex tasks into smaller parts
   - Provide clearer success criteria

---

## FILES TO REVIEW

### Generated Code
- Location: `{self.file_ops.working_directory}`
- Check files for syntax errors, missing imports, incomplete implementations

### Workflow Steps
- Location: `{self.steps_dir}`
- Review each step's output to understand the workflow

### Detailed Logs
- Agent Log: `{self.logger.log_file}`
- Contains all LLM requests/responses and tool calls

---

## TROUBLESHOOTING

### Common Causes of Failure

1. **Response Truncation**: Coder's output was cut off due to `max_tokens` limit
   - Solution: Increase `max_tokens` in config (current: {self.config.max_tokens})

2. **Context Window Exceeded**: Too much context for the LLM
   - Solution: Increase `context_window` in config (current: {self.config.context_window})

3. **Ambiguous Requirements**: Prompt wasn't specific enough
   - Solution: Enhance the original prompt with more details

4. **Complex Task**: Task too large for single workflow
   - Solution: Break into smaller sub-tasks

5. **Model Limitations**: Local model not capable enough
   - Solution: Try a larger model or Azure OpenAI

### Analysis Tools

Use the context analyzer to check for truncation:

```python
from utils.context_analyzer import ContextAnalyzer

analyzer = ContextAnalyzer()
stats = analyzer.analyze_log_file('{self.logger.log_file}')
analyzer.print_analysis(stats)
```

---

Generated by Azure Code Agent Multi-Agent System
"""

        return content

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
