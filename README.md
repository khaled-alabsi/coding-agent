# Azure Code Agent - Multi-Agent Coding System

An intelligent **multi-agent coding system** that automatically generates complete, production-ready projects from natural language descriptions. Built with a modular 5-agent architecture, comprehensive logging, and support for both local LLM (LM Studio) and Azure OpenAI.

**Primary Interface**: Jupyter Notebook (`main.ipynb`)
**Primary LLM**: Local LLM via LM Studio (DeepSeek R1)

---

## 🎯 Overview

This system employs **5 specialized AI agents** that work together to transform your project ideas into complete, working code:

1. **Prompt Enhancer** → Clarifies and enhances your requirements
2. **Planner** → Creates detailed execution plans
3. **Plan Enhancer** → Validates and improves plans
4. **Coder** → Implements the code
5. **Result Validator** → Validates output and triggers fixes (up to 3 iterations)

All agent interactions, LLM requests/responses, and tool calls are logged in detail with timestamps for full transparency and debugging.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INPUT (Notebook)                     │
│                   "Create a todo app with React"                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT ORCHESTRATOR                           │
│  • Manages workflow                                             │
│  • Coordinates agents                                           │
│  • Handles logging                                              │
│  • Plays completion sounds                                      │
└────┬──────┬──────┬──────┬──────┬───────────────────────────────┘
     │      │      │      │      │
     ▼      ▼      ▼      ▼      ▼
   ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐
   │P1│  │P2│  │P3│  │C │  │V │   P1: Prompt Enhancer
   └──┘  └──┘  └──┘  └──┘  └──┘   P2: Planner
                                    P3: Plan Enhancer
     │      │      │      │      │   C:  Coder
     │      │      │      │      │   V:  Validator
     ▼      ▼      ▼      ▼      ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CORE SERVICES                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  LLM Client  │  │ File Ops     │  │ Logger       │          │
│  │ (w/ logging) │  │ (w/ logging) │  │ (JSON-based) │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└───────┬─────────────────┬─────────────────┬─────────────────────┘
        │                 │                 │
        ▼                 ▼                 ▼
  ┌──────────┐      ┌──────────┐     ┌──────────┐
  │ LM Studio│      │ File     │     │ Log File │
  │ (DeepSeek)│     │ System   │     │ (JSON)   │
  └──────────┘      └──────────┘     └──────────┘
                          │
                          ▼
                    ┌──────────┐
                    │ ./output/│  ← Generated code
                    └──────────┘
```

### Core Components

**Agent Layer**:
- `agents/prompt_enhancer.py` - Enhances user prompts for clarity
- `agents/planner.py` - Creates detailed execution plans
- `agents/plan_enhancer.py` - Validates and improves plans
- `agents/coder.py` - Implements code based on plans
- `agents/result_validator.py` - Validates output quality
- `agents/base_agent.py` - Base class with common functionality

**Core Layer**:
- `core/orchestrator.py` - Coordinates multi-agent workflow
- `core/llm_client.py` - LLM wrapper (supports Azure OpenAI + Local LLM)
- `core/file_operations.py` - File and command execution

**Utils Layer**:
- `utils/logger.py` - Comprehensive logging system
- `utils/sound.py` - Completion sound notifications
- `utils/helpers.py` - Utility functions

**Config Layer**:
- `config/settings.py` - Centralized configuration

---

## 🚀 Quick Start (Recommended: Jupyter Notebook)

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Set Up Local LLM (Recommended)

```bash
# 1. Download LM Studio from https://lmstudio.ai
# 2. Install and open LM Studio
# 3. Download model: deepseek/deepseek-r1-0528-qwen3-8b
# 4. Load the model and start local server (localhost:1234)
```

### 3. Run from Jupyter Notebook (Primary Interface)

```bash
# Start Jupyter
jupyter notebook

# Open main.ipynb and run cells
```

**Quick Start Cell** (in notebook):
```python
from azure_agent import run

# Run with local LLM (reads from prompt.md)
results = run(
    use_local_llm=True,
    local_model="deepseek/deepseek-r1-0528-qwen3-8b",
    max_fix_iterations=3  # Auto-retry up to 3 times
)

print(f"Status: {results['final_status']}")
print(f"Score: {results['validation_result'].get('score', 0)}/100")
print(f"Output: {results['output_directory']}")
```

---

## 📊 Features

### Multi-Agent Workflow
- ✅ **5 Specialized Agents** working together
- ✅ **Automatic Plan Enhancement** for better results
- ✅ **Iterative Fixing** - validator triggers up to 3 fix attempts
- ✅ **Quality Scoring** - each run gets a 0-100 score

### Code Generation
- ✅ **Complete Projects** - ALL files included (configs, README, .gitignore)
- ✅ **Production-Ready** - immediately runnable after `npm install`
- ✅ **Best Practices** - follows framework conventions
- ✅ **Full Styling** - CSS with actual content, not empty files

### Logging & Monitoring
- ✅ **Comprehensive Logging** - ALL LLM requests/responses logged
- ✅ **Tool Call Logging** - bash commands, file ops with timestamps
- ✅ **Sequential Log** - correct order of all interactions
- ✅ **JSON Format** - easy to parse and analyze
- ✅ **Sound Notifications** - plays sound when workflow completes

### LLM Support
- ✅ **Local LLM** (Primary) - LM Studio with DeepSeek R1
- ✅ **Azure OpenAI** (Optional) - GPT-4/3.5 support
- ✅ **Flexible** - easy to switch between backends

### Organization
- ✅ **Output Directory** - all generated code in `./output/`
- ✅ **Gitignored** - output directory contents ignored
- ✅ **Clean Structure** - modular, maintainable codebase

---

## 📚 Usage Examples

### Example 1: Create a Todo App (Notebook)

```python
from azure_agent import run

results = run(
    prompt="Create a modern todo app with React, TypeScript, and Tailwind CSS. Include add, delete, mark complete, and filter features.",
    use_local_llm=True,
    local_model="deepseek/deepseek-r1-0528-qwen3-8b",
    output_dir="./output/todo-app",
    max_fix_iterations=3
)
```

### Example 2: Create a REST API

```python
results = run(
    prompt="Create a REST API for a blog with Node.js, Express, and PostgreSQL. Include CRUD endpoints for posts and comments.",
    use_local_llm=True,
    output_dir="./output/blog-api"
)
```

### Example 3: Advanced Configuration

```python
results = run(
    prompt="Create a portfolio website with dark mode",
    use_local_llm=True,
    local_model="deepseek/deepseek-r1-0528-qwen3-8b",
    output_dir="./output/portfolio",

    # Workflow options
    skip_prompt_enhancement=False,  # Let agent enhance prompt
    skip_plan_enhancement=False,    # Let agent enhance plan
    max_fix_iterations=5,           # More retries for quality

    # Generation parameters
    temperature=0.7,     # Creativity level
    max_tokens=2000,     # Response length
    context_window=8000  # Context size
)

# Check results
print(f"\nStatus: {results['final_status']}")
print(f"Score: {results['validation_result'].get('score', 0)}/100")
print(f"Iterations: {results['fix_iterations']}")
print(f"Output: {results['output_directory']}")
```

### Example 4: Using CLI

```bash
# With prompt.md file
python run_agent.py

# Direct prompt
python run_agent.py "Create a calculator app"

# With options
python run_agent.py "Create a blog" --output ./my-blog --max-fixes 5
```

---

## 📝 Logging System

Every run creates a detailed log file: `agent_log_YYYYMMDD_HHMMSS.json`

### Log Structure

```json
{
  "session_id": "20250108_143022",
  "start_time": "2025-01-08T14:30:22.123456",
  "entries": [
    {
      "id": "workflow_start",
      "type": "workflow_start",
      "timestamp": 0.001,
      "time_human": "2025-01-08T14:30:22",
      "data": {"user_prompt": "Create a todo app"}
    },
    {
      "id": "Prompt Enhancer_0",
      "type": "llm_request",
      "timestamp": 0.152,
      "agent": "Prompt Enhancer",
      "data": {
        "system_message": "You are a Prompt Enhancement Specialist...",
        "messages": [{"role": "user", "content": "..."}],
        "parameters": {"temperature": 0.7, "max_tokens": 2000}
      }
    },
    {
      "id": "Prompt Enhancer_0_response",
      "type": "llm_response",
      "timestamp": 3.421,
      "agent": "Prompt Enhancer",
      "request_id": "Prompt Enhancer_0",
      "data": {
        "response": "Create a modern todo application...",
        "tokens_used": 450
      }
    },
    {
      "id": "Coder_bash_12",
      "type": "tool_call",
      "timestamp": 25.341,
      "agent": "Coder",
      "data": {
        "tool": "bash",
        "input": {"command": "npm install", "cwd": "/path/to/output"}
      }
    },
    {
      "id": "Coder_bash_12_result",
      "type": "tool_result",
      "timestamp": 28.764,
      "agent": "Coder",
      "call_id": "Coder_bash_12",
      "data": {
        "tool": "bash",
        "output": {"stdout": "...", "stderr": "", "returncode": 0, "success": true},
        "success": true
      }
    }
  ]
}
```

### Log Entry Types

- `workflow_start` - Workflow begins
- `workflow_complete` - Workflow ends
- `agent_start` - Agent begins working
- `agent_complete` - Agent finishes
- `llm_request` - Outgoing LLM request
- `llm_response` - Incoming LLM response
- `tool_call` - Tool execution begins (bash, read_file, write_file)
- `tool_result` - Tool execution result

---

## 🔧 Configuration

### Project Structure

```
azure_agent/
├── agents/                 # 5 specialized agents
│   ├── __init__.py
│   ├── base_agent.py
│   ├── prompt_enhancer.py
│   ├── planner.py
│   ├── plan_enhancer.py
│   ├── coder.py
│   └── result_validator.py
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── orchestrator.py     # Workflow coordinator
│   ├── llm_client.py       # LLM wrapper (with logging)
│   └── file_operations.py  # File ops (with logging)
├── utils/                  # Utilities
│   ├── __init__.py
│   ├── logger.py           # Comprehensive logging
│   ├── sound.py            # Sound notifications
│   └── helpers.py          # Helper functions
├── config/                 # Configuration
│   ├── __init__.py
│   └── settings.py
├── output/                 # Generated code (gitignored)
│   └── .gitkeep
├── tests/
├── docs/
├── azure_agent.py          # Main entry point
├── run_agent.py            # CLI runner
├── main.ipynb              # Jupyter interface (PRIMARY)
├── prompt.md               # Project specification
├── requirements.txt
├── .env.example
└── README.md               # This file
```

### Configuration Options

**AgentConfig** (`config/settings.py`):
```python
config = AgentConfig(
    # LLM Settings
    use_local_llm=True,
    local_model="deepseek/deepseek-r1-0528-qwen3-8b",
    local_api_base="http://localhost:1234/v1",

    # Generation Parameters
    temperature=0.7,
    max_tokens=2000,
    context_window=8000,

    # Agent Settings
    max_iterations=50,
    max_retry_attempts=3,

    # Paths
    output_dir=Path("./output"),

    # Timeouts
    command_timeout=300,  # 5 minutes
)
```

---

## 🎵 Sound Notifications

The system plays sounds when the workflow completes:

- **Success Sound** - When validation passes
- **Error Sound** - When validation fails or issues remain

Sounds are cross-platform (macOS, Windows, Linux).

---

## 🧪 Testing & Validation

Each workflow produces:

1. **Validation Score** (0-100) - Overall quality
2. **Passed Checks** - What worked well
3. **Failed Checks** - What needs improvement
4. **Critical Issues** - Must-fix problems
5. **Suggestions** - Optional improvements

The validator can trigger **up to 3 automatic fix iterations** if issues are found.

---

## 📖 Documentation

- **README.md** (This file) - Main documentation
- **main.ipynb** - Interactive notebook with examples
- **prompt.md** - Sample project specification
- **docs/LOCAL_LLM_GUIDE.md** - Local LLM setup guide
- **docs/AZURE_SETUP_GUIDE.md** - Azure OpenAI setup

---

## 🔐 Security

⚠️ **This system executes code automatically!**

**Best Practices**:
- Use in isolated development environments
- Review prompts before running
- Monitor agent actions in logs
- Don't run on production systems
- Check generated code before deploying

---

## 🛠️ Troubleshooting

### LLM Connection Issues

**Problem**: `Connection refused` to localhost:1234
**Solution**: Ensure LM Studio server is running

**Problem**: `Model not found`
**Solution**: Check exact model name in LM Studio matches config

### Quality Issues

**Problem**: Low validation score
**Solution**: Increase `max_fix_iterations` (3-5)

**Problem**: Missing files or broken imports
**Solution**: Check logs to see where agent failed; the validator should catch these

### Performance Issues

**Problem**: Slow generation
**Solution**: Use smaller model or reduce `context_window`

**Problem**: Out of memory
**Solution**: Reduce `context_window` to 4096 or lower

---

## 🚦 Workflow Phases

When you run the agent, it goes through these phases:

1. **PHASE 1: Prompt Enhancement**
   → Agent clarifies and expands your requirements

2. **PHASE 2: Planning**
   → Agent creates detailed execution plan with all files

3. **PHASE 3: Plan Enhancement**
   → Agent validates plan for completeness

4. **PHASE 4: Implementation**
   → Agent writes all code, configs, and documentation

5. **PHASE 5: Validation**
   → Agent validates output and triggers fixes if needed

6. **PHASE 6: Completion**
   → Results saved, logs written, sound played

---

## 💡 Tips & Best Practices

### For Best Results

1. **Be Specific** - "Create a todo app with React, TypeScript, and localStorage"
2. **Mention Stack** - Specify frameworks, tools, and libraries
3. **Include Features** - List key functionality
4. **Set Iterations** - Use `max_fix_iterations=5` for higher quality
5. **Review Logs** - Check `agent_log_*.json` to understand what happened

### Common Patterns

**Web App**:
```python
run(prompt="Create a [type] with [framework], [styling], and [features]")
```

**API**:
```python
run(prompt="Create a REST API for [domain] with [backend], [database], and [endpoints]")
```

**Script**:
```python
run(prompt="Create a Python script that [action] using [libraries]")
```

---

## 🎯 Comparison: Single vs Multi-Agent

| Aspect | Old Single Agent | New Multi-Agent System |
|--------|-----------------|------------------------|
| **Architecture** | Monolithic | 5 specialized agents |
| **Quality** | Variable | Validated (0-100 score) |
| **Fixing** | Manual | Automatic (up to 3 retries) |
| **Planning** | Basic | Enhanced 2-stage planning |
| **Logging** | Basic history | Comprehensive JSON logs |
| **Feedback** | Text only | Text + sound notifications |
| **Organization** | Mixed | Clean output directory |
| **Validation** | None | Dedicated validator agent |

---

## 📊 Performance

**Typical Run** (Todo App with React):
- Prompt Enhancement: ~3s
- Planning: ~5s
- Plan Enhancement: ~4s
- Implementation: ~45s
- Validation: ~8s
- **Total: ~65s**

**Log Size**: ~500KB for typical project
**Output Files**: 10-30 files depending on project

---

## 🤝 Contributing

This is a research/development project. Feel free to:
- Fork and modify
- Add new agents
- Improve prompts
- Extend logging
- Add new LLM backends

---

## 📄 License

This is a demonstration project. Use and modify as needed.

---

## 🆘 Getting Help

1. **Check Logs** - `agent_log_*.json` has all details
2. **Review Validation** - See what failed and why
3. **Adjust Config** - Try different temperature/iterations
4. **Check Model** - Ensure LM Studio server is running

---

**Built with ❤️ for autonomous software development**

Primary Interface: `main.ipynb`
Primary LLM: Local LLM (LM Studio)
Model: DeepSeek R1 (deepseek/deepseek-r1-0528-qwen3-8b)
