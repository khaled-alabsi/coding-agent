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
