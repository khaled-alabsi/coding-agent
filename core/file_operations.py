"""File operations for the agent system."""
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING

from config import AgentConfig

if TYPE_CHECKING:
    from utils.logger import AgentLogger


class FileOperations:
    """Handle file operations and command execution."""

    def __init__(self, config: AgentConfig, logger: Optional['AgentLogger'] = None):
        """
        Initialize file operations.

        Args:
            config: Agent configuration
            logger: Optional logger for tracking tool interactions
        """
        self.config = config
        self.logger = logger
        self.working_directory = config.output_dir

    def set_working_directory(self, path: Path):
        """Set the working directory for operations."""
        self.working_directory = Path(path)
        self.working_directory.mkdir(parents=True, exist_ok=True)

    def execute_bash_command(self, command: str, agent_name: str = "unknown") -> Dict[str, Any]:
        """
        Execute a bash command.

        Args:
            command: Command to execute
            agent_name: Name of agent executing command (for logging)

        Returns:
            Dict with stdout, stderr, returncode, and success flag
        """
        # Log the tool call
        call_id = None
        if self.logger:
            call_id = self.logger.log_tool_call(
                agent_name=agent_name,
                tool_name="bash",
                tool_input={"command": command, "cwd": str(self.working_directory)}
            )

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.config.command_timeout,
                cwd=self.working_directory
            )
            output = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0
            }

            # Log the result
            if self.logger and call_id:
                self.logger.log_tool_result(
                    call_id=call_id,
                    agent_name=agent_name,
                    tool_name="bash",
                    tool_output=output,
                    success=output["success"]
                )

            return output
        except subprocess.TimeoutExpired:
            output = {
                "stdout": "",
                "stderr": f"Command timed out after {self.config.command_timeout} seconds",
                "returncode": -1,
                "success": False
            }

            # Log the error
            if self.logger and call_id:
                self.logger.log_tool_result(
                    call_id=call_id,
                    agent_name=agent_name,
                    tool_name="bash",
                    tool_output=output,
                    success=False,
                    error="Timeout"
                )

            return output
        except Exception as e:
            output = {
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "success": False
            }

            # Log the error
            if self.logger and call_id:
                self.logger.log_tool_result(
                    call_id=call_id,
                    agent_name=agent_name,
                    tool_name="bash",
                    tool_output=output,
                    success=False,
                    error=str(e)
                )

            return output

    def write_file(self, filepath: str, content: str, agent_name: str = "unknown") -> Dict[str, Any]:
        """
        Write content to a file.

        Args:
            filepath: Path to file (relative to working directory)
            content: Content to write
            agent_name: Name of agent writing file (for logging)

        Returns:
            Dict with success flag and message
        """
        # Log the tool call
        call_id = None
        if self.logger:
            call_id = self.logger.log_tool_call(
                agent_name=agent_name,
                tool_name="write_file",
                tool_input={"filepath": filepath, "content_length": len(content)}
            )

        try:
            file_path = Path(filepath)
            if not file_path.is_absolute():
                file_path = self.working_directory / file_path

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")

            output = {
                "success": True,
                "message": f"Successfully wrote to {file_path}"
            }

            # Log the result
            if self.logger and call_id:
                self.logger.log_tool_result(
                    call_id=call_id,
                    agent_name=agent_name,
                    tool_name="write_file",
                    tool_output=output,
                    success=True
                )

            return output
        except Exception as e:
            output = {
                "success": False,
                "message": f"Error writing file: {str(e)}"
            }

            # Log the error
            if self.logger and call_id:
                self.logger.log_tool_result(
                    call_id=call_id,
                    agent_name=agent_name,
                    tool_name="write_file",
                    tool_output=output,
                    success=False,
                    error=str(e)
                )

            return output

    def read_file(self, filepath: str, agent_name: str = "unknown") -> Dict[str, Any]:
        """
        Read content from a file.

        Args:
            filepath: Path to file (relative to working directory)
            agent_name: Name of agent reading file (for logging)

        Returns:
            Dict with success flag, content, and message
        """
        # Log the tool call
        call_id = None
        if self.logger:
            call_id = self.logger.log_tool_call(
                agent_name=agent_name,
                tool_name="read_file",
                tool_input={"filepath": filepath}
            )

        try:
            file_path = Path(filepath)
            if not file_path.is_absolute():
                file_path = self.working_directory / file_path

            if not file_path.exists():
                output = {
                    "success": False,
                    "content": "",
                    "message": f"File not found: {file_path}"
                }

                # Log the result
                if self.logger and call_id:
                    self.logger.log_tool_result(
                        call_id=call_id,
                        agent_name=agent_name,
                        tool_name="read_file",
                        tool_output=output,
                        success=False,
                        error="File not found"
                    )

                return output

            content = file_path.read_text(encoding="utf-8")
            output = {
                "success": True,
                "content": content,
                "message": f"Successfully read {file_path}"
            }

            # Log the result
            if self.logger and call_id:
                self.logger.log_tool_result(
                    call_id=call_id,
                    agent_name=agent_name,
                    tool_name="read_file",
                    tool_output={"success": True, "content_length": len(content)},
                    success=True
                )

            return output
        except Exception as e:
            output = {
                "success": False,
                "content": "",
                "message": f"Error reading file: {str(e)}"
            }

            # Log the error
            if self.logger and call_id:
                self.logger.log_tool_result(
                    call_id=call_id,
                    agent_name=agent_name,
                    tool_name="read_file",
                    tool_output=output,
                    success=False,
                    error=str(e)
                )

            return output

    def list_files(self, pattern: str = "*") -> list:
        """
        List files in working directory matching pattern.

        Args:
            pattern: Glob pattern (default: *)

        Returns:
            List of file paths
        """
        try:
            return list(self.working_directory.glob(pattern))
        except Exception:
            return []
