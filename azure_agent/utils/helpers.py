"""Helper utility functions."""
import re
from typing import List, Tuple, Dict, Any


def parse_code_blocks(text: str) -> List[Tuple[str, str]]:
    """
    Parse markdown code blocks from text.

    Args:
        text: Text containing code blocks

    Returns:
        List of (language, code) tuples
    """
    pattern = r'```(\w+)?\n(.+?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return [(lang or 'text', code.strip()) for lang, code in matches]


def format_message(role: str, content: str) -> Dict[str, str]:
    """
    Format a message for LLM API.

    Args:
        role: Message role (user, assistant, system)
        content: Message content

    Returns:
        Formatted message dict
    """
    return {"role": role, "content": content}


def truncate_content(content: str, max_length: int = 500) -> str:
    """
    Truncate content to max length with ellipsis.

    Args:
        content: Content to truncate
        max_length: Maximum length

    Returns:
        Truncated content
    """
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."


def strip_thinking_tags(text: str) -> str:
    """
    Remove thinking tags from LLM responses.

    Some reasoning models (like DeepSeek R1) include <think>...</think> tags
    containing their reasoning process. This function intelligently removes
    those tags while preserving the actual answer.

    Strategy:
    1. If there's content both inside and outside thinking tags, keep only outside content
    2. If ALL content is inside thinking tags, keep the content but remove the tags
    3. This handles both structured responses and cases where the model puts everything inside tags

    Args:
        text: Text potentially containing thinking tags

    Returns:
        Text with thinking tags handled appropriately
    """
    if not text:
        return text

    # Check if there are thinking tags at all
    has_think_tags = bool(re.search(r'<think>', text, re.IGNORECASE)) or \
                     bool(re.search(r'<thinking>', text, re.IGNORECASE))

    if not has_think_tags:
        return text  # No thinking tags, return as is

    # Try to extract content outside of thinking tags first
    temp = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    temp = re.sub(r'<thinking>.*?</thinking>', '', temp, flags=re.DOTALL | re.IGNORECASE)
    temp = re.sub(r'\n\n\n+', '\n\n', temp).strip()

    # If we have substantial content outside thinking tags, use that
    if len(temp) > 50:  # Arbitrary threshold - if there's meaningful content outside
        return temp

    # Otherwise, the entire response might be inside thinking tags
    # Extract the content FROM INSIDE the tags instead of removing it
    thinking_content = []

    # Extract content from <think> tags
    for match in re.finditer(r'<think>(.*?)</think>', text, flags=re.DOTALL | re.IGNORECASE):
        thinking_content.append(match.group(1).strip())

    # Extract content from <thinking> tags
    for match in re.finditer(r'<thinking>(.*?)</thinking>', text, flags=re.DOTALL | re.IGNORECASE):
        thinking_content.append(match.group(1).strip())

    # If we extracted content from thinking tags, use that
    if thinking_content:
        combined = '\n\n'.join(thinking_content)
        # Clean up extra whitespace
        combined = re.sub(r'\n\n\n+', '\n\n', combined).strip()
        if combined:
            return combined

    # Fallback: return original with just tags stripped
    cleaned = re.sub(r'</?think(?:ing)?>',  '', text, flags=re.IGNORECASE)
    cleaned = re.sub(r'\n\n\n+', '\n\n', cleaned).strip()

    # Final safety check - never return empty if we had input
    if not cleaned and text.strip():
        # If all else fails, return the original text
        # Better to have thinking tags than lose all content
        return text.strip()

    return cleaned


def extract_json(text: str) -> Dict[str, Any]:
    """
    Extract JSON from text that may contain markdown or other content.

    Args:
        text: Text potentially containing JSON

    Returns:
        Extracted JSON as dict, or empty dict if not found
    """
    import json

    # Try to find JSON in code blocks first
    json_pattern = r'```json\n(.+?)```'
    matches = re.findall(json_pattern, text, re.DOTALL)

    if matches:
        try:
            return json.loads(matches[0])
        except json.JSONDecodeError:
            pass

    # Try to parse the entire text as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON-like structures
    brace_pattern = r'\{.+\}'
    matches = re.findall(brace_pattern, text, re.DOTALL)

    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    return {}
