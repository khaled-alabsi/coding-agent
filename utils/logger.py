"""Comprehensive logging system for all agent interactions."""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class AgentLogger:
    """Logs all LLM requests/responses and tool calls."""

    def __init__(self, log_file: Path):
        """
        Initialize the logger.

        Args:
            log_file: Path to the log file
        """
        self.log_file = log_file
        self.entries: List[Dict[str, Any]] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = time.time()

        # Create log file directory
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize log file
        self._write_header()

    def _write_header(self):
        """Write log file header."""
        header = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "entries": []
        }
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(header, f, indent=2, ensure_ascii=False)

    def log_llm_request(
        self,
        agent_name: str,
        messages: List[Dict[str, str]],
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model: Optional[str] = None,
    ) -> str:
        """
        Log an outgoing LLM request.

        Args:
            agent_name: Name of the agent making the request
            messages: Messages sent to LLM
            system_message: System message if any
            temperature: Temperature parameter
            max_tokens: Max tokens parameter

        Returns:
            Request ID for matching with response
        """
        request_id = f"{agent_name}_{len(self.entries)}"
        timestamp = time.time() - self.start_time

        entry = {
            "id": request_id,
            "type": "llm_request",
            "timestamp": timestamp,
            "time_human": datetime.now().isoformat(),
            "agent": agent_name,
            "data": {
                "system_message": system_message,
                "messages": messages,
                "parameters": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "model": model,
                },
            }
        }

        self.entries.append(entry)
        self._append_to_file(entry)
        return request_id

    def log_llm_response(
        self,
        request_id: str,
        agent_name: str,
        response: str,
        tokens_used: Optional[int] = None
    ):
        """
        Log an incoming LLM response.

        Args:
            request_id: ID of the request this responds to
            agent_name: Name of the agent receiving the response
            response: Response content
            tokens_used: Number of tokens used (if available)
        """
        timestamp = time.time() - self.start_time

        entry = {
            "id": f"{request_id}_response",
            "type": "llm_response",
            "timestamp": timestamp,
            "time_human": datetime.now().isoformat(),
            "agent": agent_name,
            "request_id": request_id,
            "data": {
                "response": response,
                "tokens_used": tokens_used
            }
        }

        self.entries.append(entry)
        self._append_to_file(entry)

    def log_tool_call(
        self,
        agent_name: str,
        tool_name: str,
        tool_input: Any
    ) -> str:
        """
        Log a tool call.

        Args:
            agent_name: Name of the agent calling the tool
            tool_name: Name of the tool being called
            tool_input: Input to the tool

        Returns:
            Tool call ID for matching with result
        """
        call_id = f"{agent_name}_{tool_name}_{len(self.entries)}"
        timestamp = time.time() - self.start_time

        entry = {
            "id": call_id,
            "type": "tool_call",
            "timestamp": timestamp,
            "time_human": datetime.now().isoformat(),
            "agent": agent_name,
            "data": {
                "tool": tool_name,
                "input": tool_input
            }
        }

        self.entries.append(entry)
        self._append_to_file(entry)
        return call_id

    def log_tool_result(
        self,
        call_id: str,
        agent_name: str,
        tool_name: str,
        tool_output: Any,
        success: bool = True,
        error: Optional[str] = None
    ):
        """
        Log a tool result.

        Args:
            call_id: ID of the tool call this is the result for
            agent_name: Name of the agent
            tool_name: Name of the tool
            tool_output: Output from the tool
            success: Whether the tool call succeeded
            error: Error message if failed
        """
        timestamp = time.time() - self.start_time

        entry = {
            "id": f"{call_id}_result",
            "type": "tool_result",
            "timestamp": timestamp,
            "time_human": datetime.now().isoformat(),
            "agent": agent_name,
            "call_id": call_id,
            "data": {
                "tool": tool_name,
                "output": tool_output,
                "success": success,
                "error": error
            }
        }

        self.entries.append(entry)
        self._append_to_file(entry)

    def log_agent_start(self, agent_name: str, context: Optional[str] = None):
        """Log when an agent starts working."""
        timestamp = time.time() - self.start_time

        entry = {
            "id": f"{agent_name}_start_{len(self.entries)}",
            "type": "agent_start",
            "timestamp": timestamp,
            "time_human": datetime.now().isoformat(),
            "agent": agent_name,
            "data": {
                "context": context
            }
        }

        self.entries.append(entry)
        self._append_to_file(entry)

    def log_agent_complete(
        self,
        agent_name: str,
        result: Optional[str] = None,
        success: bool = True
    ):
        """Log when an agent completes its work."""
        timestamp = time.time() - self.start_time

        entry = {
            "id": f"{agent_name}_complete_{len(self.entries)}",
            "type": "agent_complete",
            "timestamp": timestamp,
            "time_human": datetime.now().isoformat(),
            "agent": agent_name,
            "data": {
                "result": result,
                "success": success
            }
        }

        self.entries.append(entry)
        self._append_to_file(entry)

    def log_workflow_start(self, user_prompt: str):
        """Log when the workflow starts."""
        timestamp = time.time() - self.start_time

        entry = {
            "id": "workflow_start",
            "type": "workflow_start",
            "timestamp": timestamp,
            "time_human": datetime.now().isoformat(),
            "data": {
                "user_prompt": user_prompt
            }
        }

        self.entries.append(entry)
        self._append_to_file(entry)

    def log_workflow_complete(
        self,
        status: str,
        output_directory: str,
        validation_score: int
    ):
        """Log when the workflow completes."""
        timestamp = time.time() - self.start_time

        entry = {
            "id": "workflow_complete",
            "type": "workflow_complete",
            "timestamp": timestamp,
            "time_human": datetime.now().isoformat(),
            "data": {
                "status": status,
                "output_directory": output_directory,
                "validation_score": validation_score,
                "total_duration": timestamp
            }
        }

        self.entries.append(entry)
        self._append_to_file(entry)

    def log_event(
        self,
        event_type: str,
        agent: str = "system",
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ):
        """
        Log a generic event.

        Args:
            event_type: Type of event (e.g., "response_received", "action_parsing", "error")
            agent: Agent name (default: "system")
            data: Additional data for the event
            message: Optional message describing the event
        """
        timestamp = time.time() - self.start_time

        entry = {
            "id": f"{agent}_{event_type}_{len(self.entries)}",
            "type": event_type,
            "timestamp": timestamp,
            "time_human": datetime.now().isoformat(),
            "agent": agent,
            "data": data or {}
        }

        if message:
            entry["data"]["message"] = message

        self.entries.append(entry)
        self._append_to_file(entry)

    def _append_to_file(self, entry: Dict[str, Any]):
        """Append an entry to the log file."""
        try:
            # Read current log
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)

            # Append new entry
            log_data["entries"].append(entry)

            # Write back
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            # Fallback: write entries directly
            print(f"Warning: Could not append to log file: {e}")

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the log."""
        llm_requests = sum(1 for e in self.entries if e["type"] == "llm_request")
        llm_responses = sum(1 for e in self.entries if e["type"] == "llm_response")
        tool_calls = sum(1 for e in self.entries if e["type"] == "tool_call")
        tool_results = sum(1 for e in self.entries if e["type"] == "tool_result")

        return {
            "total_entries": len(self.entries),
            "llm_requests": llm_requests,
            "llm_responses": llm_responses,
            "tool_calls": tool_calls,
            "tool_results": tool_results,
            "duration": time.time() - self.start_time
        }
