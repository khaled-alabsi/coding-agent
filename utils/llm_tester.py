"""Simple LLM tester for measuring context and response lengths."""
from openai import OpenAI
from typing import Dict, Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import AgentConfig


def test_llm_context(
    prompt: Optional[str] = None,
    max_tokens: Optional[int] = None,
    context_window: Optional[int] = None,
    model: Optional[str] = None,
    api_base: Optional[str] = None
) -> Dict:
    """
    Test LLM with a prompt and measure context/response lengths.

    Args:
        prompt: Test prompt to send (if None, uses a stress test prompt)
        max_tokens: Maximum tokens for response (if None, uses config default)
        context_window: Context window size (if None, uses config default)
        model: Model name (if None, uses config default)
        api_base: API base URL (if None, uses config default)

    Returns:
        Dictionary with results including token counts and truncation status
    """
    # Load config defaults
    config = AgentConfig(use_local_llm=True)

    # Use config values as defaults
    if max_tokens is None:
        max_tokens = config.max_tokens
    if context_window is None:
        context_window = config.context_window
    if model is None:
        model = config.local_model
    if api_base is None:
        api_base = config.local_api_base

    # Use stress test prompt if none provided
    if prompt is None:
        prompt = (
            "Create a complete React TypeScript TODO application with the following requirements:\n"
            "1. Full CRUD operations (Create, Read, Update, Delete)\n"
            "2. Local storage persistence\n"
            "3. Filter by status (All, Active, Completed)\n"
            "4. Dark mode toggle\n"
            "5. Responsive design with Tailwind CSS\n"
            "\n"
            "Provide ALL code files with COMPLETE implementations:\n"
            "- index.html\n"
            "- package.json\n"
            "- tsconfig.json\n"
            "- vite.config.ts\n"
            "- tailwind.config.js\n"
            "- src/main.tsx\n"
            "- src/App.tsx\n"
            "- src/components/TodoList.tsx\n"
            "- src/components/TodoItem.tsx\n"
            "- src/components/TodoForm.tsx\n"
            "- src/components/FilterButtons.tsx\n"
            "- src/components/ThemeToggle.tsx\n"
            "- src/hooks/useTodos.ts\n"
            "- src/hooks/useTheme.ts\n"
            "- src/types/index.ts\n"
            "- src/utils/storage.ts\n"
            "- src/styles/index.css\n"
            "\n"
            "Write EVERY file with FULL, COMPLETE code. Do not skip any implementation details."
        )

    # At this point prompt is guaranteed to be str
    assert prompt is not None

    client = OpenAI(api_key="lm-studio", base_url=api_base)

    print("=" * 80)
    print("LLM CONTEXT TEST")
    print("=" * 80)
    print(f"\n📝 Prompt: {prompt[:100]}...")
    print(f"🔧 Settings:")
    print(f"   Model: {model}")
    print(f"   Max Tokens: {max_tokens:,}")
    print(f"   Context Window: {context_window:,}")
    print(f"\n⏳ Sending request...")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )

        response_text = response.choices[0].message.content

        # Get actual token usage if available
        usage = response.usage if hasattr(response, 'usage') else None

        # Estimate tokens (rough approximation)
        prompt_chars = len(prompt)
        response_chars = len(response_text)
        estimated_prompt_tokens = prompt_chars // 4
        estimated_response_tokens = response_chars // 4

        print(f"\n✅ Response received!")
        print(f"\n📊 Results:")

        if usage:
            print(f"   Prompt Tokens (actual): {usage.prompt_tokens:,}")
            print(f"   Response Tokens (actual): {usage.completion_tokens:,}")
            print(f"   Total Tokens (actual): {usage.total_tokens:,}")
        else:
            print(f"   Prompt Tokens (estimated): {estimated_prompt_tokens:,}")
            print(f"   Response Tokens (estimated): {estimated_response_tokens:,}")
            print(f"   Total Tokens (estimated): {estimated_prompt_tokens + estimated_response_tokens:,}")

        print(f"\n📏 Character Counts:")
        print(f"   Prompt: {prompt_chars:,} chars")
        print(f"   Response: {response_chars:,} chars")

        # Check for truncation
        actual_response_tokens = usage.completion_tokens if usage else estimated_response_tokens
        if actual_response_tokens >= max_tokens * 0.95:
            print(f"\n⚠️  WARNING: Response appears TRUNCATED!")
            print(f"   Used {actual_response_tokens:,} / {max_tokens:,} tokens ({actual_response_tokens/max_tokens*100:.1f}%)")
            print(f"   💡 Recommended: Increase max_tokens to {actual_response_tokens + 1000:,}")
        else:
            print(f"\n✅ Response looks complete")
            print(f"   Used {actual_response_tokens:,} / {max_tokens:,} tokens ({actual_response_tokens/max_tokens*100:.1f}%)")

        # Show response preview
        print(f"\n📄 Response Preview (first 200 chars):")
        print(f"   {response_text[:200]}...")
        print(f"\n📄 Response End (last 200 chars):")
        print(f"   ...{response_text[-200:]}")

        print("=" * 80)

        return {
            'prompt_tokens': usage.prompt_tokens if usage else estimated_prompt_tokens,
            'response_tokens': usage.completion_tokens if usage else estimated_response_tokens,
            'total_tokens': usage.total_tokens if usage else (estimated_prompt_tokens + estimated_response_tokens),
            'response_text': response_text,
            'truncated': actual_response_tokens >= max_tokens * 0.95
        }

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("=" * 80)
        return {'error': str(e)}
