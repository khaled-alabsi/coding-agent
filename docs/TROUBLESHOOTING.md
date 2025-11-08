# Troubleshooting Guide

**Common issues and how to fix them**

---

## Table of Contents

1. [LLM Connection Issues](#llm-connection-issues)
2. [Truncation Problems](#truncation-problems)
3. [Validation Failures](#validation-failures)
4. [Context/Memory Issues](#context-memory-issues)
5. [File Generation Problems](#file-generation-problems)
6. [Performance Issues](#performance-issues)
7. [Configuration Problems](#configuration-problems)
8. [Sound Notification Issues](#sound-notification-issues)
9. [Import/Module Errors](#import-module-errors)
10. [Debugging Techniques](#debugging-techniques)

---

## LLM Connection Issues

### Problem: "Connection refused" or "Cannot connect to LLM"

**Symptoms**:
```
Error: Connection refused at http://localhost:1234/v1
Failed to connect to LLM server
```

**Solutions**:

1. **Check LM Studio is running**:
   ```bash
   # Test connection
   curl http://localhost:1234/v1/models
   ```

   If no response:
   - Open LM Studio
   - Go to "Local Server" tab
   - Load a model (e.g., DeepSeek R1)
   - Click "Start Server"

2. **Check port**:
   ```python
   # If using different port
   run(
       prompt="...",
       api_base="http://localhost:8080/v1"  # Custom port
   )
   ```

3. **Use cloud API instead**:
   ```python
   run(
       prompt="...",
       use_local_llm=False,
       model="gpt-4-turbo",
       api_key="sk-...",
       api_base="https://api.openai.com/v1"
   )
   ```

---

### Problem: "API key required" when using cloud API

**Symptoms**:
```
Error: API key not provided
Authentication failed
```

**Solutions**:

1. **Set API key**:
   ```python
   import os

   run(
       prompt="...",
       use_local_llm=False,  # ← Important!
       api_key=os.getenv("OPENAI_API_KEY")
   )
   ```

2. **Use environment variables**:
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=sk-..." > .env
   ```

   ```python
   from dotenv import load_dotenv
   load_dotenv()

   run(
       prompt="...",
       use_local_llm=False,
       api_key=os.getenv("OPENAI_API_KEY")
   )
   ```

3. **Check API key format**:
   - OpenAI: `sk-...`
   - Anthropic: `sk-ant-...`
   - Azure: Check Azure portal

---

### Problem: "Model not found"

**Symptoms**:
```
Error: Model 'deepseek-ai/DeepSeek-R1' not found
```

**Solutions**:

1. **Check model is loaded in LM Studio**:
   - Open LM Studio
   - Go to "Models" tab
   - Download DeepSeek R1 if not present
   - Load model in "Local Server" tab

2. **Use correct model name**:
   ```python
   # Check available models
   curl http://localhost:1234/v1/models

   # Use exact name from response
   run(
       prompt="...",
       model="deepseek-ai/DeepSeek-R1"  # Exact name
   )
   ```

---

## Truncation Problems

### Problem: "Response is truncated" or incomplete code

**Symptoms**:
- Code ends abruptly
- Missing closing braces
- Incomplete file content
- "Used: 49,999 / 50,000 tokens (100.0%)"

**Solutions**:

1. **Enable truncation detection** (should be on by default):
   ```python
   run(
       prompt="...",
       truncation_detection_enabled=True,  # Default
       auto_fix_truncation=True,  # Default
       max_continuation_attempts=3  # Default
   )
   ```

2. **Increase max_tokens**:
   ```python
   run(
       prompt="...",
       max_tokens=50000  # Increase from default
   )
   ```

3. **Check logs for truncation**:
   ```python
   from utils import ContextAnalyzer

   analyzer = ContextAnalyzer()
   stats = analyzer.analyze_log_file('output/logs/agent_log_*.json')

   if stats['truncation_detected']:
       print("Truncation occurred!")
       print(f"Max tokens needed: {stats['max_tokens_used']}")
   ```

4. **Lower truncation threshold** (detect earlier):
   ```python
   run(
       prompt="...",
       truncation_threshold=0.90  # Detect at 90% instead of 95%
   )
   ```

---

### Problem: "Auto-fix failed, still truncated"

**Symptoms**:
```
⚠️ TRUNCATION DETECTED!
🔧 Attempting continuation (attempt 1/3)
🔧 Attempting continuation (attempt 2/3)
🔧 Attempting continuation (attempt 3/3)
⚠️ Response may still be incomplete after 3 continuation attempts
```

**Solutions**:

1. **Increase continuation attempts**:
   ```python
   run(
       prompt="...",
       max_continuation_attempts=5  # Try more times
   )
   ```

2. **Simplify the task**:
   ```python
   # Instead of:
   run(prompt="Create a full-stack app with 20 features")

   # Try:
   run(prompt="Create a simple TODO app with basic features")
   ```

3. **Use higher max_tokens**:
   ```python
   run(
       prompt="...",
       max_tokens=100000  # If model supports it
   )
   ```

4. **Check model context limits**:
   ```python
   from utils import test_llm_context

   result = test_llm_context(
       max_tokens=100000,
       context_window=262144
   )

   if not result['success']:
       print(f"Model can't handle these settings: {result['error']}")
   ```

---

## Validation Failures

### Problem: "Max validation iterations exceeded"

**Symptoms**:
```
❌ Validation failed (attempt 199/200)
❌ Validation failed (attempt 200/200)
💥 Max iterations (200) reached without passing validation
```

**Solutions**:

1. **Check failure logs**:
   ```bash
   cat output/fail_logs/failure_*.json
   ```

   Look for:
   - Repeated errors (infinite loop)
   - Unrealistic requirements
   - Model capability limits

2. **Simplify requirements**:
   ```python
   # Instead of:
   run(prompt="Create a perfect production-ready app with zero bugs")

   # Try:
   run(prompt="Create a basic TODO app")
   ```

3. **Increase max_iterations** (if close to success):
   ```python
   run(
       prompt="...",
       max_iterations=300  # Give more attempts
   )
   ```

4. **Check validator prompt**:
   ```bash
   cat prompts/result_validator.md
   ```

   May be too strict - consider relaxing requirements.

5. **Disable validation temporarily** (debugging):
   ```python
   # Edit core/orchestrator.py temporarily
   # Skip validation step to see raw code output
   ```

---

### Problem: "Validation stuck in loop fixing same issue"

**Symptoms**:
- Validation reports same error repeatedly
- Code doesn't improve between iterations
- Logs show identical issues

**Solutions**:

1. **Analyze validation history**:
   ```bash
   cat output/logs/workflow_steps_*/5_validation_*.md
   ```

   Look for:
   - Repeated error messages
   - Unclear error descriptions
   - Conflicting requirements

2. **Improve validator prompt clarity**:
   ```markdown
   <!-- prompts/result_validator.md -->
   Be specific about errors:
   - Exact file name
   - Exact line number
   - Exact fix needed
   ```

3. **Add more context to coder**:
   ```markdown
   <!-- prompts/coder.md -->
   When fixing validation errors:
   1. Read the error carefully
   2. Identify root cause
   3. Fix AND verify fix
   ```

4. **Reduce temperature** (more deterministic):
   ```python
   run(
       prompt="...",
       temperature=0.0  # Most deterministic
   )
   ```

---

## Context/Memory Issues

### Problem: "Context window exceeded"

**Symptoms**:
```
Error: Context length exceeded
Total tokens (270,000) > context_window (262,144)
```

**Solutions**:

1. **Increase context_window** (if model supports it):
   ```python
   run(
       prompt="...",
       context_window=500000  # If model supports
   )
   ```

2. **Check compaction is working**:
   ```python
   # Compaction should trigger at 85% of context_window
   # Check logs for compaction events
   ```

3. **Reduce max_tokens** (leave room for context):
   ```python
   run(
       prompt="...",
       max_tokens=30000,  # Smaller responses
       context_window=262144  # Leaves room for history
   )
   ```

4. **Reset agent history manually**:
   ```python
   # If running agents directly
   coder.reset_conversation()
   validator.reset_conversation()
   ```

---

### Problem: "Agent lost context from earlier conversation"

**Symptoms**:
- Agent forgets previous decisions
- Repeated questions
- Inconsistent behavior

**Solutions**:

1. **Check compaction settings**:
   ```python
   # Compactor preserves last 6 messages by default
   # May need to increase

   # Edit utils/history_compactor.py
   self.max_recent_messages = 10  # Preserve more recent messages
   ```

2. **Disable compaction temporarily** (debugging):
   ```python
   # Edit agents/base_agent.py
   def _compact_history_if_needed(self):
       pass  # Skip compaction
   ```

3. **Use smaller tasks** (less history needed):
   ```python
   # Break large task into smaller ones
   run(prompt="Step 1: Create models")
   run(prompt="Step 2: Create views")
   ```

---

## File Generation Problems

### Problem: "Cannot GET /" when testing generated app

**Symptoms**:
```bash
curl http://localhost:3000
Cannot GET /
```

**Solutions**:

1. **Check coder created index.html or routes**:
   ```bash
   ls -la output/generated_code/project_*/
   ```

2. **Verify coder ran verification checklist**:
   ```bash
   cat output/logs/workflow_steps_*/4_code.md
   ```

   Should see:
   ```
   ✓ Created index.html
   ✓ Ran npm install
   ✓ Started dev server
   ✓ Tested with curl
   ✓ Verified NOT "Cannot GET /"
   ```

3. **Check server logs**:
   ```bash
   # If coder started server, check output
   ```

4. **Test manually**:
   ```bash
   cd output/generated_code/project_*/
   npm install
   npm run dev
   curl http://localhost:3000
   ```

---

### Problem: "Generated files are empty or incomplete"

**Symptoms**:
- CSS files empty
- JS files missing functions
- Import statements reference non-existent files

**Solutions**:

1. **Check for truncation**:
   ```python
   from utils import ContextAnalyzer

   analyzer = ContextAnalyzer()
   stats = analyzer.analyze_log_file('output/logs/agent_log_*.json')
   analyzer.print_analysis(stats)
   ```

2. **Increase max_tokens**:
   ```python
   run(
       prompt="...",
       max_tokens=50000  # Large enough for all files
   )
   ```

3. **Simplify project scope**:
   ```python
   # Instead of:
   run(prompt="Create 50 components with full styling")

   # Try:
   run(prompt="Create 5 core components")
   ```

4. **Check coder prompt includes verification**:
   ```bash
   cat prompts/coder.md | grep -A 10 "VERIFICATION"
   ```

---

## Performance Issues

### Problem: "Workflow is very slow"

**Symptoms**:
- Takes 10+ minutes for simple task
- Multiple LLM calls taking long time

**Solutions**:

1. **Disable optional enhancements**:
   ```python
   run(
       prompt="...",
       enable_prompt_enhancement=False,  # Skip (default)
       enable_plan_enhancement=False  # Skip (default)
   )
   ```

2. **Reduce max_tokens** (faster generation):
   ```python
   run(
       prompt="...",
       max_tokens=10000  # Smaller = faster
   )
   ```

3. **Reduce max_iterations** (fail faster):
   ```python
   run(
       prompt="...",
       max_iterations=20  # Don't retry forever
   )
   ```

4. **Use faster model**:
   ```python
   # If using cloud API
   run(
       prompt="...",
       use_local_llm=False,
       model="gpt-3.5-turbo"  # Faster than GPT-4
   )
   ```

5. **Check LM Studio GPU usage**:
   - LM Studio > Settings > Hardware
   - Enable GPU acceleration if available

---

### Problem: "High token usage / expensive API calls"

**Symptoms**:
- Large API bills
- Many continuation attempts
- Excessive retries

**Solutions**:

1. **Reduce max_tokens**:
   ```python
   run(
       prompt="...",
       max_tokens=10000  # Smaller responses
   )
   ```

2. **Reduce max_continuation_attempts**:
   ```python
   run(
       prompt="...",
       max_continuation_attempts=1  # One retry only
   )
   ```

3. **Use cheaper model**:
   ```python
   run(
       prompt="...",
       model="gpt-3.5-turbo"  # Cheaper than GPT-4
   )
   ```

4. **Analyze token usage**:
   ```python
   from utils import ContextAnalyzer

   analyzer = ContextAnalyzer()
   stats = analyzer.analyze_log_file('output/logs/agent_log_*.json')
   analyzer.print_analysis(stats)

   print(f"Total tokens: {stats['total_tokens']}")
   print(f"Average per call: {stats['avg_tokens_per_call']}")
   ```

---

## Configuration Problems

### Problem: "Settings not being applied"

**Symptoms**:
- Configuration changes ignored
- Using default values

**Solutions**:

1. **Check you're passing settings correctly**:
   ```python
   # ❌ Wrong: Settings not passed
   run("Create app")

   # ✅ Correct: Settings passed
   run(
       prompt="Create app",
       max_tokens=30000
   )
   ```

2. **Check config loading order**:
   ```python
   # Function parameters override config defaults
   # config/settings.py defaults <- run() parameters
   ```

3. **Verify with logs**:
   ```bash
   cat output/logs/agent_log_*.json | grep "max_tokens"
   ```

---

### Problem: "Can't find config file"

**Symptoms**:
```
Error: No module named 'config'
Cannot import AgentConfig
```

**Solutions**:

1. **Check working directory**:
   ```bash
   pwd  # Should be project root
   ls config/settings.py  # Should exist
   ```

2. **Install in development mode**:
   ```bash
   pip install -e .
   ```

3. **Add to PYTHONPATH**:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:/path/to/coding-agent"
   ```

---

## Sound Notification Issues

### Problem: "No sounds playing"

**Symptoms**:
- No audio feedback
- Silent operation

**Solutions**:

1. **Check system volume**:
   - Unmute system
   - Increase volume

2. **Test sound manually**:
   ```python
   from utils import play_completion_sound

   play_completion_sound()  # Should hear sound
   ```

3. **Check platform support**:
   ```python
   import sys
   print(sys.platform)  # darwin (macOS), win32, linux
   ```

   - macOS: Uses `afplay`
   - Windows: Uses `winsound`
   - Linux: Uses `beep` or terminal bell

4. **Install beep on Linux**:
   ```bash
   sudo apt-get install beep
   ```

---

### Problem: "Wrong sound playing"

**Symptoms**:
- All events play same sound
- Unexpected sound

**Solutions**:

1. **Check sound file exists** (macOS):
   ```bash
   ls /System/Library/Sounds/Glass.aiff
   ls /System/Library/Sounds/Basso.aiff
   ```

2. **Test specific sounds**:
   ```python
   from utils import (
       play_truncation_sound,
       play_validation_failed_sound,
       play_error_sound
   )

   play_truncation_sound()  # Funk.aiff / 3 beeps
   play_validation_failed_sound()  # Sosumi.aiff / 2 beeps
   play_error_sound()  # Basso.aiff / 2 beeps
   ```

---

## Import/Module Errors

### Problem: "No module named 'azure_agent'"

**Symptoms**:
```
ModuleNotFoundError: No module named 'azure_agent'
ImportError: cannot import name 'run'
```

**Solutions**:

1. **Check virtual environment is activated**:
   ```bash
   which python  # Should point to venv
   source venv/bin/activate  # If not activated
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install in development mode**:
   ```bash
   pip install -e .
   ```

4. **Check Python path**:
   ```python
   import sys
   print(sys.path)  # Should include project directory
   ```

---

### Problem: "Circular import error"

**Symptoms**:
```
ImportError: cannot import name 'X' from partially initialized module 'Y'
```

**Solutions**:

1. **Use absolute imports**:
   ```python
   # ❌ Bad: Relative import
   from ..config import AgentConfig

   # ✅ Good: Absolute import
   from config import AgentConfig
   ```

2. **Move imports inside functions** (if necessary):
   ```python
   def my_function():
       from config import AgentConfig  # Import here
       config = AgentConfig()
   ```

---

## Debugging Techniques

### Technique 1: Enable Detailed Logging

```python
run(
    prompt="...",
    log_thinking=True,  # Include model reasoning
    log_file="output/logs/debug_{timestamp}.json"
)

# Read log
import json
with open("output/logs/debug_20251108_110714.json") as f:
    log = json.load(f)
    print(json.dumps(log, indent=2))
```

---

### Technique 2: Analyze Logs with ContextAnalyzer

```python
from utils import ContextAnalyzer

analyzer = ContextAnalyzer()
stats = analyzer.analyze_log_file('output/logs/agent_log_*.json')
analyzer.print_analysis(stats)

# Check:
# - Token usage patterns
# - Truncation occurrences
# - Large requests
# - Recommendations
```

---

### Technique 3: Test Individual Agents

```python
from agents import Coder
from config import AgentConfig
from core import LLMClient

config = AgentConfig(log_thinking=True)
llm = LLMClient(config)
coder = Coder(config, llm)

# Test directly
response = coder.chat("Create a simple function")
print(response)

# Check conversation history
print(f"Messages in history: {len(coder.messages)}")
```

---

### Technique 4: Examine Workflow Steps

```bash
ls -la output/logs/workflow_steps_*/

# Check each step
cat output/logs/workflow_steps_20251108_110714/0_original_prompt.md
cat output/logs/workflow_steps_20251108_110714/2_plan.md
cat output/logs/workflow_steps_20251108_110714/4_code.md
cat output/logs/workflow_steps_20251108_110714/5_validation_1.md
```

---

### Technique 5: Test LLM Directly

```python
from utils import test_llm_context

result = test_llm_context(
    prompt="Test prompt",
    max_tokens=50000,
    context_window=262144
)

print(f"Success: {result['success']}")
print(f"Tokens used: {result['tokens_used']}")
print(f"Response length: {len(result['response'])}")
```

---

### Technique 6: Add Debug Prints

```python
# Temporarily add debug output
# core/llm_client.py

def chat(self, messages, ...):
    print(f"[DEBUG] Calling LLM with {len(messages)} messages")
    print(f"[DEBUG] Max tokens: {max_tokens}")

    response = self.client.chat.completions.create(...)

    print(f"[DEBUG] Response tokens: {response.usage.completion_tokens}")

    return response.choices[0].message.content
```

---

## Getting More Help

If your issue isn't covered here:

1. **Check logs**:
   - `output/logs/agent_log_*.json` - LLM interactions
   - `output/logs/workflow_steps_*/` - Step-by-step workflow
   - `output/fail_logs/` - Failure reports

2. **Read documentation**:
   - [ARCHITECTURE.md](ARCHITECTURE.md) - How system works
   - [CONFIGURATION.md](CONFIGURATION.md) - All settings
   - [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Development help

3. **Search GitHub issues**:
   - Look for similar problems
   - Check closed issues for solutions

4. **Open an issue**:
   - Describe the problem
   - Include logs
   - Specify configuration
   - Provide reproduction steps

---

**Last Updated**: 2025-11-08
**Version**: 1.0.0
