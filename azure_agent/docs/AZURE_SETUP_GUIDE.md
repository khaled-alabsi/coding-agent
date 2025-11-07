# Azure Coding Agent Setup Guide

This guide shows how to set up and use the Azure OpenAI-based coding agent.

## Overview

The Azure Coding Agent is similar to Open Interpreter but uses Azure OpenAI services instead of local LM Studio. It provides:

- **Code Execution**: Execute bash commands, read/write files
- **History Management**: Save and resume conversations
- **Auto-Save**: Automatic periodic saving of conversation state
- **Inactivity Watchdog**: Automatically stop if agent becomes inactive
- **Azure OpenAI Integration**: Uses Azure's GPT-4 or GPT-3.5 models

## Prerequisites

### 1. Azure OpenAI Service

You need an Azure OpenAI resource with a deployed model:

1. **Create Azure OpenAI Resource**:
   - Go to [Azure Portal](https://portal.azure.com)
   - Create a new "Azure OpenAI" resource
   - Note your endpoint URL and API key

2. **Deploy a Model**:
   - In your Azure OpenAI resource, go to "Model deployments"
   - Deploy GPT-4 or GPT-3.5-Turbo
   - Note your deployment name

### 2. Python Environment

- Python 3.8 or higher
- Virtual environment (recommended)

## Installation

### Step 1: Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Or Windows
# venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

The requirements include:
- `openai>=1.0.0` - Azure OpenAI Python SDK
- Other utilities for file handling and subprocess management

### Step 3: Set Environment Variables

Create a `.env` file in the `azure_agent` directory:

```bash
# .env file
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

Or export them in your shell:

```bash
export AZURE_OPENAI_API_KEY="your_api_key_here"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="your-deployment-name"
```

## Usage

### Basic Usage

```python
from azure_agent import run

# Run the agent with default settings
run()
```

### Python Script Usage

Create a script (e.g., `run_agent.py`):

```python
from azure_agent import run, AzureCodeAgent

# Option 1: Use environment variables
run(
    continue_from_history=True,  # Continue from previous session
    inactivity_timeout=300,      # Stop after 5 minutes of inactivity
    auto_save_interval=30        # Save every 30 seconds
)

# Option 2: Pass credentials explicitly
run(
    api_key="your-api-key",
    azure_endpoint="https://your-resource.openai.azure.com/",
    deployment_name="your-deployment-name",
    continue_from_history=False,  # Start fresh
    auto_save_interval=30
)
```

### Jupyter Notebook Usage

```python
from azure_agent import AzureCodeAgent, save_history

# Create agent
agent = AzureCodeAgent(
    api_key="your-api-key",
    azure_endpoint="https://your-resource.openai.azure.com/",
    deployment_name="gpt-4"
)

# Read the project spec
from pathlib import Path
prompt_text = Path("prompt.md").read_text()

# Chat with the agent
agent.chat(f"""
Here is the project specification:

{prompt_text}

Please implement this project step by step.
""", display=True)

# Save the conversation
save_history(agent)
```

### Advanced Usage

```python
from azure_agent import (
    run,
    clear_history,
    view_history,
    AzureCodeAgent
)

# View previous conversation history
view_history()

# Clear history to start fresh
clear_history()

# Create custom agent with specific settings
agent = AzureCodeAgent(
    api_key="your-api-key",
    azure_endpoint="https://your-resource.openai.azure.com/",
    deployment_name="gpt-4",
    api_version="2024-02-15-preview"  # Specific API version
)

# Set custom working directory
agent.working_directory = Path("/path/to/project")

# Set custom max iterations
agent.max_iterations = 100

# Chat with custom prompt
response = agent.chat("Create a Python web scraper", display=True)
```

## How It Works

### Agent Actions

The agent can perform three types of actions by including special markers in its responses:

1. **BASH: \<command\>** - Execute shell commands
   ```
   BASH: npm install
   BASH: python -m pytest tests/
   ```

2. **WRITE_FILE: \<filepath\>** - Create or update files
   ```
   WRITE_FILE: src/app.py
   ```python
   def hello():
       print("Hello, World!")
   ```
   ```

3. **READ_FILE: \<filepath\>** - Read file contents
   ```
   READ_FILE: package.json
   ```

4. **COMPLETE** - Signal task completion
   ```
   All tasks completed successfully!
   COMPLETE
   ```

### Execution Flow

1. User sends initial prompt with project specification
2. Agent analyzes the spec and plans tasks
3. Agent generates actions (bash commands, file operations)
4. Actions are parsed and executed automatically
5. Results are sent back to agent
6. Agent continues until task is complete or max iterations reached
7. Conversation is saved automatically

### History Management

- **Auto-Save**: Conversation is saved every 30 seconds (configurable)
- **Manual Save**: Call `save_history(agent)` anytime
- **Resume**: Set `continue_from_history=True` to resume previous session
- **Clear**: Call `clear_history()` to start fresh

### Timeout Features

1. **Inactivity Timeout**: Stops agent if no activity for specified seconds
   ```python
   run(inactivity_timeout=300)  # Stop after 5 minutes of inactivity
   ```

2. **Max Iterations**: Prevents infinite loops (default: 50 iterations)
   ```python
   agent.max_iterations = 100
   ```

## Configuration Options

### run() Function Parameters

- `continue_from_history` (bool): Continue from saved history (default: True)
- `inactivity_timeout` (int): Seconds of inactivity before stopping (default: None)
- `auto_save_interval` (int): Seconds between auto-saves (default: 30)
- `api_key` (str): Azure OpenAI API key (optional if env var set)
- `azure_endpoint` (str): Azure endpoint URL (optional if env var set)
- `deployment_name` (str): Deployment name (optional if env var set)

### AzureCodeAgent Class Parameters

- `api_key` (str): Azure OpenAI API key
- `api_version` (str): API version (default: "2024-02-15-preview")
- `azure_endpoint` (str): Azure endpoint URL
- `deployment_name` (str): Name of deployed model

### Agent Properties

- `messages` (list): Conversation history
- `system_message` (str): System instructions for the agent
- `max_iterations` (int): Maximum conversation iterations (default: 50)
- `working_directory` (Path): Directory for file operations (default: project_dir)

## Examples

### Example 1: Create a Web Application

```python
from azure_agent import AzureCodeAgent

agent = AzureCodeAgent()

agent.chat("""
Create a Flask web application with the following features:
1. Homepage with a form to submit user data
2. Store submissions in SQLite database
3. Display all submissions on a separate page
4. Include proper error handling
5. Add CSS styling

Implement this step by step.
""", display=True)
```

### Example 2: Data Analysis Project

```python
from azure_agent import run

# Update prompt.md with data analysis spec
# Then run the agent

run(
    continue_from_history=False,
    inactivity_timeout=600,  # 10 minutes
    auto_save_interval=60    # Save every minute
)
```

### Example 3: Resume Previous Session

```python
from azure_agent import run, view_history

# Check what was done previously
view_history()

# Continue from where you left off
run(continue_from_history=True)
```

## Comparison with Open Interpreter

| Feature | Open Interpreter | Azure Coding Agent |
|---------|-----------------|-------------------|
| LLM Backend | LM Studio (local) | Azure OpenAI (cloud) |
| Installation | Complex (Rust, tiktoken issues) | Simple (pip install) |
| Code Execution | Built-in | Custom implementation |
| History Management | ✅ | ✅ |
| Auto-Save | ✅ | ✅ |
| Watchdog | ✅ | ✅ |
| Cost | Free (local) | Pay-per-use (Azure) |
| Performance | Depends on local GPU | Consistent (cloud) |
| Models | Any GGUF model | GPT-4, GPT-3.5, etc. |

## Troubleshooting

### Error: "Missing Azure OpenAI configuration"

**Solution**: Set environment variables or pass parameters:
```python
run(
    api_key="your-key",
    azure_endpoint="https://your-resource.openai.azure.com/",
    deployment_name="gpt-4"
)
```

### Error: "Resource not found"

**Problem**: Wrong endpoint or deployment name

**Solution**: Verify your Azure OpenAI resource settings:
1. Check endpoint URL in Azure Portal
2. Verify deployment name in "Model deployments"

### Error: "Unauthorized"

**Problem**: Invalid API key

**Solution**:
1. Get fresh API key from Azure Portal
2. Make sure it's for the correct resource

### Agent Gets Stuck

**Problem**: Agent in infinite loop or waiting

**Solution**:
- Use `inactivity_timeout` parameter
- Lower `max_iterations`
- Interrupt with Ctrl+C (history is saved)

### Commands Fail to Execute

**Problem**: Permission issues or wrong working directory

**Solution**:
```python
agent = AzureCodeAgent()
agent.working_directory = Path("/correct/path")
```

## Best Practices

1. **Always Use Virtual Environments**: Keep dependencies isolated

2. **Set Appropriate Timeouts**: Prevent runaway costs
   ```python
   run(inactivity_timeout=300, auto_save_interval=30)
   ```

3. **Review History Regularly**: Check what agent has done
   ```python
   view_history()
   ```

4. **Clear History for New Projects**: Start fresh
   ```python
   clear_history()
   ```

5. **Monitor Azure Costs**: GPT-4 can be expensive, use GPT-3.5 for testing

6. **Use Specific Prompts**: Clear specifications get better results

7. **Enable Display Mode**: Watch agent's progress in real-time
   ```python
   agent.chat(message, display=True)
   ```

## Security Considerations

⚠️ **Warning**: This agent can execute arbitrary code and commands!

- **Use in Safe Environments**: Don't run on production systems
- **Review Agent Actions**: Check what commands will be executed
- **Restrict Working Directory**: Limit agent to specific directories
- **Never Share API Keys**: Keep credentials secure
- **Monitor Usage**: Watch Azure OpenAI consumption

## Cost Optimization

Azure OpenAI charges per token. To minimize costs:

1. **Use GPT-3.5**: Cheaper than GPT-4
   ```python
   deployment_name="gpt-35-turbo"
   ```

2. **Set Max Tokens**: Limit response size
   ```python
   # In the agent code, modify:
   max_tokens=1000  # Instead of 2000
   ```

3. **Use Shorter Prompts**: Be concise but clear

4. **Clear Old History**: Reduce context size
   ```python
   clear_history()
   ```

5. **Set Lower Max Iterations**: Stop sooner
   ```python
   agent.max_iterations = 20
   ```

## Next Steps

1. Try the example in `prompt.md`
2. Create your own project specifications
3. Experiment with different Azure OpenAI models
4. Customize the system instructions for your use case
5. Integrate with CI/CD pipelines

## Resources

- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Azure Portal](https://portal.azure.com)

## Support

For issues or questions:
1. Check Azure OpenAI service health
2. Review agent logs in console output
3. Check `agent_history.json` for conversation details
4. Verify Azure Portal configurations

---

**Last updated**: 2025-11-07
