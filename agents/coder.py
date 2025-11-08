"""Coder Agent - Executes the implementation plan."""
import re
from typing import List, Dict, Any
from .base_agent import BaseAgent
from ..core import FileOperations
from ..utils import load_prompt


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

        # Run execution loop
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

    def _parse_and_execute_actions(self, response: str) -> List[Dict[str, Any]]:
        """Parse and execute actions from the agent's response."""
        results = []

        # Parse BASH commands
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
                print(f"📤 Output: {result['stdout'][:500]}")
            if result["stderr"]:
                print(f"⚠️  Error: {result['stderr'][:500]}")

        # Parse WRITE_FILE commands
        write_pattern = r'WRITE_FILE:\s*(.+?)\n```(?:\w+)?\n(.+?)```'
        write_commands = re.findall(write_pattern, response, re.DOTALL)

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

        # Parse READ_FILE commands
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

        return results_message
