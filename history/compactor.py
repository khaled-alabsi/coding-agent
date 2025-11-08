"""Utilities for compacting long conversation histories."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional, Sequence

from config import AgentConfig
from core import LLMClient


@dataclass
class CompactionResult:
    """Represents the outcome of a history compaction attempt."""

    messages: List[Dict[str, str]]
    compacted: bool


class HistoryCompactor:
    """Summarizes older conversation turns to stay within the context window."""

    SUMMARY_PREFIX = "Conversation summary"
    SUMMARY_MESSAGE_NAME = "history_compactor"

    def __init__(
        self,
        config: AgentConfig,
        llm_client: LLMClient,
        *,
        trigger_ratio: float = 0.85,
        max_recent_messages: int = 6,
        min_recent_messages: int = 2,
        summary_chunk_size: int = 8,
        response_buffer_tokens: int = 1024,
        fallback_summary_chars: int = 500,
    ) -> None:
        self.config = config
        self.llm_client = llm_client
        self.trigger_ratio = trigger_ratio
        self.max_recent_messages = max_recent_messages
        self.min_recent_messages = min_recent_messages
        self.summary_chunk_size = max(1, summary_chunk_size)
        self.response_buffer_tokens = response_buffer_tokens
        self.fallback_summary_chars = fallback_summary_chars

    def compact(
        self,
        messages: Sequence[Dict[str, str]],
        *,
        system_prompt: Optional[str],
        context_window: int,
    ) -> CompactionResult:
        """Return a compacted version of ``messages`` if needed."""
        if not messages:
            return CompactionResult(list(messages), False)

        trigger_limit = self._trigger_limit(context_window)
        total_tokens = self._estimate_tokens(messages, system_prompt)
        if total_tokens <= trigger_limit:
            return CompactionResult(list(messages), False)

        # Remove any previous compactor summaries before re-summarizing.
        conversation_only = [
            msg
            for msg in messages
            if not self._is_compactor_summary(msg)
        ]

        if len(conversation_only) <= self.min_recent_messages:
            # Not enough messages to summarize meaningfully.
            return CompactionResult(list(messages), False)

        recent_to_keep = min(len(conversation_only), self.max_recent_messages)
        best_candidate: Optional[List[Dict[str, str]]] = None

        while recent_to_keep >= self.min_recent_messages:
            preserved_recent = list(conversation_only[-recent_to_keep:])
            to_summarize = conversation_only[:-recent_to_keep]
            if not to_summarize:
                break

            summary_sections = self._summarize_messages(to_summarize)
            summary_message = {
                "role": "system",
                "content": self._format_summary(summary_sections),
                "name": self.SUMMARY_MESSAGE_NAME,
            }

            candidate = [summary_message]
            candidate.extend(preserved_recent)
            best_candidate = candidate

            candidate_tokens = self._estimate_tokens(candidate, system_prompt)
            if candidate_tokens <= trigger_limit:
                return CompactionResult(candidate, True)

            # Try keeping fewer recent messages and summarize more aggressively.
            recent_to_keep -= 2

        if best_candidate is not None:
            return CompactionResult(best_candidate, True)

        # Fall back to original messages if nothing could be summarized.
        return CompactionResult(list(messages), False)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _trigger_limit(self, context_window: int) -> int:
        if context_window <= 0:
            return 0
        ratio_limit = max(1, int(context_window * self.trigger_ratio))
        buffer_limit = max(1, context_window - self.response_buffer_tokens)
        return max(1, min(ratio_limit, buffer_limit))

    def _estimate_tokens(
        self,
        messages: Sequence[Dict[str, str]],
        system_prompt: Optional[str],
    ) -> int:
        total = 0
        if system_prompt:
            total += self._estimate_text_tokens(system_prompt)
        for msg in messages:
            total += self._estimate_text_tokens(msg.get("content", ""))
        return total

    def _estimate_text_tokens(self, text: str) -> int:
        if not text:
            return 0
        # Approximate by assuming 4 characters per token with a small buffer.
        return max(1, int(len(text) / 4) + 1)

    def _is_compactor_summary(self, message: Dict[str, str]) -> bool:
        if message.get("role") != "system":
            return False
        if message.get("name") == self.SUMMARY_MESSAGE_NAME:
            return True
        content = message.get("content", "")
        return content.startswith(self.SUMMARY_PREFIX)

    def _summarize_messages(self, messages: Sequence[Dict[str, str]]) -> List[str]:
        summaries: List[str] = []
        for chunk in self._chunk(messages, self.summary_chunk_size):
            formatted = self._format_chunk(chunk)
            summary = self._call_summarizer(formatted)
            summaries.append(summary)
        return summaries

    def _chunk(
        self,
        messages: Sequence[Dict[str, str]],
        size: int,
    ) -> List[List[Dict[str, str]]]:
        chunk: List[Dict[str, str]] = []
        chunks: List[List[Dict[str, str]]] = []
        for msg in messages:
            chunk.append(msg)
            if len(chunk) >= size:
                chunks.append(chunk)
                chunk = []
        if chunk:
            chunks.append(chunk)
        return chunks

    def _format_chunk(self, chunk: Sequence[Dict[str, str]]) -> str:
        lines = []
        for message in chunk:
            role = message.get("role", "user").upper()
            content = message.get("content", "").strip()
            lines.append(f"{role}: {content}")
        return "\n\n".join(lines)

    def _call_summarizer(self, formatted_chunk: str) -> str:
        prompt = (
            "Summarize the following portion of a conversation into concise bullet points. "
            "Capture goals, constraints, decisions, and any outstanding tasks. "
            "Preserve critical instructions verbatim when necessary."
            "\n\nConversation:\n"
            f"{formatted_chunk}"
        )
        try:
            summary = self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                system_message=(
                    "You are a meticulous conversation summarizer."
                    " Keep the summary short, objective, and focused on actionable items."
                ),
                temperature=0.0,
                max_tokens=min(512, self.config.max_tokens),
                agent_name="HistoryCompactor",
            )
            return summary.strip()
        except Exception:
            # Fall back to deterministic truncation.
            truncated = formatted_chunk[: self.fallback_summary_chars].strip()
            return f"• {truncated}" if truncated else "• (no summary available)"

    def _format_summary(self, sections: Sequence[str]) -> str:
        if not sections:
            return f"{self.SUMMARY_PREFIX}: (no prior turns summarized)"
        if len(sections) == 1:
            return f"{self.SUMMARY_PREFIX}:\n{sections[0]}"
        lines = [f"{self.SUMMARY_PREFIX}:"]
        for idx, section in enumerate(sections, start=1):
            lines.append(f"Section {idx}:\n{section}")
        return "\n\n".join(lines)
