"""Base agent class with common functionality."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..config import AgentConfig
from ..core import LLMClient
from ..utils import strip_thinking_tags


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

        if display:
            print(f"\n{'='*70}")
            print(f"🤖 {self.agent_name}")
            print(f"{'='*70}")

        try:
            response = self.llm_client.chat(
                messages=self.messages,
                system_message=self.system_prompt,
                agent_name=self.agent_name  # Pass agent name for logging
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
