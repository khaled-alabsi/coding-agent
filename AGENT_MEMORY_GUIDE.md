# Agent Memory & Persistence Guide

This guide explains how to use the agent's memory system to continue work from where it stopped.

## How It Works

The agent saves its entire conversation history to `agent_history.json` after each session. This includes:
- All user messages
- All agent responses
- All code executions and their outputs
- All decisions and reasoning

When you restart the agent, it can load this history and continue from where it left off.

## Usage Examples

### 1. Continue from Last Session (Default)

```python
from cli_test import run

# This will automatically load previous history and continue
run()
```

Or if the agent finished but you want to add more:
```python
# The agent will say: "Continue from where you left off..."
run(continue_from_history=True)
```

### 2. Start Fresh (Ignore History)

```python
from cli_test import run

# Start a completely new session, ignoring previous history
run(continue_from_history=False)
```

### 3. Continue with Custom Instructions

```python
from cli_test import continue_conversation

# Continue with specific instructions
continue_conversation("Add unit tests for the authentication module")

# Or ask for changes
continue_conversation("Refactor the code to use async/await")

# Or fix issues
continue_conversation("The server is not starting. Please debug and fix the issue.")
```

### 4. View Conversation History

```python
from cli_test import view_history

# View a summary of all previous messages
view_history()
```

Output example:
```
📜 Conversation History (45 messages)
======================================================================
1. [user] (message): We are in the project directory: /Users/...
2. [assistant] (message): I'll help you implement this project. Let me start by...
3. [assistant] (code): mkdir src
4. [assistant] (console): Directory created successfully
...
```

### 5. Clear History

```python
from cli_test import clear_history

# Delete all conversation history and start fresh next time
clear_history()
```

## Complete Workflow Example

### Session 1: Start Project
```python
import importlib
import cli_test
importlib.reload(cli_test)
from cli_test import run

# First run - starts project
run()
# Agent creates files, installs dependencies, etc.
# Session is automatically saved
```

### Session 2: Continue After Interruption
```python
import importlib
import cli_test
importlib.reload(cli_test)
from cli_test import run

# Continue from where we left off
run()
# Agent: "📚 Loaded 45 previous messages from history"
# Agent: "🔄 Continuing from previous session..."
# Agent reviews what it did and continues
```

### Session 3: Add More Features
```python
import importlib
import cli_test
importlib.reload(cli_test)
from cli_test import continue_conversation

# Add specific new requirements
continue_conversation("""
Add the following features:
1. User authentication with JWT
2. Password hashing with bcrypt
3. Rate limiting middleware
""")
```

### Session 4: Check What Was Done
```python
import importlib
import cli_test
importlib.reload(cli_test)
from cli_test import view_history

# Review all the work
view_history()
```

### Session 5: Start New Project
```python
import importlib
import cli_test
importlib.reload(cli_test)
from cli_test import clear_history, run

# Clear old project history
clear_history()

# Start fresh with new spec (update prompt.md first)
run(continue_from_history=False)
```

## How the Agent Remembers Context

When continuing from history, the agent has access to:

1. **Previous Tasks**: What it was asked to do
2. **Completed Work**: Files created, commands run, tests executed
3. **Current State**: What's done and what's pending
4. **Errors/Issues**: Any problems encountered
5. **Decisions Made**: Architecture choices, library selections, etc.

The agent will:
- Review the conversation history
- Assess the current state of the project
- Identify what's complete and what's pending
- Continue from where it stopped

## File Location

The conversation history is saved in:
```
/Users/Khaled.Alabsi/projects/test-cli-agents/agent_history.json
```

This is a JSON file containing all messages. You can:
- View it manually to see what the agent did
- Back it up to save important sessions
- Share it to reproduce agent behavior
- Delete it to start fresh

## Tips & Best Practices

### 1. Regular Sessions
Break work into sessions:
```python
# Session 1: Setup
run()

# Session 2: Core features
continue_conversation("Implement core features")

# Session 3: Testing
continue_conversation("Add comprehensive tests")

# Session 4: Documentation
continue_conversation("Add API documentation")
```

### 2. Recovery from Errors
If the agent gets stuck or makes mistakes:
```python
continue_conversation("""
The previous approach didn't work. Let's try a different solution:
1. Revert the last changes
2. Use library X instead of Y
3. Follow this pattern: [describe pattern]
""")
```

### 3. Context Window Management
The agent has a context window of 7657 tokens. If history gets too long:

```python
# Option 1: Start fresh with summary
clear_history()
run(continue_from_history=False)

# Option 2: Provide a summary
continue_conversation("""
Summary of work so far:
- Created Express API with TypeScript
- Implemented CRUD for todos
- Added tests with Jest

Next task: Add user authentication
""")
```

### 4. Backup Important Sessions
```bash
# Backup before major changes
cp agent_history.json agent_history_backup.json

# Restore if needed
cp agent_history_backup.json agent_history.json
```

## Advanced: Multiple Projects

For managing multiple projects:

```python
# Project 1
project_dir = Path("/path/to/project1")
history_file = project_dir / "agent_history.json"

# Project 2
project_dir = Path("/path/to/project2")
history_file = project_dir / "agent_history.json"
```

Each project gets its own history file.

## Troubleshooting

### History not loading?
```python
from cli_test import load_history
messages = load_history()
print(f"Loaded {len(messages)} messages")
```

### Want to edit history manually?
Open `agent_history.json` in a text editor. It's a JSON array of message objects:
```json
[
  {
    "role": "user",
    "type": "message",
    "content": "Create a todo app"
  },
  {
    "role": "assistant",
    "type": "message",
    "content": "I'll create a todo app..."
  }
]
```

### History file too large?
```python
import json
from pathlib import Path

# Keep only last N messages
history_file = Path("agent_history.json")
with open(history_file) as f:
    messages = json.load(f)

# Keep last 50 messages
trimmed = messages[-50:]

with open(history_file, 'w') as f:
    json.dump(trimmed, f, indent=2)
```

## Summary of Available Functions

| Function | Purpose | Usage |
|----------|---------|-------|
| `run()` | Start/continue with full spec | `run()` or `run(continue_from_history=True/False)` |
| `continue_conversation(msg)` | Continue with custom message | `continue_conversation("Add tests")` |
| `view_history()` | View conversation summary | `view_history()` |
| `clear_history()` | Delete all history | `clear_history()` |
| `load_history()` | Load history (returns list) | `messages = load_history()` |
| `save_history()` | Save current conversation | `save_history()` |

---

*With this system, your agent has perfect memory and can continue complex projects across multiple sessions!*
