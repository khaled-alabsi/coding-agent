"""File operations for the agent system."""
import subprocess
from pathlib import Path
from typing import Dict, Any
from ..config import AgentConfig


class FileOperations:
    """Handle file operations and command execution."""

    def __init__(self, config: AgentConfig):
        """
        Initialize file operations.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.working_directory = config.output_dir

    def set_working_directory(self, path: Path):
        """Set the working directory for operations."""
        self.working_directory = Path(path)
        self.working_directory.mkdir(parents=True, exist_ok=True)

    def execute_bash_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a bash command.

        Args:
            command: Command to execute

        Returns:
            Dict with stdout, stderr, returncode, and success flag
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.config.command_timeout,
                cwd=self.working_directory
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Command timed out after {self.config.command_timeout} seconds",
                "returncode": -1,
                "success": False
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "success": False
            }

    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """
        Write content to a file.

        Args:
            filepath: Path to file (relative to working directory)
            content: Content to write

        Returns:
            Dict with success flag and message
        """
        try:
            file_path = Path(filepath)
            if not file_path.is_absolute():
                file_path = self.working_directory / file_path

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")

            return {
                "success": True,
                "message": f"Successfully wrote to {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error writing file: {str(e)}"
            }

    def read_file(self, filepath: str) -> Dict[str, Any]:
        """
        Read content from a file.

        Args:
            filepath: Path to file (relative to working directory)

        Returns:
            Dict with success flag, content, and message
        """
        try:
            file_path = Path(filepath)
            if not file_path.is_absolute():
                file_path = self.working_directory / file_path

            if not file_path.exists():
                return {
                    "success": False,
                    "content": "",
                    "message": f"File not found: {file_path}"
                }

            content = file_path.read_text(encoding="utf-8")
            return {
                "success": True,
                "content": content,
                "message": f"Successfully read {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "content": "",
                "message": f"Error reading file: {str(e)}"
            }

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
