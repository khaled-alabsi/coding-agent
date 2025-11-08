# Development Guide

**Setup, contributing, testing, and code style**

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/coding-agent.git
cd coding-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run a test
python -m azure_agent "Create a TODO app"
```

---

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Project Structure](#project-structure)
3. [Running the System](#running-the-system)
4. [Development Workflow](#development-workflow)
5. [Testing](#testing)
6. [Code Style](#code-style)
7. [Contributing](#contributing)
8. [Troubleshooting](#troubleshooting)

---

## Environment Setup

### Prerequisites

- **Python**: 3.8+ (3.10+ recommended)
- **Git**: For version control
- **LM Studio** (optional): For local LLM serving

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/coding-agent.git
cd coding-agent

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install in development mode (optional)
pip install -e .
```

### Setting Up Local LLM (LM Studio)

1. **Download LM Studio**: https://lmstudio.ai/
2. **Download Model**: DeepSeek R1 (recommended)
3. **Start Server**:
   - Open LM Studio
   - Go to "Local Server" tab
   - Load DeepSeek R1 model
   - Click "Start Server"
   - Default: `http://localhost:1234`

### Setting Up Cloud API (Optional)

```bash
# Create .env file
cat > .env << EOF
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
EOF

# Load in Python
from dotenv import load_dotenv
load_dotenv()
```

---

## Project Structure

After moving `azure_agent/` to top level:

```
coding-agent/
├── agents/                    # 🧠 Agent implementations
│   ├── base_agent.py         # Base class with history compaction
│   ├── prompt_enhancer.py    # Prompt enhancement
│   ├── planner.py            # Implementation planning
│   ├── plan_enhancer.py      # Plan validation
│   ├── coder.py              # Code generation
│   └── result_validator.py   # Code validation
│
├── core/                      # 🔧 Core infrastructure
│   ├── llm_client.py         # LLM communication + truncation handling
│   ├── file_operations.py    # File I/O
│   └── orchestrator.py       # Workflow coordination
│
├── utils/                     # 🛠️ Utilities (incl. memory management)
│   ├── history_compactor.py  # History summarization
│   ├── helpers.py            # General helpers
│   ├── logger.py             # Logging system
│   ├── sound.py              # Audio notifications
│   ├── context_analyzer.py   # Token analysis
│   ├── llm_tester.py         # LLM testing
│   └── prompt_loader.py      # Prompt file loading
│
├── config/                    # ⚙️ Configuration
│   └── settings.py           # AgentConfig dataclass
│
├── prompts/                   # 📝 Agent system prompts
│   ├── prompt_enhancer.md
│   ├── planner.md
│   ├── plan_enhancer.md
│   ├── coder.md
│   └── result_validator.md
│
├── output/                    # 📁 Generated outputs
│   ├── logs/                 # Agent logs
│   ├── fail_logs/            # Failure reports
│   └── generated_code/       # Generated projects
│
├── docs/                      # 📚 Documentation
│   ├── INDEX.md              # Documentation index
│   ├── ARCHITECTURE.md       # System architecture
│   ├── COMPACTOR_DESIGN.md   # Compactor design rationale
│   ├── DESIGN_PRINCIPLES.md  # Design philosophies
│   ├── CONFIGURATION.md      # Config reference
│   ├── DEVELOPMENT_GUIDE.md  # This file
│   └── TROUBLESHOOTING.md    # Common issues
│
├── tests/                     # 🧪 Unit tests (to be added)
│
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
├── README.md                 # Project README
└── run_agent.py              # CLI entry point
```

---

## Running the System

### Basic Usage

```python
from azure_agent import run

# Simple request
result = run(prompt="Create a TODO app")

# With options
result = run(
    prompt="Create a TODO app with authentication",
    max_tokens=50000,
    enable_prompt_enhancement=True
)
```

### Command Line Interface

```bash
# Basic usage
python run_agent.py "Create a TODO app"

# With options
python run_agent.py "Create a TODO app" \
    --enable-prompt-enhancement \
    --enable-plan-enhancement \
    --max-tokens 50000

# See all options
python run_agent.py --help
```

### Jupyter Notebook

```python
# In notebook/testing.ipynb

from azure_agent import run

result = run(
    prompt="Create a simple calculator",
    max_tokens=10000
)

print(result['status'])
print(result['output_dir'])
```

---

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Edit relevant files. Common development tasks:

**Adding a new agent**:
```bash
# 1. Create agent file
touch agents/my_new_agent.py

# 2. Create prompt file
touch prompts/my_new_agent.md

# 3. Implement agent
# See existing agents for examples

# 4. Add to orchestrator workflow
# Edit core/orchestrator.py
```

**Modifying configuration**:
```bash
# Edit config/settings.py
# Add new fields to AgentConfig dataclass
```

**Adding utilities**:
```bash
# Create utility file
touch utils/my_utility.py

# Export from __init__.py
# Edit utils/__init__.py
```

### 3. Test Your Changes

```bash
# Run manual test
python run_agent.py "Create a test project"

# Check logs
ls -la output/logs/

# Analyze results (entry types: workflow_start/complete, llm_request/response, tool_call/result, agent_start/complete)
python -c "
from utils import ContextAnalyzer
analyzer = ContextAnalyzer()
stats = analyzer.analyze_log_file('output/logs/agent_log_*.json')
analyzer.print_analysis(stats)
"
```

### 4. Update Documentation

```bash
# If you changed behavior, update docs
# Edit relevant files in docs/

# If you added configuration, update:
- docs/CONFIGURATION.md
- config/settings.py docstrings

# If you changed architecture, update:
- docs/ARCHITECTURE.md
- docs/INDEX.md (if needed)
```

### 5. Commit Changes

```bash
# Stage files
git add .

# Commit with descriptive message
git commit -m "Add feature: ..."

# Push to remote
git push origin feature/your-feature-name
```

### 6. Create Pull Request

1. Go to GitHub repository
2. Click "New Pull Request"
3. Select your feature branch
4. Fill in PR template:
   - What changed
   - Why it changed
   - How to test
   - Related issues

---

## Testing

### Manual Testing

```bash
# Test basic workflow
python run_agent.py "Create a TODO app"

# Test with enhancements
python run_agent.py "Create a TODO app" \
    --enable-prompt-enhancement \
    --enable-plan-enhancement

# Test truncation handling
python run_agent.py "Create a large full-stack application" \
    --max-tokens 10000  # Force truncation

# Test validation retries
python run_agent.py "Create an intentionally buggy app" \
    --max-iterations 5
```

### Testing Utilities

**Test LLM Context**:
```python
from utils import test_llm_context

result = test_llm_context(
    max_tokens=50000,
    context_window=262144
)

print(f"Success: {result['success']}")
print(f"Tokens used: {result['tokens_used']}")
```

**Analyze Logs**:
```python
from utils import ContextAnalyzer

analyzer = ContextAnalyzer()
stats = analyzer.analyze_log_file('output/logs/agent_log_20251108_110714.json')
analyzer.print_analysis(stats)

# Get recommendations
optimal = analyzer.get_optimal_settings('output/logs/agent_log_20251108_110714.json')
print(optimal)
```

### Unit Tests (Future)

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=azure_agent tests/
```

---

## Code Style

### Python Style Guide

We follow **PEP 8** with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes `"` for strings, single `'` for dict keys (flexible)
- **Imports**: Absolute imports preferred

### Formatting Tools

```bash
# Install formatters
pip install black isort flake8

# Format code
black .
isort .

# Check style
flake8 .
```

### Type Hints

Use type hints for all public functions:

```python
from typing import List, Dict, Optional

def process_messages(
    messages: List[Dict[str, str]],
    system_prompt: Optional[str] = None
) -> str:
    """Process messages and return response.

    Args:
        messages: List of conversation messages
        system_prompt: Optional system prompt

    Returns:
        LLM response text
    """
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def compact_history(messages: List[Dict], threshold: float) -> List[Dict]:
    """Compact conversation history when it exceeds threshold.

    Args:
        messages: List of conversation messages
        threshold: Token ratio threshold (0.0-1.0)

    Returns:
        Compacted message list with summary

    Raises:
        ValueError: If threshold is out of range
    """
    pass
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `BaseAgent`, `HistoryCompactor`)
- **Functions**: `snake_case` (e.g., `compact_history`, `play_sound`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_TOKENS`, `DEFAULT_MODEL`)
- **Private**: Prefix with `_` (e.g., `_internal_helper`)

### File Organization

Each file should have:

```python
"""Module docstring explaining purpose."""
from __future__ import annotations  # For forward references

# Standard library imports
import os
import sys
from typing import List, Dict, Optional

# Third-party imports
from openai import OpenAI

# Local imports
from config import AgentConfig
from utils import helpers

# Constants
DEFAULT_TEMPERATURE = 0.0
MAX_RETRIES = 3

# Classes and functions
class MyClass:
    """Class docstring."""
    pass

def my_function():
    """Function docstring."""
    pass
```

---

## Contributing

### Before Contributing

1. **Read documentation**:
   - [ARCHITECTURE.md](ARCHITECTURE.md)
   - [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)
   - This file

2. **Check existing issues**:
   - Look for related issues
   - Comment on issue if you want to work on it

3. **Discuss major changes**:
   - Open an issue first
   - Get feedback before implementing

### Contribution Types

**Bug Fixes**:
- Fix and add test
- Update docs if behavior changes
- Reference issue in commit message

**New Features**:
- Discuss in issue first
- Add tests
- Update documentation
- Add configuration if needed

**Documentation**:
- Fix typos, clarify explanations
- Add examples
- Update architecture docs

**Performance**:
- Benchmark before/after
- Document trade-offs
- Update configuration docs

### Pull Request Process

1. **Create feature branch**: `git checkout -b feature/my-feature`
2. **Make changes**: Edit code, tests, docs
3. **Test thoroughly**: Manual and automated tests
4. **Update docs**: Keep docs in sync with code
5. **Commit**: Use descriptive commit messages
6. **Push**: `git push origin feature/my-feature`
7. **Open PR**: On GitHub, with description
8. **Code review**: Address reviewer feedback
9. **Merge**: Maintainer merges when approved

### Commit Message Format

```
<type>: <short summary>

<detailed description>

Fixes #<issue_number>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples**:
```
feat: Add support for Claude API

- Add Claude API client wrapper
- Update configuration with Anthropic settings
- Add tests for Claude integration

Fixes #123
```

```
fix: Resolve truncation detection for short responses

- Check response length before applying threshold
- Add minimum token check (100 tokens)
- Update tests

Fixes #456
```

---

## Development Tips

### 1. Use Jupyter Notebook for Exploration

```python
# notebook/testing.ipynb

from agents import Coder
from config import AgentConfig
from core import LLMClient

config = AgentConfig(log_thinking=True)
llm = LLMClient(config)
coder = Coder(config, llm)

# Test agent directly
response = coder.chat("Create a simple function...")
print(response)
```

### 2. Enable Detailed Logging

```python
from azure_agent import run

result = run(
    prompt="...",
    log_thinking=True,  # Include model reasoning
    log_file="output/logs/debug_{timestamp}.json"
)

# Check logs
import json
with open("output/logs/debug_20251108_110714.json") as f:
    log = json.load(f)
    print(json.dumps(log, indent=2))
```

### 3. Test Individual Agents

```python
from agents import Planner
from config import AgentConfig
from core import LLMClient

config = AgentConfig()
llm = LLMClient(config)
planner = Planner(config, llm)

plan = planner.chat("Create a TODO app")
print(plan)
```

### 4. Profile Token Usage

```python
from utils import ContextAnalyzer

analyzer = ContextAnalyzer()

# Analyze logs from multiple runs
for log_file in glob("output/logs/agent_log_*.json"):
    stats = analyzer.analyze_log_file(log_file)
    print(f"\n{log_file}:")
    analyzer.print_analysis(stats)
```

### 5. Test Truncation Handling

```python
# Force truncation for testing
result = run(
    prompt="Create a very large application...",
    max_tokens=5000,  # Small limit to force truncation
    truncation_detection_enabled=True,
    auto_fix_truncation=True,
    max_continuation_attempts=3
)

# Check if truncation was handled
# Look for sounds or check logs
```

---

## Common Development Tasks

### Adding a New Configuration Option

1. **Update dataclass**:
```python
# config/settings.py
@dataclass
class AgentConfig:
    # ... existing fields ...

    # New option
    my_new_option: bool = True  # Add default
```

2. **Use in code**:
```python
# agents/my_agent.py
if self.config.my_new_option:
    # Do something
    pass
```

3. **Document**:
```markdown
<!-- docs/CONFIGURATION.md -->
### `my_new_option`
**Type**: `bool`
**Default**: `True`
**Description**: What this option does...
```

### Adding a New Sound

1. **Add function**:
```python
# utils/sound.py
def play_my_sound():
    """Play a sound for my event."""
    if sys.platform == "darwin":
        subprocess.run(["afplay", "/System/Library/Sounds/Hero.aiff"])
    # ... other platforms
```

2. **Export**:
```python
# utils/__init__.py
from .sound import play_my_sound

__all__ = [
    # ... existing ...
    'play_my_sound'
]
```

3. **Use**:
```python
# core/llm_client.py
from utils import play_my_sound

def some_function():
    play_my_sound()
```

### Modifying Agent Prompts

1. **Edit markdown file**:
```bash
# prompts/coder.md
# Edit the system prompt
```

2. **Reload prompts** (if running interactively):
```python
from utils import reload_prompts
reload_prompts()
```

3. **Test**:
```python
from azure_agent import run
result = run(prompt="Test the modified prompt...")
```

---

## Troubleshooting Development Issues

### Import Errors

```python
# If you get import errors:
# 1. Check you're in project root
cd /path/to/coding-agent

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install in development mode
pip install -e .
```

### LM Studio Not Responding

```bash
# Check server is running
curl http://localhost:1234/v1/models

# If no response:
# 1. Open LM Studio
# 2. Go to "Local Server" tab
# 3. Click "Start Server"
```

### Logs Not Generated

```python
# Check output directory exists
import os
os.makedirs("output/logs", exist_ok=True)

# Run with explicit log path
result = run(
    prompt="...",
    log_file="output/logs/test_{timestamp}.json"
)
```

---

## Related Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[CONFIGURATION.md](CONFIGURATION.md)** - All configuration options
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** - Why things are designed this way

---

**Last Updated**: 2025-11-08
**Version**: 1.0.0
