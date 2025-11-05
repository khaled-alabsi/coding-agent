from interpreter import interpreter
from pathlib import Path
import json
import os

project_dir = Path(__file__).parent
prompt_file = project_dir / "prompt.md"
history_file = project_dir / "agent_history.json"

prompt_text = prompt_file.read_text(encoding="utf-8")

system_instructions = """
You are an autonomous coding agent working only inside this project directory.

Goals:
- Read the provided project specification.
- Initialize the correct stack (e.g., Node+TypeScript).
- Create all described files/folders.
- Install dependencies and run tests where appropriate.
- Ask before any destructive action.
"""

def load_history():
    """Load previous conversation history if it exists."""
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                print(f"📚 Loaded {len(history)} previous messages from history")
                return history
        except Exception as e:
            print(f"⚠️  Could not load history: {e}")
            return []
    return []

def save_history():
    """Save the current conversation history to file."""
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(interpreter.messages, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(interpreter.messages)} messages to history")
    except Exception as e:
        print(f"⚠️  Could not save history: {e}")

def run(continue_from_history=True):
    # Configure interpreter for LM Studio
    interpreter.llm.api_base = "http://localhost:1234/v1"   # LM Studio default
    interpreter.llm.api_key = "lm-studio"                   # any non-empty string works
    interpreter.llm.model = "openai/qwen/qwen3-coder-30b"  # Prefix with openai/ for custom API base
    interpreter.llm.context_window = 7657                   # Set context window size
    interpreter.llm.max_tokens = 2000                       # Max tokens per response

    # Disable confirmation prompts - auto-run code without asking
    interpreter.auto_run = True

    # Enable verbose mode to see detailed logs of what's happening
    interpreter.verbose = True

    interpreter.system_message = system_instructions

    # Load previous conversation history if requested
    if continue_from_history:
        previous_messages = load_history()
        if previous_messages:
            interpreter.messages = previous_messages
            print("🔄 Continuing from previous session...")
        else:
            print("🆕 Starting fresh session...")
    else:
        # Clear history to start fresh
        interpreter.messages = []
        print("🆕 Starting fresh session (history ignored)...")

    # Use display=True for Jupyter to show real-time output
    print("=" * 70)
    print("STARTING AGENT - Watch the output below")
    print("=" * 70)

    try:
        # If continuing, ask the agent to continue, otherwise give full spec
        if continue_from_history and len(interpreter.messages) > 2:
            interpreter.chat(
                "Continue from where you left off. Review what you've done and complete any remaining tasks.",
                display=True
            )
        else:
            interpreter.chat(
                f"""
We are in the project directory: {project_dir}

Here is the project specification you must implement:

--- BEGIN SPEC (prompt.md) ---
{prompt_text}
--- END SPEC ---

Read the spec carefully, then:
1) Plan the tasks.
2) Implement the project step by step in this directory.
3) Show commands and file changes as you go.
""",
                display=True  # This enables the rich terminal interface in Jupyter
            )
    finally:
        # Always save history, even if interrupted
        save_history()

    print("\n" + "=" * 70)
    print("AGENT COMPLETED")
    print("=" * 70)

def clear_history():
    """Clear the conversation history."""
    if history_file.exists():
        history_file.unlink()
        print("🗑️  History cleared")
    else:
        print("ℹ️  No history to clear")

def view_history():
    """View the conversation history summary."""
    history = load_history()
    if not history:
        print("ℹ️  No history found")
        return

    print(f"\n📜 Conversation History ({len(history)} messages)")
    print("=" * 70)
    for i, msg in enumerate(history, 1):
        role = msg.get('role', 'unknown')
        msg_type = msg.get('type', 'message')
        content = msg.get('content', '')

        # Truncate long content
        preview = content[:100] + "..." if len(content) > 100 else content
        print(f"{i}. [{role}] ({msg_type}): {preview}")
    print("=" * 70)

def continue_conversation(message):
    """Continue the conversation with a custom message."""
    # Load history
    previous_messages = load_history()
    if previous_messages:
        interpreter.messages = previous_messages
        print(f"📚 Loaded {len(previous_messages)} previous messages")

    # Configure interpreter
    interpreter.llm.api_base = "http://localhost:1234/v1"
    interpreter.llm.api_key = "lm-studio"
    interpreter.llm.model = "openai/qwen/qwen3-coder-30b"
    interpreter.llm.context_window = 7657
    interpreter.llm.max_tokens = 2000
    interpreter.auto_run = True
    interpreter.verbose = True
    interpreter.system_message = system_instructions

    # Continue with custom message
    print("=" * 70)
    print("CONTINUING CONVERSATION")
    print("=" * 70)

    try:
        interpreter.chat(message, display=True)
    finally:
        save_history()

    print("\n" + "=" * 70)
    print("CONVERSATION SAVED")
    print("=" * 70)

if __name__ == "__main__":
    run()
