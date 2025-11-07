# Local LLM Setup Guide (LM Studio)

Complete guide to running the coding agent with local LLM using LM Studio.

## Prerequisites

### 1. Install LM Studio

Download and install LM Studio from [lmstudio.ai](https://lmstudio.ai/)

- Available for macOS, Windows, and Linux
- Free to use
- Supports many open-source models

### 2. Download a Model

In LM Studio:
1. Go to the "Discover" tab
2. Search for and download a coding model, for example:
   - `deepseek/deepseek-r1-0528-qwen3-8b` (recommended for coding)
   - `qwen/qwen3-coder-30b`
   - `codellama/CodeLlama-7b`
   - Any other model that fits your hardware

### 3. Start the Local Server

1. In LM Studio, load your downloaded model
2. Go to the "Local Server" tab
3. Click "Start Server"
4. Server will start at `http://localhost:1234` by default
5. Keep LM Studio running while using the agent

## Installation

### Step 1: Set Up Python Environment

```bash
cd azure_agent

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and set:

```bash
# Local LLM Configuration
LOCAL_LLM_API_BASE=http://localhost:1234/v1
LOCAL_LLM_MODEL=deepseek/deepseek-r1-0528-qwen3-8b
```

## Usage Examples

### Example 1: Basic Usage with run()

```python
from azure_agent import run

run(
    use_local_llm=True,
    local_model="deepseek/deepseek-r1-0528-qwen3-8b",
    continue_from_history=True
)
```

### Example 2: With Environment Variables

```python
from azure_agent import run
from dotenv import load_dotenv

load_dotenv()

# Will use LOCAL_LLM_MODEL and LOCAL_LLM_API_BASE from .env
run(use_local_llm=True)
```

### Example 3: Custom Configuration

```python
from azure_agent import AzureCodeAgent

agent = AzureCodeAgent(
    use_local_llm=True,
    local_api_base="http://localhost:1234/v1",
    local_model="deepseek/deepseek-r1-0528-qwen3-8b",
    context_window=8000,
    max_tokens=2000,
    temperature=0.7
)

agent.chat("Create a Python web scraper", display=True)
```

### Example 4: Using the Example Script

```bash
# Make sure LM Studio server is running
python run_local_llm.py
```

### Example 5: Jupyter Notebook

In `main.ipynb`:

```python
from azure_agent import AzureCodeAgent
from dotenv import load_dotenv

load_dotenv()

# Create agent with local LLM
agent = AzureCodeAgent(
    use_local_llm=True,
    local_model="deepseek/deepseek-r1-0528-qwen3-8b"
)

# Chat
agent.chat("Create a REST API with Flask", display=True)
```

## Configuration Parameters

### Local LLM Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `use_local_llm` | Enable local LLM mode | `False` |
| `local_api_base` | LM Studio API URL | `http://localhost:1234/v1` |
| `local_model` | Model name in LM Studio | From env var or `"local-model"` |
| `context_window` | Context window size | `8000` |
| `max_tokens` | Max tokens per response | `2000` |
| `temperature` | Generation temperature | `0.7` |

### Model-Specific Settings

Different models have different context windows:

```python
# DeepSeek Coder
agent = AzureCodeAgent(
    use_local_llm=True,
    local_model="deepseek/deepseek-r1-0528-qwen3-8b",
    context_window=8192,
    max_tokens=2048
)

# Qwen Coder
agent = AzureCodeAgent(
    use_local_llm=True,
    local_model="qwen/qwen3-coder-30b",
    context_window=32768,
    max_tokens=4096
)

# CodeLlama
agent = AzureCodeAgent(
    use_local_llm=True,
    local_model="codellama/CodeLlama-13b",
    context_window=16384,
    max_tokens=2048
)
```

## Complete Workflow

### 1. Start LM Studio Server

```bash
# In LM Studio:
# 1. Load your model (e.g., deepseek-r1-0528-qwen3-8b)
# 2. Go to "Local Server" tab
# 3. Click "Start Server"
# 4. Verify it shows: "Server running at http://localhost:1234"
```

### 2. Test the Connection

```python
from openai import OpenAI

client = OpenAI(
    api_key="lm-studio",
    base_url="http://localhost:1234/v1"
)

# Test
response = client.chat.completions.create(
    model="local-model",
    messages=[{"role": "user", "content": "Hello"}],
    temperature=0.7
)

print(response.choices[0].message.content)
```

### 3. Run the Agent

```bash
python run_local_llm.py
```

Or in Python:

```python
from azure_agent import run

run(
    use_local_llm=True,
    local_model="deepseek/deepseek-r1-0528-qwen3-8b",
    inactivity_timeout=600,  # 10 minutes
    auto_save_interval=30
)
```

## Troubleshooting

### Issue: "Connection refused"

**Problem**: LM Studio server is not running

**Solution**:
1. Open LM Studio
2. Load a model
3. Start the server in "Local Server" tab
4. Verify URL is `http://localhost:1234`

### Issue: "Model not found"

**Problem**: Model name doesn't match

**Solution**:
- Check the exact model name in LM Studio
- Use the full path as shown in LM Studio
- Or use `"local-model"` as a generic name

### Issue: Slow responses

**Problem**: Model is too large for your hardware

**Solution**:
1. Use a smaller model (7B instead of 30B)
2. Adjust `max_tokens` to be smaller
3. Close other applications
4. Check GPU memory in LM Studio settings

### Issue: Out of memory errors

**Problem**: Context window too large

**Solution**:
```python
agent = AzureCodeAgent(
    use_local_llm=True,
    context_window=4096,  # Reduce from 8000
    max_tokens=1000      # Reduce from 2000
)
```

### Issue: Agent gives poor responses

**Problem**: Model not suitable for coding tasks

**Solution**:
- Use a coding-specific model:
  - DeepSeek Coder
  - Qwen Coder
  - CodeLlama
  - StarCoder
- Adjust temperature (lower = more focused):
  ```python
  temperature=0.3  # More deterministic
  ```

### Issue: Port already in use

**Problem**: Another service is using port 1234

**Solution**:
1. Change LM Studio port in settings
2. Update your configuration:
   ```python
   local_api_base="http://localhost:5000/v1"
   ```

## Performance Tips

### 1. Choose the Right Model Size

| Hardware | Recommended Model Size |
|----------|----------------------|
| 8GB RAM | 3B-7B models |
| 16GB RAM | 7B-13B models |
| 32GB+ RAM | 13B-30B+ models |

### 2. Optimize Context Window

```python
# Small projects
context_window=4096

# Medium projects
context_window=8192

# Large projects (if hardware allows)
context_window=16384
```

### 3. Adjust Temperature

```python
# Precise, deterministic code
temperature=0.3

# Balanced
temperature=0.7

# Creative solutions
temperature=0.9
```

### 4. Use Efficient Models

Quantized models (Q4, Q5) are faster and use less memory:
- `deepseek-coder-6.7b-instruct.Q4_K_M.gguf`
- `qwen3-coder-14b.Q5_K_M.gguf`

## Comparison: Azure vs Local LLM

| Feature | Azure OpenAI | Local LLM |
|---------|--------------|-----------|
| **Cost** | Pay per token | Free (hardware cost) |
| **Speed** | Fast | Depends on hardware |
| **Privacy** | Data sent to cloud | Fully local |
| **Setup** | Simple | Requires LM Studio |
| **Models** | GPT-4, GPT-3.5 | Open source models |
| **Availability** | Internet required | Works offline |
| **Consistency** | Very consistent | Varies by model |

## Recommended Models for Coding

### Best Overall
- **DeepSeek Coder V2** (6.7B, 16B, 33B)
  - Excellent for code generation
  - Good reasoning abilities
  - Fast inference

### Best for Large Projects
- **Qwen Coder 2.5** (7B, 14B, 32B)
  - Large context window
  - Multi-language support
  - Strong at understanding existing code

### Best for Low Memory
- **Phi-3-mini** (3.8B)
  - Very efficient
  - Decent coding abilities
  - Runs on 4GB RAM

### Best for Specific Languages
- **CodeLlama** - Python, C++, Java
- **StarCoder** - Multi-language
- **WizardCoder** - General purpose

## Example Projects

### Project 1: Simple CLI Tool

```python
from azure_agent import AzureCodeAgent

agent = AzureCodeAgent(use_local_llm=True)
agent.chat("""
Create a command-line todo list manager:
- Add tasks
- List tasks
- Mark complete
- Save to JSON
""", display=True)
```

### Project 2: Web Scraper

```python
agent = AzureCodeAgent(
    use_local_llm=True,
    local_model="deepseek/deepseek-r1-0528-qwen3-8b",
    temperature=0.5
)

agent.chat("""
Create a web scraper that:
1. Scrapes headlines from a news site
2. Saves to CSV
3. Has error handling
4. Uses requests and BeautifulSoup
""", display=True)
```

### Project 3: Data Analysis

```python
agent = AzureCodeAgent(
    use_local_llm=True,
    max_tokens=3000,
    context_window=8192
)

agent.chat("""
Create a data analysis project:
1. Generate sample CSV data
2. Load with pandas
3. Perform statistical analysis
4. Create visualizations
5. Save report
""", display=True)
```

## Advanced Configuration

### Custom System Prompt

```python
agent = AzureCodeAgent(use_local_llm=True)

agent.system_message = """
You are a Python expert focused on writing clean, efficient code.
Always include type hints and docstrings.
Follow PEP 8 style guidelines.
"""

agent.chat("Create a calculator module", display=True)
```

### Multiple Agents

```python
# Code agent
coder = AzureCodeAgent(
    use_local_llm=True,
    local_model="deepseek-coder",
    temperature=0.3
)

# Creative agent
creative = AzureCodeAgent(
    use_local_llm=True,
    local_model="qwen-coder",
    temperature=0.9
)
```

### Streaming Responses

For real-time output, the agent already uses `display=True`:

```python
agent.chat("Create a web server", display=True)
# Output appears in real-time as agent works
```

## Resources

- [LM Studio Website](https://lmstudio.ai/)
- [DeepSeek Models](https://huggingface.co/deepseek-ai)
- [Qwen Models](https://huggingface.co/Qwen)
- [Code Llama](https://huggingface.co/codellama)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

## Support

For issues:
1. Check LM Studio server is running
2. Verify model is loaded
3. Test connection with simple prompt
4. Check logs in console output
5. Review `agent_history.json`

---

**Last updated**: 2025-11-07
