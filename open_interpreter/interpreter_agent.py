from interpreter import interpreter
from pathlib import Path
import json
import os
import signal
import time
import threading

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

# Global flag for timeout handling
timeout_occurred = False
auto_save_thread = None
stop_auto_save = False
watchdog_thread = None
stop_watchdog = False
last_activity_time = None
message_count = 0

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

def save_history_silent():
    """Save history without printing (for auto-save)."""
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(interpreter.messages, f, indent=2, ensure_ascii=False)
    except Exception as e:
        pass  # Silent fail for background saves

def auto_save_worker(interval=30):
    """Background worker to save history periodically."""
    global stop_auto_save
    while not stop_auto_save:
        time.sleep(interval)
        if not stop_auto_save:
            save_history_silent()

def start_auto_save(interval=30):
    """Start background auto-save thread."""
    global auto_save_thread, stop_auto_save
    stop_auto_save = False
    auto_save_thread = threading.Thread(target=auto_save_worker, args=(interval,), daemon=True)
    auto_save_thread.start()
    print(f"🔄 Auto-save enabled (every {interval} seconds)")

def stop_auto_save_thread():
    """Stop the auto-save thread."""
    global stop_auto_save
    stop_auto_save = True
    if auto_save_thread:
        auto_save_thread.join(timeout=2)

def update_activity():
    """Update the last activity timestamp."""
    global last_activity_time
    last_activity_time = time.time()

def watchdog_worker(inactivity_timeout):
    """
    Background worker to monitor for inactivity.
    Triggers if no activity detected for inactivity_timeout seconds.
    """
    global stop_watchdog, timeout_occurred, last_activity_time

    check_interval = min(5, inactivity_timeout / 4)  # Check frequently

    while not stop_watchdog:
        time.sleep(check_interval)

        if stop_watchdog:
            break

        if last_activity_time is not None:
            idle_time = time.time() - last_activity_time
            if idle_time > inactivity_timeout:
                timeout_occurred = True
                print(f"\n⏰ INACTIVITY TIMEOUT: No activity for {int(idle_time)} seconds. Saving and stopping...")
                save_history_silent()
                # Use a different exception or just set flag
                stop_watchdog = True
                break

def start_watchdog(inactivity_timeout):
    """Start background watchdog thread for inactivity monitoring."""
    global watchdog_thread, stop_watchdog, last_activity_time
    stop_watchdog = False
    last_activity_time = time.time()  # Initialize
    watchdog_thread = threading.Thread(target=watchdog_worker, args=(inactivity_timeout,), daemon=True)
    watchdog_thread.start()
    print(f"🐕 Watchdog enabled (inactivity timeout: {inactivity_timeout}s)")

def stop_watchdog_thread():
    """Stop the watchdog thread."""
    global stop_watchdog
    stop_watchdog = True
    if watchdog_thread:
        watchdog_thread.join(timeout=2)

def activity_monitor_wrapper(interval=2):
    """
    Monitor interpreter.messages for changes and update activity.
    This runs in the background and checks if new messages appear.
    """
    global message_count, stop_watchdog

    while not stop_watchdog:
        time.sleep(interval)
        current_count = len(interpreter.messages)
        if current_count != message_count:
            message_count = current_count
            update_activity()

def start_activity_monitor():
    """Start monitoring interpreter messages for activity."""
    global message_count
    message_count = len(interpreter.messages)
    monitor_thread = threading.Thread(target=activity_monitor_wrapper, daemon=True)
    monitor_thread.start()

def timeout_handler(signum, frame):
    """Handle timeout signal."""
    global timeout_occurred
    timeout_occurred = True
    print("\n⏰ TIMEOUT: Agent is taking too long. Saving progress and stopping...")
    save_history()
    raise TimeoutError("Agent execution timed out")

def run(continue_from_history=True, timeout_seconds=None, inactivity_timeout=None, auto_save_interval=30):
    """
    Run the coding agent.

    Args:
        continue_from_history: Whether to continue from saved history
        timeout_seconds: Maximum TOTAL execution time in seconds (None = no limit)
        inactivity_timeout: Maximum time with no activity in seconds (None = no inactivity check)
                           This resets whenever the agent produces output/messages
        auto_save_interval: How often to auto-save history in seconds (default: 30)
    """
    global timeout_occurred
    timeout_occurred = False

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

    # Start auto-save background thread
    start_auto_save(auto_save_interval)

    # Start inactivity watchdog if requested
    if inactivity_timeout:
        start_watchdog(inactivity_timeout)
        start_activity_monitor()

    # Use display=True for Jupyter to show real-time output
    print("=" * 70)
    print("STARTING AGENT - Watch the output below")
    if timeout_seconds:
        print(f"⏰ Total timeout: {timeout_seconds} seconds")
    if inactivity_timeout:
        print(f"🐕 Inactivity timeout: {inactivity_timeout} seconds (resets on activity)")
    print("=" * 70)

    try:
        # Set up total timeout if specified (Note: signal.alarm doesn't work on Windows or in threads)
        if timeout_seconds and hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)

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

        # Cancel total timeout if it was set
        if timeout_seconds and hasattr(signal, 'SIGALRM'):
            signal.alarm(0)

    except TimeoutError:
        print("\n⚠️  Agent timed out. History has been saved. You can continue later.")
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user. Saving history...")
        save_history()
        raise
    finally:
        # Stop all background threads
        stop_auto_save_thread()
        if inactivity_timeout:
            stop_watchdog_thread()

        # Always save history one final time, even if interrupted
        save_history()

    print("\n" + "=" * 70)
    if timeout_occurred:
        print("AGENT STOPPED (TIMEOUT)")
    else:
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

def force_save():
    """Manually trigger a save of the current conversation state."""
    if interpreter.messages:
        save_history()
        print("✅ Current conversation state saved!")
    else:
        print("ℹ️  No messages to save")

def continue_conversation(message, timeout_seconds=None, inactivity_timeout=None, auto_save_interval=30):
    """
    Continue the conversation with a custom message.

    Args:
        message: The message to send to the agent
        timeout_seconds: Maximum TOTAL execution time in seconds (None = no limit)
        inactivity_timeout: Maximum time with no activity in seconds (None = no inactivity check)
        auto_save_interval: How often to auto-save history in seconds (default: 30)
    """
    global timeout_occurred
    timeout_occurred = False

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

    # Start auto-save background thread
    start_auto_save(auto_save_interval)

    # Start inactivity watchdog if requested
    if inactivity_timeout:
        start_watchdog(inactivity_timeout)
        start_activity_monitor()

    # Continue with custom message
    print("=" * 70)
    print("CONTINUING CONVERSATION")
    if timeout_seconds:
        print(f"⏰ Total timeout: {timeout_seconds} seconds")
    if inactivity_timeout:
        print(f"🐕 Inactivity timeout: {inactivity_timeout} seconds (resets on activity)")
    print("=" * 70)

    try:
        # Set up total timeout if specified
        if timeout_seconds and hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)

        interpreter.chat(message, display=True)

        # Cancel total timeout if it was set
        if timeout_seconds and hasattr(signal, 'SIGALRM'):
            signal.alarm(0)

    except TimeoutError:
        print("\n⚠️  Agent timed out. History has been saved. You can continue later.")
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user. Saving history...")
        save_history()
        raise
    finally:
        # Stop all background threads
        stop_auto_save_thread()
        if inactivity_timeout:
            stop_watchdog_thread()

        # Always save history
        save_history()

    print("\n" + "=" * 70)
    if timeout_occurred:
        print("CONVERSATION STOPPED (TIMEOUT)")
    else:
        print("CONVERSATION SAVED")
    print("=" * 70)

if __name__ == "__main__":
    run()
