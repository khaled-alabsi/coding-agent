"""Coder Agent - Executes the implementation plan."""
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from .base_agent import BaseAgent

from core.file_operations import FileOperations
from utils import load_prompt
from tools import ToolRunner


class CoderAgent(BaseAgent):
    """Executes code based on the plan."""

    def __init__(self, config, llm_client, file_ops: FileOperations):
        """
        Initialize the coder agent.

        Args:
            config: Agent configuration
            llm_client: Shared LLM client
            file_ops: File operations handler
        """
        super().__init__(config, llm_client)
        self.file_ops = file_ops
        self._tool_runner = ToolRunner(llm_client, config, agent_name=self.agent_name)

    def set_tools_dir(self, tools_dir: Path) -> None:
        """Set directory where tool I/O snapshots are stored."""
        self._tool_runner.set_tools_dir(Path(tools_dir))

    @property
    def agent_name(self) -> str:
        return "Coder"

    @property
    def system_prompt(self) -> str:
        return load_prompt("coder")

    def execute_plan(self, plan: str) -> str:
        """
        Execute the implementation plan.

        Args:
            plan: Enhanced execution plan

        Returns:
            Summary of execution results
        """
        print(f"\n💻 Executing implementation plan...")
        print(f"Working directory: {self.file_ops.working_directory}")

        # Start execution
        self.chat(
            f"""Execute this plan step by step in the working directory.

Working Directory: {self.file_ops.working_directory}

PLAN:
{plan}

Start implementing now. Create all files as specified in the plan.""",
            display=False
        )

        # STEP 2: Run execution loop (iterate until COMPLETE or max iterations)
        iteration = 0
        max_iterations = self.config.max_iterations

        while iteration < max_iterations:
            iteration += 1

            last_response = self.get_last_response()
            if not last_response:
                break

            print(f"\n{'='*70}")
            print(f"Iteration {iteration}/{max_iterations}")
            print(f"{'='*70}")
            print(f"\n🤖 Coder: {last_response[:500]}...")

            # Check if complete
            if "COMPLETE" in last_response:
                print(f"\n✅ Coder completed implementation!")
                return last_response

            # Execute actions from response
            action_results = self._parse_and_execute_actions(last_response)

            # Send results back to agent
            if action_results:
                results_message = self._format_action_results(action_results)
                self.chat(results_message, display=False)
            else:
                # No actions found, might need clarification
                break

        print(f"\n⚠️  Reached maximum iterations ({max_iterations})")
        return self.get_last_response() or "Execution incomplete"

    def execute_from_prompt(self, user_prompt: str) -> str:
        """Drive the build starting from a raw user prompt.

        The agent may choose to invoke tools to enhance the prompt,
        create a plan, and/or enhance the plan before implementation.
        """
        intro = (
            "You are given a raw user request. First decide if it needs enhancement,"
            " whether a plan is present or required, and whether that plan needs"
            " enhancement. Use TOOL calls to perform these actions as needed, then"
            " proceed with implementation using BASH/WRITE_FILE/READ_FILE."
            "\n\nUSER REQUEST:\n" + user_prompt
        )
        # Kick off the conversation
        self.chat(intro, display=False)

        iteration = 0
        max_iterations = self.config.max_iterations

        while iteration < max_iterations:
            iteration += 1
            last_response = self.get_last_response()
            if not last_response:
                # Log to file: no response received
                if hasattr(self, 'llm_client') and hasattr(self.llm_client, 'logger') and self.llm_client.logger:
                    self.llm_client.logger.log_event(
                        event_type="iteration_no_response",
                        agent=self.agent_name,
                        data={"iteration": iteration},
                        message=f"No response in iteration {iteration}, breaking loop"
                    )
                break

            print(f"\n{'='*70}")
            print(f"Iteration {iteration}/{max_iterations}")
            print(f"{'='*70}")
            print(f"\n🤖 Coder: {last_response[:500]}...")

            # Log to file: iteration state
            if hasattr(self, 'llm_client') and hasattr(self.llm_client, 'logger') and self.llm_client.logger:
                self.llm_client.logger.log_event(
                    event_type="iteration_progress",
                    agent=self.agent_name,
                    data={
                        "iteration": iteration,
                        "max_iterations": max_iterations,
                        "response_preview": last_response[:200],
                        "has_complete": "COMPLETE" in last_response
                    },
                    message=f"Iteration {iteration}/{max_iterations}"
                )

            if "COMPLETE" in last_response:
                print(f"\n✅ Coder completed implementation!")
                # Log to file: completion detected
                if hasattr(self, 'llm_client') and hasattr(self.llm_client, 'logger') and self.llm_client.logger:
                    self.llm_client.logger.log_event(
                        event_type="coder_complete",
                        agent=self.agent_name,
                        data={"iteration": iteration},
                        message=f"Coder marked COMPLETE at iteration {iteration}"
                    )
                return last_response

            # Execute any actions (tools, shell, file I/O)
            action_results = self._parse_and_execute_actions(last_response)

            # Check if planning tools were used - if so, switch to implementation phase
            if action_results:
                planning_tools_used = any(
                    r.get("type") == "tool" and r.get("tool") in ["ENHANCE_PROMPT", "CREATE_PLAN", "ENHANCE_PLAN"]
                    for r in action_results
                )
                if planning_tools_used and self._tool_runner._phase == "preparation":
                    self._tool_runner.switch_to_implementation_phase()
                results_message = self._format_action_results(action_results)
                self.chat(results_message, display=False)
            else:
                break

        print(f"\n⚠️  Reached maximum iterations ({max_iterations})")
        return self.get_last_response() or "Execution incomplete"

    def _parse_and_execute_actions(self, response: str) -> List[Dict[str, Any]]:
        """Parse and execute actions from the agent's response."""
        results = []

        # Log to file: starting action parsing
        if hasattr(self, 'llm_client') and hasattr(self.llm_client, 'logger') and self.llm_client.logger:
            self.llm_client.logger.log_event(
                event_type="action_parsing_start",
                agent=self.agent_name,
                data={"response_length": len(response)},
                message=f"Starting to parse actions from response ({len(response)} chars)"
            )

        # STEP 1A: Parse BASH commands
        bash_pattern = r'BASH:\s*(.+?)(?=\n(?:BASH:|WRITE_FILE:|READ_FILE:|COMPLETE|$))'
        bash_commands = re.findall(bash_pattern, response, re.DOTALL)

        for command in bash_commands:
            command = command.strip()
            print(f"\n🔧 Executing: {command}")
            result = self.file_ops.execute_bash_command(command, agent_name=self.agent_name)
            results.append({
                "type": "bash",
                "command": command,
                "result": result
            })
            if result["stdout"]:
                print(f"📤 stdout Output: {result['stdout'][:500]}")
            if result["stderr"]:
                print(f"⚠️  Error: {result['stderr'][:500]}")

        # STEP 1B: Parse WRITE_FILE commands (robust to missing closing code fences)
        fenced_pattern = r'WRITE_FILE:\s*(.+?)\n```(?:\w+)?\n([\s\S]*?)```'
        write_commands = re.findall(fenced_pattern, response, re.DOTALL)

        # Fallback: no closing ```; capture until next marker or end
        consumed_spans = []
        for m in re.finditer(fenced_pattern, response, re.DOTALL):
            consumed_spans.append((m.start(), m.end()))

        def overlaps(i0, i1, spans):
            for s0, s1 in spans:
                if not (i1 <= s0 or i0 >= s1):
                    return True
            return False

        fallback_pattern = re.compile(
            r'WRITE_FILE:\s*(.+?)\n([\s\S]*?)(?=\n(?:BASH:|WRITE_FILE:|READ_FILE:|TOOL:|COMPLETE|$))',
            re.DOTALL,
        )
        for m in fallback_pattern.finditer(response):
            if overlaps(m.start(), m.end(), consumed_spans):
                continue
            write_commands.append((m.group(1), m.group(2)))

        for filepath, content in write_commands:
            filepath = filepath.strip()
            content = content.strip()
            print(f"\n📝 Writing file: {filepath} ({len(content)} chars)")
            result = self.file_ops.write_file(filepath, content, agent_name=self.agent_name)
            results.append({
                "type": "write_file",
                "filepath": filepath,
                "result": result
            })
            print(f"✅ {result['message']}")

        # STEP 1C: Parse READ_FILE commands
        read_pattern = r'READ_FILE:\s*(.+?)(?=\n|$)'
        read_commands = re.findall(read_pattern, response)

        for filepath in read_commands:
            filepath = filepath.strip()
            print(f"\n📖 Reading file: {filepath}")
            result = self.file_ops.read_file(filepath, agent_name=self.agent_name)
            results.append({
                "type": "read_file",
                "filepath": filepath,
                "result": result
            })
            if result["success"]:
                print(f"✅ Read {len(result['content'])} characters")
            else:
                print(f"❌ {result['message']}")

        # STEP 1D: Parse and execute TOOL invocations via ToolRunner
        tool_results = self._tool_runner.run_calls(response)
        for r in tool_results:
            # Mirror logs for consistency with previous behavior
            tool = r.get("tool")
            if "error" in r:
                print(f"❌ TOOL {tool} failed: {r['error']}")
            else:
                out = r.get("output", "")
                print(f"✅ TOOL {tool} completed ({len(out)} chars)")
        results.extend(tool_results)

        # Log to file: action parsing complete
        if hasattr(self, 'llm_client') and hasattr(self.llm_client, 'logger') and self.llm_client.logger:
            action_summary = {
                "total_actions": len(results),
                "bash_commands": sum(1 for r in results if r.get("type") == "bash"),
                "files_written": sum(1 for r in results if r.get("type") == "write_file"),
                "files_read": sum(1 for r in results if r.get("type") == "read_file"),
                "tool_calls": sum(1 for r in results if r.get("type") == "tool"),
            }
            self.llm_client.logger.log_event(
                event_type="action_parsing_complete",
                agent=self.agent_name,
                data=action_summary,
                message=f"Parsed and executed {len(results)} actions"
            )

        # always append summary
        results.append({
            "type": "summary",
            "message": "Completed action batch",
            "actions_executed": len(results)
        })
        return results

    def _format_action_results(self, action_results: List[Dict[str, Any]]) -> str:
        """Format action results for sending back to the agent."""
        results_message = "Execution Results:\n\n"

        for action in action_results:
            if action["type"] == "bash":
                results_message += f"Command: {action['command']}\n"
                results_message += f"Output: {action['result']['stdout']}\n"
                if action['result']['stderr']:
                    results_message += f"Error: {action['result']['stderr']}\n"
                results_message += f"Success: {action['result']['success']}\n\n"

            elif action["type"] == "write_file":
                results_message += f"Write File: {action['filepath']}\n"
                results_message += f"Result: {action['result']['message']}\n\n"

            elif action["type"] == "read_file":
                results_message += f"Read File: {action['filepath']}\n"
                if action['result']['success']:
                    # Truncate long content
                    content = action['result']['content']
                    if len(content) > 1000:
                        content = content[:1000] + "\n... (truncated)"
                    results_message += f"Content:\n{content}\n\n"
                else:
                    results_message += f"Error: {action['result']['message']}\n\n"

            elif action["type"] == "tool":
                tool = action.get("tool")
                if action.get("error"):
                    results_message += f"Tool: {tool}\nError: {action['error']}\n\n"
                else:
                    # Truncate overly long tool outputs
                    out = action.get("output", "")
                    if len(out) > 2000:
                        out = out[:2000] + "\n... (truncated)"
                    results_message += f"Tool: {tool}\nOutput:\n{out}\n\n"

        return results_message

    # (No coder-specific tool snapshot helpers; handled by ToolRunner)
