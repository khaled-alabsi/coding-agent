"""Tests for the conversation history compactor."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import pytest

from azure_agent.config import AgentConfig
from azure_agent.agents.base_agent import BaseAgent


class FakeLLMClient:
    """Simple LLM client stub for testing."""

    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_message: Optional[str] = None,
        agent_name: str = "unknown",
    ) -> str:
        self.calls.append(
            {
                "messages": messages,
                "system_message": system_message,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "agent_name": agent_name,
            }
        )
        if agent_name == "HistoryCompactor":
            return "• summarized conversation"
        return "assistant response"


class DummyAgent(BaseAgent):
    """Concrete agent for exercising base functionality."""

    @property
    def agent_name(self) -> str:
        return "Dummy"

    @property
    def system_prompt(self) -> str:
        return "You are a helpful assistant."


@pytest.fixture
def config() -> AgentConfig:
    return AgentConfig(
        use_local_llm=True,
        local_model="test-model",
        context_window=200,
        max_tokens=32,
    )


@pytest.fixture
def llm() -> FakeLLMClient:
    return FakeLLMClient()


@pytest.fixture
def agent(config: AgentConfig, llm: FakeLLMClient) -> DummyAgent:
    return DummyAgent(config, llm)


def _long_message(idx: int) -> str:
    return f"Turn {idx}: " + ("content " * 20)


def test_history_compaction_triggers_when_over_budget(agent: DummyAgent, llm: FakeLLMClient) -> None:
    """Ensure summaries are inserted once the token budget is exceeded."""
    # Small number of turns should not trigger compaction.
    agent.chat(_long_message(0), display=False)
    agent.chat(_long_message(1), display=False)
    assert not any(msg.get("name") == "history_compactor" for msg in agent.messages)

    # More turns push the history over the threshold.
    for idx in range(2, 8):
        agent.chat(_long_message(idx), display=False)

    summary_messages = [msg for msg in agent.messages if msg.get("name") == "history_compactor"]
    assert summary_messages, "Compaction should insert a summary message."
    assert summary_messages[0]["content"].startswith("Conversation summary")

    # The latest turn must remain untouched.
    assert agent.messages[-1]["role"] == "assistant"
    assert agent.messages[-1]["content"] == "assistant response"
    assert agent.messages[-2]["role"] == "user"
    assert "Turn 7" in agent.messages[-2]["content"]

    # History compactor should have called the LLM at least once.
    assert any(call["agent_name"] == "HistoryCompactor" for call in llm.calls)


def test_recent_turns_are_preserved(agent: DummyAgent) -> None:
    """The most recent turns should be kept verbatim after compaction."""
    for idx in range(10):
        agent.chat(_long_message(idx), display=False)

    non_summary = [msg for msg in agent.messages if msg.get("role") != "system"]
    assert non_summary[-1]["role"] == "assistant"
    assert non_summary[-1]["content"] == "assistant response"
    assert non_summary[-2]["role"] == "user"
    assert non_summary[-2]["content"].startswith("Turn 9")


def test_no_compaction_when_history_is_small(agent: DummyAgent, llm: FakeLLMClient) -> None:
    """If the history fits comfortably, no summary should be added."""
    agent.chat("Short exchange", display=False)
    agent.chat("Another", display=False)

    assert not any(msg.get("name") == "history_compactor" for msg in agent.messages)
    # The compactor should never have been invoked.
    assert not any(call["agent_name"] == "HistoryCompactor" for call in llm.calls)
