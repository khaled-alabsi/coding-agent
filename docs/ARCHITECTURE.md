# Azure Code Agent - System Architecture

**Understanding the multi-agent coding system**

---

## Overview

Azure Code Agent is a multi-agent system that generates complete software projects from natural language descriptions. It uses 5 specialized agents working in sequence, each with a specific role in the development pipeline.

**Key Features:**
- Multi-agent pipeline with specialization
- Automatic error detection and fixing
- Memory compaction for long conversations
- Truncation detection and auto-continuation
- Comprehensive logging and debugging
- Support for local and cloud LLMs

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                             │
│          "Create a TODO app with React and TypeScript"          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                                │
│  Coordinates agent workflow, manages state, handles retries     │
└────┬───────┬────────┬────────┬────────┬───────────────────────┬┘
     │       │        │        │        │                       │
     ▼       ▼        ▼        ▼        ▼                       ▼
┌─────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐          ┌──────────┐
│ Prompt  │ │ Plan │ │ Plan │ │ Code │ │ Vali │          │  SHARED  │
│Enhancer │ │ ner  │ │Enhan │ │  r   │ │ dator│          │ SERVICES │
│         │ │      │ │ cer  │ │      │ │      │          │          │
│ 🎯      │ │ 📋   │ │ ✅   │ │ 💻   │ │ 🔍   │          │ LLMClient│
│         │ │      │ │      │ │      │ │      │          │ FileOps  │
│Stateless│ │Stateless│Stateless│Stateful│Stateful│       │ Compactor│
│         │ │      │ │      │ │      │ │      │          │ Logger   │
└────┬────┘ └───┬──┘ └───┬──┘ └───┬──┘ └───┬──┘          └──────────┘
     │          │        │        │        │
     │  Enhanced Prompt  │        │        │
     └───────────►───────┘        │        │
                │    Plan         │        │
                └─────────►───────┘        │
                         │  Enhanced Plan  │
                         └─────────►───────┘
                                  │  Code   │
                                  └────►────┘
                                       │ Validation
                                       └─────────┐
                                                 │
                         ┌───────────────────────┘
                         │
                         ▼
                    ┌─────────┐
                    │ SUCCESS?│
                    └────┬────┘
                         │
              ┌──────────┴──────────┐
              │                     │
             YES                   NO
              │                     │
              ▼                     ▼
        ┌──────────┐         ┌──────────┐
        │ COMPLETE │         │ RETRY    │
        │ ✅       │         │ (N times)│
        └──────────┘         └────┬─────┘
                                  │
                                  └──► Back to Coder
```

---

## Agents Overview

### 1. Prompt Enhancer 🎯
**Type**: Stateless
**Optional**: Yes (disabled by default)
**Purpose**: Clarifies and enriches user requests

**Input**: Raw user prompt
**Output**: Enhanced prompt with:
- Explicit requirements
- Technical constraints
- Success criteria
- Potential edge cases

**Example**:
```
Input:  "Create a TODO app"
Output: "Create a TODO application with:
         - Add/remove/edit tasks
         - Mark tasks as complete
         - Local storage persistence
         - Responsive design
         - TypeScript + React
         - Input validation
         - Empty state handling"
```

**When to enable**: Complex or ambiguous requirements

---

### 2. Planner 📋
**Type**: Stateless
**Purpose**: Breaks down requirements into implementation plan

**Input**: Enhanced prompt (or original if enhancer disabled)
**Output**: Structured implementation plan with:
- File structure
- Component breakdown
- Data models
- Implementation steps
- Technology choices

**Example**:
```markdown
## Implementation Plan

### File Structure
- src/components/TodoList.tsx
- src/components/TodoItem.tsx
- src/hooks/useTodos.ts
- src/types/todo.ts

### Implementation Steps
1. Define TypeScript interfaces
2. Create useTodos hook with localStorage
3. Build TodoItem component
4. Build TodoList component
5. Add styling with Tailwind CSS
```

---

### 3. Plan Enhancer ✅
**Type**: Stateless
**Optional**: Yes (disabled by default)
**Purpose**: Validates and improves the plan

**Input**: Initial plan
**Output**: Enhanced plan with:
- Missing edge cases identified
- Validation logic added
- Error handling improved
- Accessibility considerations
- Testing suggestions

**When to enable**: Mission-critical projects, production code

---

### 4. Coder 💻
**Type**: Stateful (maintains conversation history)
**Purpose**: Generates actual code from the plan

**Input**: Enhanced plan
**Output**: Complete project with all files

**Responsibilities:**
- Create all source files
- Write complete, working code
- Handle imports and dependencies
- Follow best practices
- Run verification checklist (see below)

**Verification Checklist** (from [coder.md:87-104](../azure_agent/prompts/coder.md#L87-L104)):
1. Create all referenced files
2. CSS files contain actual styling (not empty)
3. Run `npm install`
4. Start development server
5. Test with `curl http://localhost:<port>`
6. Verify response is NOT "Cannot GET /"
7. Fix any errors before marking COMPLETE

**Memory Management**:
- Maintains conversation history
- Uses HistoryCompactor when approaching context limit
- Preserves recent messages for context

---

### 5. Result Validator 🔍
**Type**: Stateful (maintains conversation history)
**Purpose**: Reviews code quality and completeness

**Input**: Generated code
**Output**: Validation report with:
- Quality assessment (PASS/FAIL)
- Issues found
- Recommendations
- Missing files or logic

**Validation Criteria:**
- All planned files exist
- Code is complete and functional
- No syntax errors
- Proper error handling
- Dependencies are correct
- Follows project structure

**Auto-Fix Flow**:
```
Validator finds issues
      ↓
Plays validation_failed_sound
      ↓
Sends issues to Coder
      ↓
Coder fixes and resubmits
      ↓
Validator re-checks
      ↓
Repeat up to max_iterations (200)
```

---

## Core Components

### LLMClient
**Location**: [core/llm_client.py](../azure_agent/core/llm_client.py)

**Responsibilities:**
- Communicate with LLM (local or cloud)
- Handle API requests/responses
- Detect truncated responses
- Auto-fix truncation with continuations
- Log all interactions
- Play notification sounds

**Truncation Detection** (from [TRUNCATION_IMPLEMENTATION_SUMMARY.md](../TRUNCATION_IMPLEMENTATION_SUMMARY.md)):
```python
def _detect_truncation(self, response, max_tokens, agent_name, response_text):
    # Method 2: Response Ending Analysis
    # 1. Check if tokens used >= 95% of max_tokens
    # 2. Check if response ends naturally (punctuation, markers)
    # 3. Check agent-specific completion markers
    return {'truncated': True/False, 'used_tokens': N, ...}
```

**Auto-Fix Strategy** (Strategy 1: Continuation Request):
```python
def _handle_truncation(self, truncation_info, ...):
    play_truncation_sound()  # Alert user
    for attempt in range(1, max_continuation_attempts + 1):
        # Request continuation: "Continue from where you left off"
        # Merge responses
        # Check if still truncated
    return full_response
```

---

### HistoryCompactor
**Location**: [history/compactor.py](../azure_agent/history/compactor.py)
**Design Doc**: [COMPACTOR_DESIGN.md](COMPACTOR_DESIGN.md)

**Purpose**: Summarize old conversation history to stay within context window

**How It Works**:
1. Estimate total tokens in conversation
2. If > 85% of context_window, trigger compaction
3. Summarize old messages (using LLM)
4. Preserve recent messages (last 6)
5. Return compacted message list

**Used By**: All stateful agents (Coder, Validator) via BaseAgent

**Configuration**:
- `trigger_ratio`: 0.85 (85% of context window)
- `max_recent_messages`: 6
- `summary_chunk_size`: 8 messages per summary

---

### Orchestrator
**Location**: [core/orchestrator.py](../azure_agent/core/orchestrator.py)

**Responsibilities:**
- Manage agent workflow
- Pass data between agents
- Handle retries and error recovery
- Log workflow steps
- Generate final output

**Workflow**:
```python
def run_workflow(user_prompt):
    # 1. Optional: Enhance prompt
    if enable_prompt_enhancement:
        enhanced_prompt = prompt_enhancer.chat(user_prompt)
    else:
        enhanced_prompt = user_prompt

    # 2. Create plan
    plan = planner.chat(enhanced_prompt)

    # 3. Optional: Enhance plan
    if enable_plan_enhancement:
        enhanced_plan = plan_enhancer.chat(plan)
    else:
        enhanced_plan = plan

    # 4. Generate code
    code = coder.chat(enhanced_plan)

    # 5. Validate and fix
    for iteration in range(max_iterations):
        validation = validator.chat(code)
        if validation == "PASS":
            break
        # Auto-fix: Send issues back to coder
        code = coder.chat(f"Fix these issues: {validation}")

    # 6. Save output
    return save_project(code)
```

---

## Data Flow

### Message Format
All agents communicate using OpenAI-compatible message format:
```python
{
    "role": "user" | "assistant" | "system",
    "content": "message text",
    "name": "optional_identifier"  # Used by HistoryCompactor
}
```

### Stateless Agents (Enhancers, Planner)
```
Input → Agent → Output
(No memory retained)
```

### Stateful Agents (Coder, Validator)
```
Input → [Conversation History] → Agent → Output
                ↑                           ↓
                └───────── Append ──────────┘

When history grows too large:
[Old Messages] → Compactor → [Summary] + [Recent Messages]
```

---

## File Organization

```
coding-agent/
├── azure_agent/              # Main package
│   ├── agents/              # 🧠 Intelligence layer
│   │   ├── base_agent.py    # Base class with compaction
│   │   ├── prompt_enhancer.py
│   │   ├── planner.py
│   │   ├── plan_enhancer.py
│   │   ├── coder.py
│   │   └── result_validator.py
│   │
│   ├── core/                # 🔧 Infrastructure layer
│   │   ├── llm_client.py    # LLM communication + truncation handling
│   │   ├── file_operations.py
│   │   └── orchestrator.py  # Workflow coordination
│   │
│   ├── history/             # 💾 Memory management layer
│   │   ├── compactor.py     # History summarization
│   │   └── __init__.py
│   │
│   ├── utils/               # 🛠️ Utilities layer
│   │   ├── helpers.py       # General helpers
│   │   ├── logger.py        # Logging system
│   │   ├── sound.py         # Audio notifications
│   │   ├── context_analyzer.py  # Token analysis
│   │   └── llm_tester.py    # LLM testing
│   │
│   ├── config/              # ⚙️ Configuration layer
│   │   └── settings.py      # AgentConfig dataclass
│   │
│   ├── prompts/             # 📝 Prompt templates
│   │   ├── prompt_enhancer.md
│   │   ├── planner.md
│   │   ├── plan_enhancer.md
│   │   ├── coder.md
│   │   └── result_validator.md
│   │
│   └── output/              # 📁 All outputs (logs, code, failures)
│       ├── logs/            # agent_log_*.json, workflow_steps_*/
│       ├── fail_logs/       # Failure reports
│       └── generated_code/  # Generated projects
│
├── docs/                    # 📚 Documentation
│   ├── INDEX.md            # Documentation index (start here!)
│   ├── ARCHITECTURE.md     # This file
│   ├── COMPACTOR_DESIGN.md # Why compactor is in history/
│   └── ...                 # Other docs
│
└── README.md               # Project README
```

**Design Principle**: Clear separation of concerns
- `agents/` = Intelligence (decision makers)
- `core/` = Infrastructure (plumbing)
- `history/` = Memory management
- `utils/` = General utilities
- `config/` = Configuration
- `prompts/` = Agent instructions
- `output/` = ALL outputs (logs, code, failures)

---

## Configuration

**Location**: [config/settings.py](../azure_agent/config/settings.py)

**Key Settings**:
```python
@dataclass
class AgentConfig:
    # LLM Settings
    use_local_llm: bool = True
    model: str = "deepseek-ai/DeepSeek-R1"
    api_base: str = "http://localhost:1234/v1"
    temperature: float = 0.0

    # Context Settings
    context_window: int = 262144  # 256K tokens
    max_tokens: int = 50000       # Max response size

    # Workflow Settings
    max_iterations: int = 200     # Max validation retries

    # Enhancement Toggles
    enable_prompt_enhancement: bool = False  # Disabled by default
    enable_plan_enhancement: bool = False    # Disabled by default

    # Truncation Settings
    truncation_detection_enabled: bool = True
    auto_fix_truncation: bool = True
    max_continuation_attempts: int = 3
    truncation_threshold: float = 0.95  # 95% of max_tokens

    # Logging
    log_file: str = "output/logs/agent_log_{timestamp}.json"
    log_thinking: bool = True
```

**Usage**:
```python
from azure_agent import run

# Use defaults
results = run(prompt="Create a TODO app")

# Override settings
results = run(
    prompt="Create a TODO app",
    max_tokens=32000,
    temperature=0.3,
    enable_prompt_enhancement=True
)
```

---

## Sound Notifications

**Location**: [utils/sound.py](../azure_agent/utils/sound.py)

Different sounds for different events:

| Event | Function | macOS Sound | Other Platforms |
|-------|----------|-------------|-----------------|
| Workflow complete | `play_completion_sound()` | Glass.aiff | 1 beep |
| Critical error | `play_error_sound()` | Basso.aiff | 2 beeps |
| Warning | `play_warning_sound()` | Ping.aiff | 1 beep |
| Truncation detected | `play_truncation_sound()` | Funk.aiff | 3 beeps |
| Validation failed | `play_validation_failed_sound()` | Sosumi.aiff | 2 beeps |
| Auto-fix attempt | `play_fix_attempt_sound()` | Blow.aiff | 1 beep |

---

## Logging System

### Agent Logs
**Location**: `output/logs/agent_log_{timestamp}.json`

**Format**:
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

### Workflow Steps
**Location**: `output/logs/workflow_steps_{timestamp}/`

**Contents**:
- `0_original_prompt.md` - User's request
- `1_prompt_enhanced.md` - Enhanced prompt (if enabled)
- `2_plan.md` - Initial plan
- `3_plan_enhanced.md` - Enhanced plan (if enabled)
- `4_code.md` - Generated code
- `5_validation_N.md` - Validation reports
- `final_result.md` - Complete output

### Failure Logs
**Location**: `output/fail_logs/failure_{timestamp}.json`

**Triggered when**: Validation fails after max_iterations

---

## Error Handling

### 1. Truncated Responses
**Detection**: [llm_client.py:_detect_truncation](../azure_agent/core/llm_client.py)
```python
# Check token usage >= 95%
# Check response endings
# Check agent-specific markers
```

**Auto-Fix**: [llm_client.py:_handle_truncation](../azure_agent/core/llm_client.py)
```python
# Play sound
# Request continuation
# Merge responses
# Repeat up to 3 times
```

### 2. Validation Failures
**Detection**: ResultValidator checks code quality

**Auto-Fix**: Orchestrator sends issues back to Coder
```python
for iteration in range(max_iterations):
    validation = validator.validate(code)
    if validation.passed:
        break
    play_validation_failed_sound()
    code = coder.fix(validation.issues)
```

### 3. Context Overflow
**Detection**: HistoryCompactor checks token count

**Auto-Fix**: Compact old messages, preserve recent ones
```python
if tokens > 85% of context_window:
    messages = compactor.compact(messages)
```

---

## Testing and Debugging

### Testing LLM Context
```python
from azure_agent.utils import test_llm_context

result = test_llm_context(
    max_tokens=50000,
    context_window=262144
)
# Tests actual context limits
```

### Analyzing Logs
```python
from azure_agent.utils import ContextAnalyzer

analyzer = ContextAnalyzer()
stats = analyzer.analyze_log_file('output/logs/agent_log_*.json')
analyzer.print_analysis(stats)
# Shows token usage, truncation, recommendations
```

---

## Extension Points

### Adding New Agents
1. Inherit from `BaseAgent`
2. Implement `agent_name` and `system_prompt`
3. Create prompt file in `prompts/`
4. Add to orchestrator workflow

### Adding New Memory Strategies
1. Add to `history/` folder
2. Implement compaction interface
3. Update `BaseAgent` to use it

### Adding New LLM Providers
1. Update `LLMClient.__init__()`
2. Add provider-specific configuration
3. Test with `llm_tester.py`

---

## Performance Considerations

### Token Management
- **Context window**: 262,144 tokens (256K)
- **Max response**: 50,000 tokens
- **Compaction trigger**: 85% of context window
- **Recent messages preserved**: 6

### Optimization Tips
1. Disable enhancers for simple tasks (default)
2. Reduce `max_iterations` for faster failures
3. Use smaller `max_tokens` for focused tasks
4. Enable `truncation_detection` (default: on)

---

## Related Documentation

- **[INDEX.md](INDEX.md)** - Documentation entry point
- **[COMPACTOR_DESIGN.md](COMPACTOR_DESIGN.md)** - Why compactor is in history/
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** - Core design philosophies
- **[CONFIGURATION.md](CONFIGURATION.md)** - Complete configuration reference
- **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** - Setup and contributing
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues

---

**Last Updated**: 2025-11-08
**Version**: 1.0.0
