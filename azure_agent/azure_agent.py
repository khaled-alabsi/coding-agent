from openai import OpenAI, AzureOpenAI
from pathlib import Path
import json
import os
import subprocess
import time
import threading
import re
from typing import List, Dict, Any, Optional

project_dir = Path(__file__).parent
prompt_file = project_dir / "prompt.md"
history_file = project_dir / "agent_history.json"

prompt_text = prompt_file.read_text(encoding="utf-8") if prompt_file.exists() else ""

system_instructions = """
You are an autonomous coding agent working only inside this project directory.

Goals:
- Read the provided project specification.
- Initialize the correct stack (e.g., Node+TypeScript, Python, etc.).
- Create ALL files needed for a COMPLETE, RUNNABLE project.
- Install dependencies and run tests where appropriate.
- Ask before any destructive action.

CRITICAL - Create COMPLETE Projects:
When creating a project, you MUST include ALL necessary files to make it immediately runnable:

For Web Projects (React/Vue/Angular):
  ✅ MUST CREATE: package.json with all dependencies and scripts
  ✅ MUST CREATE: Build tool config (vite.config.ts, webpack.config.js, etc.)
  ✅ MUST CREATE: TypeScript config (tsconfig.json, tsconfig.node.json)
  ✅ MUST CREATE: All source files (components, styles, etc.)
  ✅ MUST CREATE: CSS/SCSS files with ACTUAL STYLING (NOT EMPTY!)
  ✅ MUST CREATE: index.html or entry point
  ✅ MUST CREATE: README.md with clear "How to Run" instructions
  ✅ Include "npm install" and "npm run dev" commands in README

  🔴 CRITICAL - File Consistency:
  - If you create src/styles/main.css, then import './styles/main.css'
  - If you create src/index.css, then import './index.css'
  - NEVER import files that don't exist or have different names!
  - CSS files MUST contain actual styles (colors, layouts, etc.), not be empty
  - Verify ALL import statements match the actual files you created

For Python Projects:
  ✅ MUST CREATE: requirements.txt or pyproject.toml
  ✅ MUST CREATE: setup.py or setup.cfg if needed
  ✅ MUST CREATE: All Python modules and packages
  ✅ MUST CREATE: README.md with installation and run instructions
  ✅ MUST CREATE: .env.example if using environment variables
  ✅ Include "pip install -r requirements.txt" command in README

For Node/Express Projects:
  ✅ MUST CREATE: package.json with dependencies
  ✅ MUST CREATE: Server entry point (server.js, index.js)
  ✅ MUST CREATE: All route files and middleware
  ✅ MUST CREATE: README.md with setup instructions

General Requirements:
  ✅ README MUST include: installation steps, how to run, how to test
  ✅ Create .gitignore file
  ✅ Organize files in proper directory structure
  ✅ Make project immediately runnable after "npm install" or "pip install"

ALWAYS create a complete, production-ready project structure, not just source files.

You can execute shell commands and write/read files. When you need to execute code or commands:
1. Provide the command or code in your response
2. I will execute it and return the results
3. Continue based on those results

Format your responses to include actions using these markers:
- BASH: <command> - for shell commands
- WRITE_FILE: <filepath> - followed by the file content
- READ_FILE: <filepath> - to read a file
- COMPLETE - when you've finished all tasks

Example workflow for React project:
1. Create package.json with all deps (react, react-dom, vite, typescript, etc.)
2. Create vite.config.ts and tsconfig.json files
3. Create src/styles/main.css with FULL STYLING (colors, layouts, responsive design)
4. Create src/components/ with all React components
5. Create src/App.tsx that imports components
6. Create src/main.tsx that imports App AND './styles/main.css' (matching the file name!)
7. Create index.html in src/ folder
8. Create README.md with "npm install && npm run dev" instructions
9. Create .gitignore
10. VERIFY all imports match actual files before signaling COMPLETE
11. Signal COMPLETE

VERIFICATION CHECKLIST (before COMPLETE):
- [ ] All imports reference files that actually exist
- [ ] CSS files contain actual styling code (not empty)
- [ ] package.json has all required dependencies
- [ ] Build configs are complete and valid
- [ ] README has clear installation and run instructions

If ANY file is missing or ANY import is broken, FIX IT before signaling COMPLETE!

CSS FILE REQUIREMENTS - NEVER CREATE EMPTY CSS FILES!
A proper CSS file for a React project must include at minimum:
```css
/* Reset */
* { margin: 0; padding: 0; box-sizing: border-box; }

/* Variables */
:root {
  --primary-color: #3b82f6;
  --text-dark: #1f2937;
  /* ... more variables */
}

/* Base styles */
body { font-family: sans-serif; color: var(--text-dark); }

/* Component styles */
.header { /* styles */ }
.hero { /* styles */ }
/* ... all sections */

/* Responsive */
@media (max-width: 768px) { /* mobile styles */ }
```

This is the MINIMUM. Include full styling for header, sections, buttons, forms, footer, etc.
NEVER write an empty CSS file or a file with just comments!
"""

# Global flags for timeout handling
timeout_occurred = False
auto_save_thread = None
stop_auto_save = False
watchdog_thread = None
stop_watchdog = False
last_activity_time = None
message_count = 0

class AzureCodeAgent:
    """LLM-based coding agent with code execution capabilities. Supports both Azure OpenAI and local LLM (LM Studio)."""

    def __init__(
        self,
        use_local_llm: bool = False,
        # Azure OpenAI parameters
        api_key: Optional[str] = None,
        api_version: str = "2024-02-15-preview",
        azure_endpoint: Optional[str] = None,
        deployment_name: Optional[str] = None,
        # Local LLM parameters
        local_api_base: Optional[str] = None,
        local_model: Optional[str] = None,
        context_window: int = 8000,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ):
        """
        Initialize the Code Agent.

        Args:
            use_local_llm: If True, use local LLM (LM Studio). If False, use Azure OpenAI.

            Azure OpenAI parameters:
                api_key: Azure OpenAI API key (or set AZURE_OPENAI_API_KEY env var)
                api_version: Azure OpenAI API version
                azure_endpoint: Azure endpoint URL (or set AZURE_OPENAI_ENDPOINT env var)
                deployment_name: Name of your deployment (or set AZURE_OPENAI_DEPLOYMENT env var)

            Local LLM parameters:
                local_api_base: Local LLM API base URL (or set LOCAL_LLM_API_BASE env var, default: http://localhost:1234/v1)
                local_model: Local model name (or set LOCAL_LLM_MODEL env var)
                context_window: Context window size for local LLM
                max_tokens: Max tokens per response
                temperature: Temperature for generation
        """
        self.use_local_llm = use_local_llm
        self.context_window = context_window
        self.max_tokens = max_tokens
        self.temperature = temperature

        if use_local_llm:
            # Configure for local LLM (LM Studio)
            self.local_api_base = local_api_base or os.getenv("LOCAL_LLM_API_BASE", "http://localhost:1234/v1")
            self.model_name = local_model or os.getenv("LOCAL_LLM_MODEL", "local-model")

            print(f"🏠 Using Local LLM")
            print(f"   API Base: {self.local_api_base}")
            print(f"   Model: {self.model_name}")

            self.client = OpenAI(
                api_key="lm-studio",  # LM Studio accepts any non-empty string
                base_url=self.local_api_base
            )

            self.deployment_name = self.model_name

        else:
            # Configure for Azure OpenAI
            self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
            self.azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
            self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT")

            if not all([self.api_key, self.azure_endpoint, self.deployment_name]):
                raise ValueError(
                    "Missing Azure OpenAI configuration. Provide via parameters or environment variables:\n"
                    "- AZURE_OPENAI_API_KEY\n"
                    "- AZURE_OPENAI_ENDPOINT\n"
                    "- AZURE_OPENAI_DEPLOYMENT\n"
                    "\nOr set use_local_llm=True to use local LLM Studio"
                )

            print(f"☁️  Using Azure OpenAI")
            print(f"   Endpoint: {self.azure_endpoint}")
            print(f"   Deployment: {self.deployment_name}")

            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=api_version,
                azure_endpoint=self.azure_endpoint
            )

            self.model_name = self.deployment_name

        self.messages: List[Dict[str, Any]] = []
        self.system_message = system_instructions
        self.max_iterations = 50
        self.working_directory = project_dir

    def execute_bash_command(self, command: str) -> Dict[str, Any]:
        """Execute a bash command and return the result."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.working_directory
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": "Command timed out after 300 seconds",
                "returncode": -1,
                "success": False
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "success": False
            }

    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """Write content to a file."""
        try:
            file_path = Path(filepath)
            if not file_path.is_absolute():
                file_path = self.working_directory / file_path

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")

            return {
                "success": True,
                "message": f"Successfully wrote to {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error writing file: {str(e)}"
            }

    def read_file(self, filepath: str) -> Dict[str, Any]:
        """Read content from a file."""
        try:
            file_path = Path(filepath)
            if not file_path.is_absolute():
                file_path = self.working_directory / file_path

            if not file_path.exists():
                return {
                    "success": False,
                    "content": "",
                    "message": f"File not found: {file_path}"
                }

            content = file_path.read_text(encoding="utf-8")
            return {
                "success": True,
                "content": content,
                "message": f"Successfully read {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "content": "",
                "message": f"Error reading file: {str(e)}"
            }

    def parse_and_execute_actions(self, response: str) -> List[Dict[str, Any]]:
        """Parse the agent's response and execute any requested actions."""
        results = []

        # Parse BASH commands
        bash_pattern = r'BASH:\s*(.+?)(?=\n(?:BASH:|WRITE_FILE:|READ_FILE:|COMPLETE|$))'
        bash_commands = re.findall(bash_pattern, response, re.DOTALL)

        for command in bash_commands:
            command = command.strip()
            print(f"\n🔧 Executing: {command}")
            result = self.execute_bash_command(command)
            results.append({
                "type": "bash",
                "command": command,
                "result": result
            })
            if result["stdout"]:
                print(f"📤 Output: {result['stdout']}")
            if result["stderr"]:
                print(f"⚠️  Error: {result['stderr']}")

        # Parse WRITE_FILE commands
        write_pattern = r'WRITE_FILE:\s*(.+?)\n```(?:\w+)?\n(.+?)```'
        write_commands = re.findall(write_pattern, response, re.DOTALL)

        for filepath, content in write_commands:
            filepath = filepath.strip()
            content = content.strip()
            print(f"\n📝 Writing file: {filepath}")
            result = self.write_file(filepath, content)
            results.append({
                "type": "write_file",
                "filepath": filepath,
                "result": result
            })
            print(f"✅ {result['message']}")

        # Parse READ_FILE commands
        read_pattern = r'READ_FILE:\s*(.+?)(?=\n|$)'
        read_commands = re.findall(read_pattern, response)

        for filepath in read_commands:
            filepath = filepath.strip()
            print(f"\n📖 Reading file: {filepath}")
            result = self.read_file(filepath)
            results.append({
                "type": "read_file",
                "filepath": filepath,
                "result": result
            })
            if result["success"]:
                print(f"✅ {result['message']}")
                print(f"Content preview: {result['content'][:200]}...")
            else:
                print(f"❌ {result['message']}")

        return results

    def chat(self, user_message: str, display: bool = True) -> str:
        """
        Send a message to the agent and get a response with action execution.

        Args:
            user_message: The message to send
            display: Whether to display the conversation in real-time

        Returns:
            The agent's final response
        """
        self.messages.append({
            "role": "user",
            "content": user_message
        })

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1

            # Prepare messages for API call
            api_messages = [{"role": "system", "content": self.system_message}] + self.messages

            # Call Azure OpenAI
            if display:
                print(f"\n{'='*70}")
                print(f"Iteration {iteration}/{self.max_iterations}")
                print(f"{'='*70}")

            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=api_messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )

                assistant_message = response.choices[0].message.content

                self.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })

                if display:
                    print(f"\n🤖 Agent Response:")
                    print(assistant_message)

                # Check if agent is done
                if "COMPLETE" in assistant_message:
                    if display:
                        print(f"\n✅ Agent completed the task!")
                    return assistant_message

                # Execute any actions in the response
                action_results = self.parse_and_execute_actions(assistant_message)

                # If there were actions, send results back to agent
                if action_results:
                    results_message = "Execution Results:\n\n"
                    for action in action_results:
                        if action["type"] == "bash":
                            results_message += f"Command: {action['command']}\n"
                            results_message += f"Output: {action['result']['stdout']}\n"
                            if action['result']['stderr']:
                                results_message += f"Error: {action['result']['stderr']}\n"
                            results_message += f"Success: {action['result']['success']}\n\n"
                        elif action["type"] == "write_file":
                            results_message += f"Write File: {action['filepath']}\n"
                            results_message += f"Result: {action['result']['message']}\n\n"
                        elif action["type"] == "read_file":
                            results_message += f"Read File: {action['filepath']}\n"
                            if action['result']['success']:
                                results_message += f"Content:\n{action['result']['content']}\n\n"
                            else:
                                results_message += f"Error: {action['result']['message']}\n\n"

                    self.messages.append({
                        "role": "user",
                        "content": results_message
                    })
                else:
                    # No actions found, agent might be waiting for confirmation
                    # or just providing information
                    break

            except Exception as e:
                error_msg = f"Error calling Azure OpenAI: {str(e)}"
                print(f"\n❌ {error_msg}")
                self.messages.append({
                    "role": "system",
                    "content": error_msg
                })
                break

        if iteration >= self.max_iterations:
            print(f"\n⚠️  Reached maximum iterations ({self.max_iterations})")

        return self.messages[-1]["content"] if self.messages else ""

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

def save_history(agent: AzureCodeAgent):
    """Save the current conversation history to file."""
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(agent.messages, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(agent.messages)} messages to history")
    except Exception as e:
        print(f"⚠️  Could not save history: {e}")

def save_history_silent(agent: AzureCodeAgent):
    """Save history without printing (for auto-save)."""
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(agent.messages, f, indent=2, ensure_ascii=False)
    except Exception as e:
        pass  # Silent fail for background saves

def auto_save_worker(agent: AzureCodeAgent, interval=30):
    """Background worker to save history periodically."""
    global stop_auto_save
    while not stop_auto_save:
        time.sleep(interval)
        if not stop_auto_save:
            save_history_silent(agent)

def start_auto_save(agent: AzureCodeAgent, interval=30):
    """Start background auto-save thread."""
    global auto_save_thread, stop_auto_save
    stop_auto_save = False
    auto_save_thread = threading.Thread(
        target=auto_save_worker,
        args=(agent, interval),
        daemon=True
    )
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

def watchdog_worker(agent: AzureCodeAgent, inactivity_timeout):
    """Background worker to monitor for inactivity."""
    global stop_watchdog, timeout_occurred, last_activity_time

    check_interval = min(5, inactivity_timeout / 4)

    while not stop_watchdog:
        time.sleep(check_interval)

        if stop_watchdog:
            break

        if last_activity_time is not None:
            idle_time = time.time() - last_activity_time
            if idle_time > inactivity_timeout:
                timeout_occurred = True
                print(f"\n⏰ INACTIVITY TIMEOUT: No activity for {int(idle_time)} seconds. Saving and stopping...")
                save_history_silent(agent)
                stop_watchdog = True
                break

def start_watchdog(agent: AzureCodeAgent, inactivity_timeout):
    """Start background watchdog thread for inactivity monitoring."""
    global watchdog_thread, stop_watchdog, last_activity_time
    stop_watchdog = False
    last_activity_time = time.time()
    watchdog_thread = threading.Thread(
        target=watchdog_worker,
        args=(agent, inactivity_timeout),
        daemon=True
    )
    watchdog_thread.start()
    print(f"🐕 Watchdog enabled (inactivity timeout: {inactivity_timeout}s)")

def stop_watchdog_thread():
    """Stop the watchdog thread."""
    global stop_watchdog
    stop_watchdog = True
    if watchdog_thread:
        watchdog_thread.join(timeout=2)

def activity_monitor_wrapper(agent: AzureCodeAgent, interval=2):
    """Monitor agent messages for changes and update activity."""
    global message_count, stop_watchdog

    while not stop_watchdog:
        time.sleep(interval)
        current_count = len(agent.messages)
        if current_count != message_count:
            message_count = current_count
            update_activity()

def start_activity_monitor(agent: AzureCodeAgent):
    """Start monitoring agent messages for activity."""
    global message_count
    message_count = len(agent.messages)
    monitor_thread = threading.Thread(
        target=activity_monitor_wrapper,
        args=(agent,),
        daemon=True
    )
    monitor_thread.start()

def run(
    continue_from_history=True,
    inactivity_timeout=None,
    auto_save_interval=30,
    # LLM mode selection
    use_local_llm=False,
    # Azure OpenAI parameters
    api_key=None,
    azure_endpoint=None,
    deployment_name=None,
    # Local LLM parameters
    local_api_base=None,
    local_model=None,
    context_window=8000,
    max_tokens=2000,
    temperature=0.7
):
    """
    Run the coding agent.

    Args:
        continue_from_history: Whether to continue from saved history
        inactivity_timeout: Maximum time with no activity in seconds (None = no inactivity check)
        auto_save_interval: How often to auto-save history in seconds (default: 30)

        LLM mode:
            use_local_llm: If True, use local LLM (LM Studio). If False, use Azure OpenAI.

        Azure OpenAI parameters:
            api_key: Azure OpenAI API key (optional, can use env var)
            azure_endpoint: Azure endpoint URL (optional, can use env var)
            deployment_name: Azure deployment name (optional, can use env var)

        Local LLM parameters:
            local_api_base: Local LLM API base URL (default: http://localhost:1234/v1)
            local_model: Local model name (e.g., deepseek/deepseek-r1-0528-qwen3-8b)
            context_window: Context window size for local LLM
            max_tokens: Max tokens per response
            temperature: Temperature for generation
    """
    global timeout_occurred
    timeout_occurred = False

    # Create agent
    agent = AzureCodeAgent(
        use_local_llm=use_local_llm,
        api_key=api_key,
        azure_endpoint=azure_endpoint,
        deployment_name=deployment_name,
        local_api_base=local_api_base,
        local_model=local_model,
        context_window=context_window,
        max_tokens=max_tokens,
        temperature=temperature
    )

    # Load previous conversation history if requested
    if continue_from_history:
        previous_messages = load_history()
        if previous_messages:
            agent.messages = previous_messages
            print("🔄 Continuing from previous session...")
        else:
            print("🆕 Starting fresh session...")
    else:
        print("🆕 Starting fresh session (history ignored)...")

    # Start auto-save background thread
    start_auto_save(agent, auto_save_interval)

    # Start inactivity watchdog if requested
    if inactivity_timeout:
        start_watchdog(agent, inactivity_timeout)
        start_activity_monitor(agent)

    print("=" * 70)
    print("STARTING AZURE AGENT - Watch the output below")
    if inactivity_timeout:
        print(f"🐕 Inactivity timeout: {inactivity_timeout} seconds (resets on activity)")
    print("=" * 70)

    try:
        # If continuing, ask the agent to continue, otherwise give full spec
        if continue_from_history and len(agent.messages) > 2:
            agent.chat(
                "Continue from where you left off. Review what you've done and complete any remaining tasks.",
                display=True
            )
        else:
            agent.chat(
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
                display=True
            )

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user. Saving history...")
        save_history(agent)
        raise
    finally:
        # Stop all background threads
        stop_auto_save_thread()
        if inactivity_timeout:
            stop_watchdog_thread()

        # Always save history one final time
        save_history(agent)

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
        content = msg.get('content', '')

        # Truncate long content
        preview = content[:100] + "..." if len(content) > 100 else content
        print(f"{i}. [{role}]: {preview}")
    print("=" * 70)

def force_save(agent: AzureCodeAgent):
    """Manually trigger a save of the current conversation state."""
    if agent.messages:
        save_history(agent)
        print("✅ Current conversation state saved!")
    else:
        print("ℹ️  No messages to save")

if __name__ == "__main__":
    run()
