"""
Azure Code Agent - Multi-Agent Coding System

A sophisticated multi-agent system for automated software development.

Agents:
- Prompt Enhancer: Improves user prompts for clarity
- Planner: Creates detailed execution plans
- Plan Enhancer: Validates and improves plans
- Coder: Implements the code
- Result Validator: Validates output and triggers fixes
"""

from pathlib import Path
from typing import Optional
from .config import AgentConfig
from .core import AgentOrchestrator


def run(
    prompt: Optional[str] = None,
    prompt_file: Optional[str] = None,
    output_dir: Optional[str] = None,
    # LLM Configuration
    use_local_llm: bool = True,
    local_model: str = "deepseek/deepseek-r1-0528-qwen3-8b",
    local_api_base: str = "http://localhost:1234/v1",
    # Azure OpenAI (if not using local)
    azure_api_key: Optional[str] = None,
    azure_endpoint: Optional[str] = None,
    azure_deployment: Optional[str] = None,
    # Workflow options
    skip_prompt_enhancement: bool = False,
    skip_plan_enhancement: bool = False,
    max_fix_iterations: int = 3,
    # Generation parameters
    temperature: float = 0.7,
    max_tokens: int = 2000,
    context_window: int = 8000
) -> dict:
    """
    Run the multi-agent coding workflow.

    Args:
        prompt: User prompt (either this or prompt_file required)
        prompt_file: Path to file containing prompt
        output_dir: Output directory for generated code (default: ./output)

        LLM Configuration:
            use_local_llm: Use local LLM (LM Studio) instead of Azure OpenAI
            local_model: Local model name
            local_api_base: Local LLM API base URL

        Azure OpenAI (if not using local LLM):
            azure_api_key: Azure OpenAI API key
            azure_endpoint: Azure endpoint URL
            azure_deployment: Azure deployment name

        Workflow Options:
            skip_prompt_enhancement: Skip prompt enhancement phase
            skip_plan_enhancement: Skip plan enhancement phase
            max_fix_iterations: Maximum number of fix iterations (default: 3)

        Generation Parameters:
            temperature: Temperature for generation (default: 0.7)
            max_tokens: Max tokens per response (default: 2000)
            context_window: Context window size (default: 8000)

    Returns:
        Dict with workflow results

    Examples:
        # Basic usage with local LLM
        >>> run(prompt="Create a todo app", use_local_llm=True)

        # Use prompt from file
        >>> run(prompt_file="prompt.md", use_local_llm=True)

        # Custom output directory
        >>> run(prompt="Create a blog", output_dir="./my-blog", use_local_llm=True)

        # With Azure OpenAI
        >>> run(
        ...     prompt="Create an API",
        ...     use_local_llm=False,
        ...     azure_api_key="...",
        ...     azure_endpoint="...",
        ...     azure_deployment="gpt-4"
        ... )
    """
    # Create config
    config = AgentConfig(
        use_local_llm=use_local_llm,
        local_model=local_model,
        local_api_base=local_api_base,
        azure_api_key=azure_api_key,
        azure_endpoint=azure_endpoint,
        azure_deployment=azure_deployment,
        temperature=temperature,
        max_tokens=max_tokens,
        context_window=context_window,
        max_retry_attempts=max_fix_iterations
    )

    # Set custom output directory if provided
    if output_dir:
        config.output_dir = Path(output_dir).resolve()

    # Load prompt
    if prompt_file:
        prompt = Path(prompt_file).read_text(encoding="utf-8")
    elif not prompt:
        # Try to load from default prompt.md
        default_prompt_file = config.project_dir / "prompt.md"
        if default_prompt_file.exists():
            prompt = default_prompt_file.read_text(encoding="utf-8")
        else:
            raise ValueError("Either 'prompt' or 'prompt_file' must be provided")

    # Create orchestrator
    orchestrator = AgentOrchestrator(config)

    # Execute workflow
    try:
        results = orchestrator.execute_workflow(
            user_prompt=prompt,
            output_directory=config.output_dir if output_dir else None,
            skip_prompt_enhancement=skip_prompt_enhancement,
            skip_plan_enhancement=skip_plan_enhancement,
            max_fix_iterations=max_fix_iterations
        )
        return results
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        raise
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


def run_interactive():
    """Run in interactive mode with prompt from user input."""
    print("=" * 70)
    print("Azure Code Agent - Interactive Mode")
    print("=" * 70)
    print("\nEnter your project description (or 'quit' to exit):")
    print("(Press Enter twice to submit)\n")

    lines = []
    while True:
        line = input()
        if line.lower() == 'quit':
            return
        if line == '' and lines:
            break
        lines.append(line)

    prompt = '\n'.join(lines)

    if not prompt.strip():
        print("❌ No prompt provided")
        return

    # Run with default settings
    run(prompt=prompt, use_local_llm=True)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Run with prompt from command line argument
        prompt = sys.argv[1]
        run(prompt=prompt, use_local_llm=True)
    else:
        # Try to run with prompt.md
        try:
            run(use_local_llm=True)
        except ValueError:
            # No prompt.md found, run interactive mode
            run_interactive()
