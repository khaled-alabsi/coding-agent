"""Utility functions for Azure Code Agent."""
from .helpers import parse_code_blocks, format_message, truncate_content, strip_thinking_tags
from .logger import AgentLogger
from .sound import (
    play_completion_sound,
    play_error_sound,
    play_warning_sound,
    play_truncation_sound,
    play_validation_failed_sound,
    play_fix_attempt_sound,
)
from .prompt_loader import load_prompt, reload_prompts, get_available_prompts
from .context_analyzer import ContextAnalyzer
from .history_compactor import HistoryCompactor

__all__ = [
    'parse_code_blocks',
    'format_message',
    'truncate_content',
    'strip_thinking_tags',
    'AgentLogger',
    'play_completion_sound',
    'play_error_sound',
    'play_warning_sound',
    'play_truncation_sound',
    'play_validation_failed_sound',
    'play_fix_attempt_sound',
    'load_prompt',
    'reload_prompts',
    'get_available_prompts',
    'ContextAnalyzer',
    'test_llm_context',
    'HistoryCompactor',
]

# Lazy wrapper to avoid importing heavy deps (e.g., OpenAI client) at module import
def test_llm_context(*args, **kwargs):
    from .llm_tester import test_llm_context as _test
    return _test(*args, **kwargs)
