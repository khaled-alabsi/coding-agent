"""Prompt loader utility for loading agent prompts from files."""
from pathlib import Path
from typing import Dict

# Cache for loaded prompts
_prompt_cache: Dict[str, str] = {}


def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt from the prompts directory.

    Args:
        prompt_name: Name of the prompt file (without .md extension)

    Returns:
        Prompt content as string

    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    # Check cache first
    if prompt_name in _prompt_cache:
        return _prompt_cache[prompt_name]

    # Build path to prompt file
    prompts_dir = Path(__file__).parent.parent / "prompts"
    prompt_file = prompts_dir / f"{prompt_name}.md"

    if not prompt_file.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_file}\n"
            f"Available prompts in {prompts_dir}: "
            f"{', '.join([f.stem for f in prompts_dir.glob('*.md')])}"
        )

    # Load and cache the prompt
    content = prompt_file.read_text(encoding='utf-8')
    _prompt_cache[prompt_name] = content

    return content


def reload_prompts():
    """Clear the prompt cache to force reload from files."""
    _prompt_cache.clear()


def get_available_prompts() -> list:
    """
    Get list of available prompt files.

    Returns:
        List of prompt names (without .md extension)
    """
    prompts_dir = Path(__file__).parent.parent / "prompts"
    if not prompts_dir.exists():
        return []

    return [f.stem for f in prompts_dir.glob('*.md')]
