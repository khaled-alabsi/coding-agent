# Azure Coding Agent

An autonomous coding agent that supports both **Azure OpenAI** (cloud) and **Local LLM** (LM Studio). Similar to Open Interpreter but with flexible backend options.

## 🚀 New: Local LLM Support!

You can now use this agent with **local models via LM Studio** - no cloud API needed!

```python
from azure_agent import run

# Use with local LM Studio
run(
    use_local_llm=True,
    local_model="deepseek/deepseek-r1-0528-qwen3-8b"
)
```

See [LOCAL_LLM_GUIDE.md](LOCAL_LLM_GUIDE.md) for complete setup instructions.

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Your Backend

**Option A: Local LLM (Free, Private)** ⭐ Recommended for your use case

```bash
# 1. Install and open LM Studio (https://lmstudio.ai)
# 2. Download deepseek/deepseek-r1-0528-qwen3-8b
# 3. Load the model and start server
# 4. Update .env:
cp .env.example .env
# Edit .env and set LOCAL_LLM_MODEL=deepseek/deepseek-r1-0528-qwen3-8b
```

**Option B: Azure OpenAI (Cloud-based)**

```bash
cp .env.example .env
# Edit .env with your Azure credentials:
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_ENDPOINT
# - AZURE_OPENAI_DEPLOYMENT
```

### 3. Run the Agent

**Option A: With Local LLM** (Your DeepSeek model)

```python
from azure_agent import run

# Use your local LM Studio
run(
    use_local_llm=True,
    local_model="deepseek/deepseek-r1-0528-qwen3-8b"
)
```

Or use the provided script:
```bash
python run_local_llm.py
```

**Option B: With Azure OpenAI**

```python
from azure_agent import run

# Use Azure OpenAI
run()
```

**Option C: Direct Usage**

```python
from azure_agent import AzureCodeAgent

# Local LLM
agent = AzureCodeAgent(
    use_local_llm=True,
    local_model="deepseek/deepseek-r1-0528-qwen3-8b"
)

# Or Azure
agent = AzureCodeAgent()

agent.chat("Create a Python calculator CLI", display=True)
```

**Option D: Jupyter Notebook**

Open `main.ipynb` and run the cells.

## Features

- ✅ **Code Execution**: Run bash commands and Python code
- ✅ **File Operations**: Read and write files automatically
- ✅ **History Management**: Save and resume conversations
- ✅ **Auto-Save**: Periodic automatic saves
- ✅ **Inactivity Watchdog**: Auto-stop after inactivity
- ✅ **Azure OpenAI**: Powered by GPT-4 or GPT-3.5
- ✅ **Project-Based**: Works within project directory
- ✅ **Verbose Mode**: See real-time progress

## Usage Examples

### Example 1: Simple Task

```python
from azure_agent import AzureCodeAgent

agent = AzureCodeAgent()
response = agent.chat("""
Create a simple Python script that:
1. Takes a filename as argument
2. Counts the number of words in that file
3. Prints the result
""", display=True)
```

### Example 2: With Timeouts

```python
from azure_agent import run

run(
    continue_from_history=False,
    inactivity_timeout=300,  # Stop after 5 min of inactivity
    auto_save_interval=60    # Save every minute
)
```

### Example 3: Resume Previous Session

```python
from azure_agent import run, view_history

# View what was done before
view_history()

# Continue from where you left off
run(continue_from_history=True)
```

## How It Works

The agent:
1. Receives your project specification from `prompt.md`
2. Plans the implementation steps
3. Executes commands and creates files
4. Checks results and continues
5. Saves progress automatically

### Agent Actions

The agent uses special markers in responses:

- `BASH: <command>` - Execute shell commands
- `WRITE_FILE: <path>` - Create/update files
- `READ_FILE: <path>` - Read file contents
- `COMPLETE` - Signal completion

## File Structure

```
azure_agent/
├── azure_agent.py          # Main agent implementation
├── prompt.md               # Project specification
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .env                   # Your credentials (git-ignored)
├── agent_history.json     # Conversation history (auto-generated)
├── run_local_llm.py       # Example script for local LLM
├── main.ipynb            # Jupyter notebook interface
├── README.md             # This file
├── AZURE_SETUP_GUIDE.md  # Azure OpenAI setup guide
└── LOCAL_LLM_GUIDE.md    # Local LLM setup guide
```

## Documentation

- **[LOCAL_LLM_GUIDE.md](LOCAL_LLM_GUIDE.md)** - Complete guide for using with LM Studio ⭐
- [AZURE_SETUP_GUIDE.md](AZURE_SETUP_GUIDE.md) - Azure OpenAI setup and usage
- [prompt.md](prompt.md) - Sample project specification

## Comparison with Open Interpreter

| Feature | Open Interpreter | This Agent |
|---------|-----------------|-------------|
| Backend | LM Studio (local) | **Azure OpenAI OR Local LLM** |
| Setup | Complex (Rust, tiktoken) | Simple (pip install) |
| Cost | Free | Free (local) or Pay-per-use (Azure) |
| Performance | GPU-dependent | Consistent (Azure) or GPU-dependent (local) |
| Models | Any GGUF model | GPT-4/3.5 or any LM Studio model |
| Flexibility | Local only | **Both cloud and local** |

## Configuration

Edit `prompt.md` to specify your project requirements, then run the agent.

### Key Parameters

**For Local LLM:**
```python
run(
    use_local_llm=True,                        # Enable local LLM mode
    local_model="deepseek/deepseek-r1-0528-qwen3-8b",  # Your model
    local_api_base="http://localhost:1234/v1", # LM Studio URL
    context_window=8000,                       # Model context size
    max_tokens=2000,                           # Max response length
    temperature=0.7,                           # Creativity (0-1)
    continue_from_history=True,                # Resume previous session
    inactivity_timeout=300,                    # Timeout after 5 min
    auto_save_interval=30                      # Save every 30 sec
)
```

**For Azure OpenAI:**
```python
run(
    use_local_llm=False,         # Use Azure (default)
    api_key=None,                # Or set AZURE_OPENAI_API_KEY
    azure_endpoint=None,         # Or set AZURE_OPENAI_ENDPOINT
    deployment_name=None,        # Or set AZURE_OPENAI_DEPLOYMENT
    continue_from_history=True,
    inactivity_timeout=300,
    auto_save_interval=30
)
```

## Utility Functions

```python
from azure_agent import (
    run,              # Run the agent
    clear_history,    # Clear conversation history
    view_history,     # View conversation summary
    force_save,       # Manual save
    AzureCodeAgent    # Agent class
)
```

## Security Warning

⚠️ **This agent executes code and commands automatically!**

- Use in safe, isolated environments
- Review `prompt.md` before running
- Monitor agent actions
- Don't run on production systems

## Troubleshooting

### "Missing Azure OpenAI configuration"
- Set environment variables in `.env`
- Or pass parameters to `run()`

### "Resource not found"
- Check endpoint URL and deployment name in Azure Portal

### Agent gets stuck
- Use `inactivity_timeout` parameter
- Press Ctrl+C to interrupt (history is saved)

### High costs
- Use GPT-3.5 instead of GPT-4
- Set lower `max_iterations`
- Monitor Azure OpenAI usage in portal

## Getting Azure OpenAI Access

1. Go to [Azure Portal](https://portal.azure.com)
2. Create an "Azure OpenAI" resource
3. Deploy a model (GPT-4 or GPT-3.5-Turbo)
4. Get your API key and endpoint
5. Use them in `.env` file

## License

This is a demonstration project. Modify and use as needed.

## Contributing

Feel free to extend and customize for your needs!

---

For detailed documentation, see [AZURE_SETUP_GUIDE.md](AZURE_SETUP_GUIDE.md)
