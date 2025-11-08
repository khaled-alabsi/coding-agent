# Configuration Reference

**Complete guide to all settings and options**

---

## Overview

The Azure Code Agent system is configured through the `AgentConfig` dataclass in [config/settings.py](../config/settings.py). All settings have sensible defaults but can be overridden when calling `run()`.

---

## Configuration File

**Location**: `config/settings.py`

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class AgentConfig:
    """Configuration for the multi-agent system."""

    # ... all settings below ...
```

---

## LLM Settings

### `use_local_llm`
**Type**: `bool`
**Default**: `True`
**Description**: Whether to use a local LLM server (like LM Studio) or cloud API.

```python
# Local LLM (default)
run(prompt="...", use_local_llm=True)

# Cloud API
run(prompt="...", use_local_llm=False)
```

---

### `model`
**Type**: `str`
**Default**: `"deepseek-ai/DeepSeek-R1"`
**Description**: Model identifier for the LLM.

**For Local LLM** (LM Studio):
```python
run(model="deepseek-ai/DeepSeek-R1")  # Model name in LM Studio
```

**For Cloud APIs**:
```python
# OpenAI
run(use_local_llm=False, model="gpt-4")

# Anthropic Claude
run(use_local_llm=False, model="claude-3-opus-20240229")

# Azure OpenAI
run(use_local_llm=False, model="gpt-4-deployment-name")
```

---

### `api_base`
**Type**: `str`
**Default**: `"http://localhost:1234/v1"`
**Description**: Base URL for the LLM API endpoint.

**For Local LLM** (LM Studio):
```python
run(api_base="http://localhost:1234/v1")  # Default LM Studio port
```

**For Cloud APIs**:
```python
# OpenAI
run(
    use_local_llm=False,
    api_base="https://api.openai.com/v1"
)

# Azure OpenAI
run(
    use_local_llm=False,
    api_base="https://your-resource.openai.azure.com"
)

# Custom endpoint
run(api_base="http://your-server:8080/v1")
```

---

### `api_key`
**Type**: `Optional[str]`
**Default**: `None`
**Description**: API key for cloud LLM services. Not needed for local LLMs.

```python
# Local LLM (no key needed)
run(use_local_llm=True)  # api_key ignored

# Cloud API
run(
    use_local_llm=False,
    api_key="sk-..."  # Your API key
)

# Or use environment variable
import os
run(
    use_local_llm=False,
    api_key=os.getenv("OPENAI_API_KEY")
)
```

---

### `temperature`
**Type**: `float`
**Default**: `0.0`
**Range**: `0.0` to `2.0`
**Description**: Controls randomness in LLM responses.

- **0.0**: Deterministic, consistent (best for code)
- **0.3-0.7**: Balanced creativity
- **1.0+**: High creativity (may be incoherent)

```python
# Deterministic code generation (default)
run(temperature=0.0)

# More creative responses
run(temperature=0.5)

# Highly creative (not recommended for code)
run(temperature=1.5)
```

**Recommendation**: Use `0.0` for code generation, `0.3-0.5` for documentation.

---

## Context Settings

### `context_window`
**Type**: `int`
**Default**: `262144` (256K tokens)
**Description**: Maximum total tokens (prompt + response) the model can handle.

**Model Limits**:
- DeepSeek R1: 262,144 tokens
- GPT-4 Turbo: 128,000 tokens
- GPT-4: 8,192 tokens
- Claude 3 Opus: 200,000 tokens

```python
# DeepSeek R1 (default)
run(context_window=262144)

# GPT-4 Turbo
run(context_window=128000)

# Conservative setting
run(context_window=100000)
```

**Impact**: Affects when history compaction triggers (`context_window * 0.85`).

---

### `max_tokens`
**Type**: `int`
**Default**: `50000`
**Description**: Maximum tokens in LLM response.

```python
# Large responses (default)
run(max_tokens=50000)  # Can generate very long code

# Faster iteration
run(max_tokens=10000)  # Shorter responses

# Small tasks
run(max_tokens=2000)  # Quick answers
```

**Recommendation**:
- Simple tasks: 2,000-5,000
- Standard projects: 10,000-20,000
- Complex projects: 50,000+

**Note**: Must be significantly less than `context_window` to leave room for prompt.

---

## Workflow Settings

### `max_iterations`
**Type**: `int`
**Default**: `200`
**Description**: Maximum validation retry attempts before giving up.

```python
# High tolerance (default)
run(max_iterations=200)  # Keep trying

# Fail-fast mode
run(max_iterations=10)  # Give up quickly

# No auto-fix
run(max_iterations=1)  # Validate once, no retry
```

**When to adjust**:
- **Increase**: Critical projects that MUST succeed
- **Decrease**: Quick prototypes, want to see failures fast

---

### `enable_prompt_enhancement`
**Type**: `bool`
**Default**: `False`
**Description**: Whether to enhance user prompts before planning.

```python
# Default: Skip enhancement (faster)
run(prompt="Create a TODO app")

# Enable for complex/vague prompts
run(
    prompt="Create a TODO app",
    enable_prompt_enhancement=True
)
```

**Impact**: Adds 1 LLM call (Prompt Enhancer agent).

**When to enable**:
- Vague requirements
- Complex domain
- Mission-critical projects
- Learning tool (see what good prompts look like)

---

### `enable_plan_enhancement`
**Type**: `bool`
**Default**: `False`
**Description**: Whether to enhance implementation plans.

```python
# Default: Skip enhancement (faster)
run(prompt="Create a TODO app")

# Enable for production code
run(
    prompt="Create a TODO app",
    enable_plan_enhancement=True
)
```

**Impact**: Adds 1 LLM call (Plan Enhancer agent).

**When to enable**:
- Production deployments
- Security-critical applications
- Accessibility requirements
- Comprehensive testing needed

---

## Truncation Settings

### `truncation_detection_enabled`
**Type**: `bool`
**Default**: `True`
**Description**: Whether to detect when LLM responses are truncated.

```python
# Default: Detect truncation
run(truncation_detection_enabled=True)

# Disable detection
run(truncation_detection_enabled=False)
```

**Detection Methods** (see [TRUNCATION_IMPLEMENTATION_SUMMARY.md](../TRUNCATION_IMPLEMENTATION_SUMMARY.md)):
1. Token usage >= 95% of `max_tokens`
2. Response doesn't end naturally (no punctuation)
3. Missing agent-specific markers (e.g., "COMPLETE" for Coder)

---

### `auto_fix_truncation`
**Type**: `bool`
**Default**: `True`
**Description**: Whether to automatically request continuation when truncation detected.

```python
# Default: Auto-fix (recommended)
run(auto_fix_truncation=True)

# Manual handling
run(
    truncation_detection_enabled=True,  # Detect
    auto_fix_truncation=False  # But don't fix
)
```

**Auto-Fix Strategy**: Send continuation prompt "Continue from where you left off..." up to `max_continuation_attempts` times.

---

### `max_continuation_attempts`
**Type**: `int`
**Default**: `3`
**Description**: Maximum times to request continuation for truncated responses.

```python
# Default: Try 3 times
run(max_continuation_attempts=3)

# More aggressive
run(max_continuation_attempts=5)

# One shot only
run(max_continuation_attempts=1)
```

**Cost**: Each continuation is a full LLM call.

---

### `truncation_threshold`
**Type**: `float`
**Default**: `0.95` (95%)
**Range**: `0.0` to `1.0`
**Description**: Token usage percentage to consider truncated.

```python
# Default: 95%
run(truncation_threshold=0.95)

# More aggressive
run(truncation_threshold=0.90)  # Detect at 90%

# Only exact hits
run(truncation_threshold=0.99)  # Detect at 99%
```

**Recommendation**: Keep at `0.95` for good balance.

---

## Logging Settings

### `log_file`
**Type**: `str`
**Default**: `"output/logs/agent_log_{timestamp}.json"`
**Description**: Path template for agent interaction logs.

```python
# Default location
run(log_file="output/logs/agent_log_{timestamp}.json")

# Custom location
run(log_file="/var/logs/agents/my_log_{timestamp}.json")

# Simple name
run(log_file="output/logs/my_agent.json")
```

**Template Variables**:
- `{timestamp}`: Current timestamp (YYYYMMDD_HHMMSS)

**Log Format**:
```json
{
  "timestamp": "2025-11-08T10:30:45.123",
  "agent_name": "Coder",
  "model": "deepseek-ai/DeepSeek-R1",
  "temperature": 0.0,
  "max_tokens": 50000,
  "system_prompt": "...",
  "messages": [...],
  "response": "...",
  "has_thinking_tags": true,
  "truncation_detected": false,
  "continuation_attempt": 0
}
```

---

### `log_thinking`
**Type**: `bool`
**Default**: `True`
**Description**: Whether to include `<think>` tags in logs (for models that support it).

```python
# Include thinking (default)
run(log_thinking=True)  # See model's reasoning

# Strip thinking
run(log_thinking=False)  # Only final answers
```

**Models with Thinking**:
- DeepSeek R1
- OpenAI o1/o3

**Impact**: Logs can be 2-3x larger with thinking included.

---

## Sound Notification Settings

Currently, sounds are always enabled. To disable, mute system sounds or use headless environments.

**Sound Events**:
- `play_completion_sound()` - Workflow complete
- `play_error_sound()` - Critical error
- `play_warning_sound()` - Warning
- `play_truncation_sound()` - Truncation detected
- `play_validation_failed_sound()` - Validation failed
- `play_fix_attempt_sound()` - Auto-fix attempt

**Future Enhancement**: Add `enable_sounds` config option.

---

## Usage Examples

### Example 1: Quick Prototype

**Goal**: Fast iteration, don't care about edge cases

```python
from azure_agent import run

run(
    prompt="Create a simple TODO app",
    max_tokens=10000,  # Smaller responses
    max_iterations=10,  # Fail fast
    enable_prompt_enhancement=False,  # Skip
    enable_plan_enhancement=False,  # Skip
)
```

---

### Example 2: Production Application

**Goal**: High quality, comprehensive, production-ready

```python
run(
    prompt="Create a production-ready TODO app with authentication",
    max_tokens=50000,  # Large responses
    max_iterations=200,  # Keep trying
    enable_prompt_enhancement=True,  # Clarify requirements
    enable_plan_enhancement=True,  # Validate plan
    temperature=0.0,  # Deterministic
)
```

---

### Example 3: Cloud API (OpenAI)

**Goal**: Use GPT-4 instead of local LLM

```python
import os

run(
    prompt="Create a TODO app",
    use_local_llm=False,
    model="gpt-4-turbo",
    api_base="https://api.openai.com/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
    context_window=128000,  # GPT-4 Turbo limit
    max_tokens=4000,
)
```

---

### Example 4: Debugging Truncation

**Goal**: Understand truncation issues

```python
run(
    prompt="Create a large application",
    max_tokens=50000,
    truncation_detection_enabled=True,
    auto_fix_truncation=True,
    max_continuation_attempts=5,  # More attempts
    log_thinking=True,  # See full reasoning
)

# Then analyze logs
from utils import ContextAnalyzer
analyzer = ContextAnalyzer()
stats = analyzer.analyze_log_file("output/logs/agent_log_*.json")
analyzer.print_analysis(stats)
```

---

### Example 5: Conservative Resource Usage

**Goal**: Minimize token usage and cost

```python
run(
    prompt="Create a TODO app",
    max_tokens=5000,  # Small responses
    context_window=50000,  # Small context
    max_iterations=20,  # Limited retries
    enable_prompt_enhancement=False,
    enable_plan_enhancement=False,
    truncation_threshold=0.99,  # Only detect obvious truncation
)
```

---

## Environment Variables

You can use environment variables for sensitive settings:

```bash
# .env file
OPENAI_API_KEY=sk-...
AZURE_API_KEY=...
LLM_API_BASE=http://localhost:1234/v1
LLM_MODEL=deepseek-ai/DeepSeek-R1
```

```python
import os
from dotenv import load_dotenv

load_dotenv()

run(
    prompt="...",
    api_key=os.getenv("OPENAI_API_KEY"),
    api_base=os.getenv("LLM_API_BASE"),
    model=os.getenv("LLM_MODEL"),
)
```

---

## Configuration Best Practices

### 1. Start with Defaults
```python
# First run - use defaults
run(prompt="Create a TODO app")

# Analyze results
# Then adjust based on needs
```

### 2. Profile Your Use Case

**Simple tasks** (landing pages, small utilities):
```python
max_tokens=5000
max_iterations=20
enable_prompt_enhancement=False
enable_plan_enhancement=False
```

**Standard projects** (web apps, APIs):
```python
max_tokens=20000
max_iterations=100
enable_prompt_enhancement=False  # Unless vague
enable_plan_enhancement=False  # Unless production
```

**Complex projects** (full-stack apps, microservices):
```python
max_tokens=50000
max_iterations=200
enable_prompt_enhancement=True
enable_plan_enhancement=True
```

### 3. Monitor Token Usage

```python
from utils import ContextAnalyzer

analyzer = ContextAnalyzer()
stats = analyzer.analyze_log_file("output/logs/agent_log_latest.json")

# Check recommendations
optimal = analyzer.get_optimal_settings("output/logs/agent_log_latest.json")
print(f"Recommended max_tokens: {optimal['recommended_max_tokens']}")
print(f"Recommended context_window: {optimal['recommended_context_window']}")
```

### 4. Test with `llm_tester`

```python
from utils import test_llm_context

# Test your planned settings
result = test_llm_context(
    max_tokens=50000,
    context_window=262144,
    model="deepseek-ai/DeepSeek-R1"
)

if result['success']:
    print("Settings are valid!")
else:
    print(f"Failed: {result['error']}")
```

---

## Common Configuration Issues

### Issue 1: "Used 100% of tokens"

**Problem**: `max_tokens` too small for task

**Solution**:
```python
run(max_tokens=50000)  # Increase
```

---

### Issue 2: "Context window exceeded"

**Problem**: `context_window` too small or not compacting

**Solution**:
```python
run(context_window=262144)  # Increase

# History compaction should be automatic at 85%
# Check compactor is working in logs
```

---

### Issue 3: "Truncated responses even with auto-fix"

**Problem**: `max_continuation_attempts` insufficient

**Solution**:
```python
run(
    max_continuation_attempts=5,  # More attempts
    truncation_threshold=0.90  # Earlier detection
)
```

---

### Issue 4: "Too many validation retries"

**Problem**: `max_iterations` too high, impossible task

**Solution**:
```python
run(max_iterations=20)  # Fail faster

# Or improve prompt to make task achievable
```

---

### Issue 5: "API key not working"

**Problem**: Cloud API configuration incorrect

**Solution**:
```python
import os

run(
    use_local_llm=False,  # ← Must be False!
    api_key=os.getenv("OPENAI_API_KEY"),
    api_base="https://api.openai.com/v1",
    model="gpt-4-turbo"
)
```

---

## Related Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - How configuration affects system behavior
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** - Why we chose these defaults
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common configuration problems
- **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** - Setting up for development

---

**Last Updated**: 2025-11-08
**Version**: 1.0.0
