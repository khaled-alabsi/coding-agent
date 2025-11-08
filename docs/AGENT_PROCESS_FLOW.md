# Multi-Agent System: Process Flow & Memory Architecture

**Goal**: Understanding and enhancing memory management across agents

---

## 1. AGENT WORKFLOW

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER PROMPT (Input)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: Prompt Enhancer (Optional - can skip)                │
│  ─────────────────────────────────────────────────────────────  │
│  Memory: Fresh (no history)                                     │
│  Input: Raw user prompt                                         │
│  Output: Enhanced, detailed prompt                              │
│  Pass: Enhanced prompt → Next phase                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: Planner                                               │
│  ─────────────────────────────────────────────────────────────  │
│  Memory: Fresh (no history)                                     │
│  Input: Enhanced prompt                                         │
│  Output: Execution plan (steps, files, structure)              │
│  Pass: Plan → Next phase                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: Plan Enhancer (Optional - can skip)                  │
│  ─────────────────────────────────────────────────────────────  │
│  Memory: Fresh (no history)                                     │
│  Input: Raw plan from Planner                                   │
│  Output: Validated & enhanced plan                              │
│  Pass: Enhanced plan → Next phase                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 4: Coder (Has internal loop)                            │
│  ─────────────────────────────────────────────────────────────  │
│  Memory: CONVERSATION HISTORY                                   │
│  - Stores all user/assistant messages                           │
│  - Auto-compacts when approaching context limit                 │
│  - Internal loop max: 50 iterations                             │
│                                                                  │
│  Loop Flow:                                                      │
│  1. Receive plan                                                 │
│  2. Generate response (code/commands)                            │
│  3. Parse WRITE_FILE, READ_FILE, BASH                           │
│  4. Execute actions → get results                                │
│  5. Feed results back to conversation                            │
│  6. Continue until "COMPLETE" or max iterations                  │
│                                                                  │
│  Pass: Implementation result → Validation                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 5: Result Validator (External validation loop)          │
│  ─────────────────────────────────────────────────────────────  │
│  Memory: CONVERSATION HISTORY (per validation attempt)          │
│  - Fresh at start                                                │
│  - Accumulates during fix attempts                               │
│                                                                  │
│  Validation Loop (max: max_fix_iterations):                      │
│  ┌────────────────────────────────────────────────┐            │
│  │ 1. Validate code (check files, imports, etc)   │            │
│  │ 2. Generate validation result                   │            │
│  │    ├─ PASS → Exit loop ✅                      │            │
│  │    └─ FAIL → Continue                           │            │
│  │ 3. Generate fix instructions                    │            │
│  │ 4. Reset Coder memory (fresh start)            │◄───┐       │
│  │ 5. Send fix to Coder                            │    │       │
│  │ 6. Coder re-implements                          │    │       │
│  │ 7. Loop back to step 1                          │────┘       │
│  └────────────────────────────────────────────────┘            │
│                                                                  │
│  If max retries reached → Generate FAIL LOG ❌                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   OUTPUT (Generated Code)                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. MEMORY ARCHITECTURE

### 2.1 Memory Types

| Agent               | Memory Type        | Persistence            | Compaction |
|---------------------|-------------------|------------------------|------------|
| Prompt Enhancer     | Stateless         | None (one-shot)        | N/A        |
| Planner             | Stateless         | None (one-shot)        | N/A        |
| Plan Enhancer       | Stateless         | None (one-shot)        | N/A        |
| **Coder**           | **Conversational**| **Entire execution**   | **YES**    |
| **Result Validator**| **Conversational**| **Per fix iteration**  | **YES**    |

### 2.2 BaseAgent Memory Structure

```python
class BaseAgent:
    self.messages: List[Dict[str, str]] = []
    # Format:
    # [
    #   {"role": "user", "content": "..."},
    #   {"role": "assistant", "content": "..."},
    #   {"role": "user", "content": "..."},
    #   ...
    # ]
```

**Key Points:**
- Messages stored in chronological order
- User/assistant alternating pattern
- Thinking tags stripped before storage (logged separately)
- Full conversation sent to LLM on each request

### 2.3 History Compaction (Automatic Memory Management)

**Trigger**: When total tokens reach 85% of context window

**Process**:
1. **Estimate tokens**: `len(text) / 4` (rough approximation)
2. **Check limit**: `trigger_limit = context_window * 0.85`
3. **If exceeded**:
   - Keep last 6 messages as-is (recent context)
   - Summarize older messages in chunks of 8
   - Create system message with summary
   - New structure: `[summary_message] + [recent_6_messages]`

**Example**:
```
Before compaction (25 messages):
[msg1, msg2, msg3, ... msg25]

After compaction:
[
  {role: "system", content: "Conversation summary: Created TODO app..."},
  msg20, msg21, msg22, msg23, msg24, msg25
]
```

**Compaction Settings** (configurable):
- `trigger_ratio`: 0.85 (85% of context)
- `max_recent_messages`: 6
- `min_recent_messages`: 2
- `summary_chunk_size`: 8 messages per summary

---

## 3. CRITICAL LOOPS

### 3.1 Coder Internal Loop

```
Coder.execute_plan()
  │
  ├─► Send plan to LLM (with conversation history)
  │
  └─► Loop (max 50 iterations):
       ├─ Get LLM response
       ├─ Parse actions (WRITE_FILE, READ_FILE, BASH)
       ├─ Execute actions
       ├─ Format results
       ├─ Add results to conversation history ◄─┐
       ├─ Send to LLM                           │ MEMORY GROWS
       └─ Check "COMPLETE" → Exit or Loop ──────┘
```

**Memory Impact**:
- Each iteration adds 2 messages (user: results, assistant: response)
- History grows: 2 + 4 + 6 + 8... messages
- Auto-compaction kicks in when needed

### 3.2 Validation Fix Loop

```
Orchestrator.execute_workflow()
  │
  └─► Validation Loop (max 3 iterations):
       │
       ├─ Validator validates implementation
       │   └─ Uses its own conversation history
       │
       ├─ If PASS → Exit ✅
       │
       ├─ If FAIL:
       │   ├─ Generate fix instructions
       │   ├─ **Reset Coder memory** (FRESH START) ◄─── KEY!
       │   ├─ Send fix to Coder
       │   │   └─ Coder runs full internal loop again
       │   └─ Loop back to validation
       │
       └─ If max retries → Save FAIL LOG ❌
```

**Key Insight**: Coder gets a **fresh start** on each fix iteration to avoid confusion from previous failed attempts.

---

## 4. MEMORY PASS FLOW

```
User Prompt
    │
    ├─► Prompt Enhancer: NO MEMORY
    │   Output: enhanced_prompt (string)
    │
    ├─► Planner: NO MEMORY
    │   Input: enhanced_prompt
    │   Output: plan (string)
    │
    ├─► Plan Enhancer: NO MEMORY
    │   Input: plan
    │   Output: enhanced_plan (string)
    │
    ├─► Coder: WITH MEMORY ◄──────────────┐
    │   Input: enhanced_plan               │
    │   Memory: [plan, actions, results]   │ GROWS
    │   Output: implementation (string)    │
    │                                       │
    └─► Validator: WITH MEMORY             │
        Input: enhanced_plan + implementation
        Memory: [validation attempts]
        │
        └─► If FAIL → Reset Coder memory ──┘
            Send fix → Coder starts fresh
```

---

## 5. MEMORY ENHANCEMENT OPPORTUNITIES

### 5.1 Current Issues

1. **Coder Memory Loss on Reset**
   - Pro: Prevents confusion from failed attempts
   - Con: Loses learned context (working solutions, file structure)

2. **No Cross-Agent Memory**
   - Validator doesn't know what Coder learned
   - Plan Enhancer can't learn from previous failures

3. **No Persistent Knowledge**
   - Each session starts from scratch
   - No learning across similar projects

4. **Limited History Compaction**
   - Summarization loses detail
   - No semantic preservation of important info

### 5.2 Enhancement Ideas

#### A. **Selective Memory Reset** (Easy - High Impact)
```python
# Instead of full reset:
coder.reset_conversation()

# Keep important context:
coder.reset_conversation(preserve=[
    "file_structure",  # Keep known files
    "working_patterns",  # Keep successful patterns
    "constraints"  # Keep requirements
])
```

#### B. **Shared Knowledge Base** (Medium - High Impact)
```python
class SharedMemory:
    def __init__(self):
        self.file_structure = {}
        self.successful_patterns = []
        self.known_issues = []
        self.constraints = {}

    def update_from_coder(self, implementation):
        # Extract file structure
        # Record successful patterns

    def inject_into_context(self, agent):
        # Add to agent's system prompt or first message
```

#### C. **Smarter Compaction** (Hard - High Impact)
```python
# Current: Summarize oldest 8 messages
# Enhanced: Preserve based on importance

class SmartCompactor:
    def compact(self, messages):
        # Extract and preserve:
        # - File paths and structures
        # - Error messages and solutions
        # - Explicit requirements
        # - Successful commands

        # Summarize:
        # - Exploratory attempts
        # - Redundant information
```

#### D. **Validation Memory Continuity** (Easy - Medium Impact)
```python
# Pass validation history to Coder on fix
fix_context = f"""
Previous validation attempts:
{validation_history}

What worked:
{successful_fixes}

What didn't work:
{failed_attempts}

New fix instructions:
{fix_instructions}
"""
```

#### E. **Semantic Memory Extraction** (Hard - High Impact)
```python
class SemanticMemory:
    """Extract key facts before compaction"""

    def extract_facts(self, messages):
        return {
            "files_created": [...],
            "dependencies_installed": [...],
            "errors_resolved": [...],
            "commands_used": [...],
            "working_directory": "...",
        }

    def inject_as_context(self, facts):
        return f"""
        Known Facts:
        - Files: {facts['files_created']}
        - Dependencies: {facts['dependencies_installed']}
        ...
        """
```

---

## 6. RECOMMENDED ENHANCEMENTS

### Priority 1: Validation Memory Context (Quick Win)
**Where**: `orchestrator.py` line 208
```python
# Current:
self.coder.reset_conversation()
self.implementation_result = self.coder.execute_plan(
    f"FIX THE FOLLOWING ISSUES:\n\n{fix_instructions}\n\n"
    f"Original Plan for reference:\n{self.enhanced_plan}"
)

# Enhanced:
validation_context = self._build_validation_context(iteration_history)
self.coder.reset_conversation()
self.implementation_result = self.coder.execute_plan(
    f"{validation_context}\n\n"
    f"FIX THE FOLLOWING ISSUES:\n\n{fix_instructions}\n\n"
    f"Original Plan for reference:\n{self.enhanced_plan}"
)
```

### Priority 2: File Structure Memory (Medium Effort)
**Where**: `base_agent.py` - add file tracking
```python
class BaseAgent:
    def __init__(self, ...):
        self.messages = []
        self.known_files = set()  # Track created files
        self.file_structure = {}  # Track directory structure

    def _extract_file_info(self, response):
        # Parse WRITE_FILE actions
        # Update known_files and file_structure
```

### Priority 3: Smart Compaction (High Effort)
**Where**: `utils/history_compactor.py` - enhance summarization
- Extract file paths, imports, errors before summarizing
- Preserve as structured data in summary message
- Format for easy LLM parsing

---

## 7. CONFIGURATION VALUES

**Current Settings** (from `config/settings.py`):
```python
context_window: 262144  # ~262k tokens
max_tokens: 35500       # Max response size
max_iterations: 50      # Coder loop limit
max_retry_attempts: 10  # Validation fix limit
```

**Memory Compaction** (from `utils/history_compactor.py`):
```python
trigger_ratio: 0.85           # 85% of context window
max_recent_messages: 6        # Keep last 6 messages
min_recent_messages: 2        # Minimum to preserve
summary_chunk_size: 8         # Messages per summary
response_buffer_tokens: 1024  # Reserve for response
```

---

## 8. DEBUGGING MEMORY ISSUES

### Check if compaction occurred:
```python
# In base_agent.py line 116:
if result.compacted:
    print(f"⚠️  History compacted! {len(original)} → {len(result.messages)} messages")
```

### Monitor memory usage:
```python
from utils.context_analyzer import ContextAnalyzer

analyzer = ContextAnalyzer()
stats = analyzer.analyze_log_file('agent_log_*.json')
analyzer.print_analysis(stats)
```

### Check for truncation:
Look for responses that:
- End abruptly mid-sentence
- Are exactly at max_tokens limit
- Don't include "COMPLETE" marker

---

## 9. KEY TAKEAWAYS

1. **Only Coder & Validator have memory** - other agents are stateless
2. **Coder loops internally** (max 50) with growing conversation history
3. **Validation loops externally** (max 3) with Coder reset each time
4. **Auto-compaction at 85%** of context window to prevent overflow
5. **Memory reset on fix** prevents confusion but loses context
6. **No cross-agent learning** - each agent isolated
7. **Enhancement opportunity**: Add selective memory preservation during resets

---

**Next Steps**: Implement Priority 1 (Validation Memory Context) for immediate improvement with minimal risk.
