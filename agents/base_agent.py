"""Base agent class with common functionality."""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

from config import AgentConfig
from core.llm_client import LLMClient
from utils import strip_thinking_tags, HistoryCompactor


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, config: AgentConfig, llm_client: LLMClient):
        """
        Initialize the base agent.

        Args:
            config: Agent configuration
            llm_client: Shared LLM client
        """
        self.config = config
        self.llm_client = llm_client
        self.messages: List[Dict[str, str]] = []
        self.history_compactor = HistoryCompactor(config, llm_client)

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Return the agent's name."""
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the agent's system prompt."""
        pass

    def chat(self, user_message: str, display: bool = True) -> str:
        """
        Send a message and get a response.

        Args:
            user_message: Message from user
            display: Whether to display the conversation

        Returns:
            Agent's response
        """
        self.messages.append({
            "role": "user",
            "content": user_message
        })

        self._compact_history_if_needed()

        if display:
            print(f"\n{'='*70}")
            print(f"🤖 {self.agent_name}")
            print(f"{'='*70}")

        try:
            print(f"\n⏳ {self.agent_name}: Waiting for LLM response...")

            # Log to file: waiting for response
            if hasattr(self.llm_client, 'logger') and self.llm_client.logger:
                self.llm_client.logger.log_event(
                    event_type="llm_waiting",
                    agent=self.agent_name,
                    message=f"Waiting for LLM response (context: {len(self.messages)} messages)"
                )

            response = self.llm_client.chat(
                messages=self.messages,
                system_message=self.system_prompt,
                agent_name=self.agent_name  # Pass agent name for logging
            )

            print(f"✅ {self.agent_name}: Received LLM response ({len(response)} chars)")

            # Log to file: response received
            if hasattr(self.llm_client, 'logger') and self.llm_client.logger:
                self.llm_client.logger.log_event(
                    event_type="llm_response_received",
                    agent=self.agent_name,
                    data={
                        "response_length": len(response),
                        "has_content": bool(response)
                    },
                    message=f"Received LLM response ({len(response)} chars)"
                )

            # Strip thinking tags from response before storing/returning
            # (Full response with thinking is already logged in llm_client)
            cleaned_response = strip_thinking_tags(response)

            self.messages.append({
                "role": "assistant",
                "content": cleaned_response
            })

            if display:
                print(f"\n{cleaned_response}\n")

            return cleaned_response

        except Exception as e:
            error_msg = f"Error in {self.agent_name}: {str(e)}"
            print(f"\n❌ {error_msg}")

            # Log the error to logger if available
            if hasattr(self.llm_client, 'logger') and self.llm_client.logger:
                self.llm_client.logger.log_event(
                    event_type="agent_error",
                    agent=self.agent_name,
                    data={"error": str(e), "type": type(e).__name__}
                )

            return error_msg

    def reset_conversation(self):
        """Clear the conversation history."""
        self.messages = []

    def get_last_response(self) -> Optional[str]:
        """Get the last assistant response."""
        for msg in reversed(self.messages):
            if msg["role"] == "assistant":
                return msg["content"]
        return None

    def add_context(self, context: str):
        """Add context to the conversation without requiring a response."""
        self.messages.append({
            "role": "user",
            "content": context
        })
        self._compact_history_if_needed()

    def _compact_history_if_needed(self):
        """Summarize older history if the context window is at risk."""
        if not self.messages:
            return

        result = self.history_compactor.compact(
            self.messages,
            system_prompt=self.system_prompt,
            context_window=self.config.context_window
        )
        if result.compacted:
            self.messages = result.messages
