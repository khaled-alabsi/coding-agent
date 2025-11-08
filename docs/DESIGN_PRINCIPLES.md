# Design Principles

**Why we made the decisions we made**

---

## Core Philosophy

This multi-agent coding system is built on three foundational principles:

1. **Separation of Concerns** - Each component has one clear responsibility
2. **Composability** - Utilities are composed, not inherited
3. **Fail-Fast with Auto-Recovery** - Detect problems early and fix automatically

---

## 1. Agent Specialization

### Principle
**Each agent is an expert in one domain, not a generalist.**

### Why
- **Focused prompts** → Better quality output
- **Easier to debug** → Know which agent failed
- **Parallel development** → Can improve agents independently
- **Clearer testing** → Test one capability at a time

### Implementation
```python
# ❌ BAD: One agent doing everything
class GeneralAgent:
    def do_everything(self, prompt):
        # Enhance, plan, code, validate all in one
        pass

# ✅ GOOD: Specialized agents
class Planner(BaseAgent):
    """Only creates implementation plans."""

class Coder(BaseAgent):
    """Only generates code from plans."""

class ResultValidator(BaseAgent):
    """Only validates code quality."""
```

### Trade-offs
- **Pro**: Higher quality, easier maintenance
- **Con**: More components to manage
- **Decision**: Quality over simplicity

---

## 2. Stateless vs Stateful Agents

### Principle
**Agents that need context are stateful. Agents that transform input → output are stateless.**

### Why
Stateful agents (Coder, Validator):
- Need conversation history for iterative refinement
- Build on previous responses
- Remember context across multiple calls
- Example: "Fix the bug I mentioned earlier"

Stateless agents (Enhancers, Planner):
- Transform input once and done
- No iterative refinement needed
- Faster and simpler
- Example: "Here's a plan for your request"

### Implementation

**Stateful** (maintains `self.messages`):
```python
class Coder(BaseAgent):
    def chat(self, user_message):
        self.messages.append({"role": "user", "content": user_message})
        self._compact_history_if_needed()  # Use compactor
        response = self.llm_client.chat(self.messages, ...)
        self.messages.append({"role": "assistant", "content": response})
        return response
```

**Stateless** (no memory):
```python
class Planner(BaseAgent):
    def chat(self, user_message):
        # Just transform input → output
        response = self.llm_client.chat(
            [{"role": "user", "content": user_message}],
            system_message=self.system_prompt
        )
        return response  # No history stored
```

### Trade-offs
- **Stateful**: More context, higher memory usage, needs compaction
- **Stateless**: Fast, simple, but can't remember previous interactions
- **Decision**: Use state only when necessary

---

## 3. Enhancement Agents are Optional

### Principle
**Prompt and Plan Enhancement are disabled by default.**

### Why
1. **Speed** - Enhancement adds 2 extra LLM calls
2. **Cost** - More API calls = higher cost
3. **Diminishing returns** - Simple tasks don't need enhancement
4. **User control** - Let users opt-in for complex tasks

### When to Enable

**Enable Prompt Enhancement when:**
- User request is vague or ambiguous
- Requirements are incomplete
- Edge cases need to be identified
- Mission-critical application

**Enable Plan Enhancement when:**
- Production-grade code needed
- Security is critical
- Accessibility is required
- Comprehensive testing needed

### Usage
```python
# Default: Fast workflow
run(prompt="Create a TODO app")
# No enhancement

# Complex task: Enable enhancement
run(
    prompt="Create a TODO app",
    enable_prompt_enhancement=True,
    enable_plan_enhancement=True
)
```

### Trade-offs
- **Pro**: 2x-3x faster default workflow
- **Con**: May miss edge cases in simple mode
- **Decision**: Optimize for common case (simple tasks)

---

## 4. Utilities as Services, Not Inheritance

### Principle
**Agents USE utilities through composition, not inheritance.**

### Why
See [COMPACTOR_DESIGN.md](COMPACTOR_DESIGN.md) for detailed rationale.

**TL;DR:**
- Compactor is a service, not an agent
- All agents share one compactor instance
- Clear separation: agents = intelligence, utilities = infrastructure
- Easier to test, maintain, and extend

### Implementation
```python
# ✅ GOOD: Composition
class BaseAgent:
    def __init__(self, config, llm_client):
        self.compactor = HistoryCompactor(config, llm_client)  # HAS-A

    def _compact_history_if_needed(self):
        result = self.compactor.compact(self.messages, ...)  # USES

# ❌ BAD: Inheritance
class BaseAgent(HistoryCompactor):  # IS-A (wrong!)
    pass
```

### File Organization
```
project/
├── agents/          # 🧠 Intelligence (decision makers)
│   ├── coder.py
│   └── planner.py
│
├── utils/           # 🛠️ Shared utilities (used BY agents)
│   ├── history_compactor.py  # Memory compaction
│   └── helpers.py
```

### Trade-offs
- **Pro**: Clear boundaries, reusable services, easier testing
- **Con**: Slightly more setup code
- **Decision**: Maintainability over brevity

---

## 5. Auto-Fix with Iteration Limits

### Principle
**Automatically retry failed validations, but cap iterations to prevent infinite loops.**

### Why
1. **User experience** - Don't fail on first error
2. **LLM capability** - Models can self-correct given feedback
3. **Safety** - Iteration limit prevents runaway costs
4. **Transparency** - User sees all attempts in logs

### Implementation
```python
for iteration in range(max_iterations):  # Default: 200
    validation = validator.chat(code)

    if "PASS" in validation:
        return code  # Success!

    # Auto-fix: Send issues back to coder
    play_validation_failed_sound()
    code = coder.chat(f"Fix these issues:\n{validation}")

# If we get here, max iterations exceeded
play_error_sound()
save_failure_log()
```

### Configuration
```python
config = AgentConfig(
    max_iterations=200  # Adjust based on task complexity
)
```

### Trade-offs
- **Pro**: Resilient to transient failures
- **Con**: Can waste tokens on impossible tasks
- **Decision**: Default to high limit (200), let users adjust

---

## 6. Truncation Detection and Auto-Fix

### Principle
**Detect truncated responses dynamically and automatically request continuations.**

### Why
See [TRUNCATION_IMPLEMENTATION_SUMMARY.md](../TRUNCATION_IMPLEMENTATION_SUMMARY.md) for implementation details.

1. **Quality** - Incomplete responses are useless
2. **Transparency** - User knows truncation happened (sound notification)
3. **Automation** - No manual intervention needed
4. **Safety** - Limited to 3 continuation attempts

### Detection Methods

**Method 2: Response Ending Analysis** (current implementation)
```python
def _detect_truncation(response, max_tokens, agent_name, response_text):
    # 1. Check token usage >= 95% of max_tokens
    if response.usage.completion_tokens >= max_tokens * 0.95:
        return True

    # 2. Check if response ends naturally
    if not ends_with_natural_punctuation(response_text):
        return True

    # 3. Check agent-specific markers
    if agent_name == "Coder" and "COMPLETE" not in response_text:
        return True

    return False
```

### Auto-Fix Strategy

**Strategy 1: Continuation Request** (current implementation)
```python
def _handle_truncation(original_response, ...):
    play_truncation_sound()  # 🔊 Alert user

    full_response = original_response
    for attempt in range(max_continuation_attempts):  # Max 3
        play_fix_attempt_sound()  # 🔊 Trying fix

        continuation = llm.chat([
            ...original_messages,
            {"role": "assistant", "content": full_response},
            {"role": "user", "content": "Continue from where you left off"}
        ])

        full_response += "\n" + continuation

        if not still_truncated(continuation):
            return full_response  # ✅ Fixed!

    return full_response  # ⚠️ Still truncated but tried
```

### Sound Notifications
Different sounds for different events (see [ARCHITECTURE.md](ARCHITECTURE.md#sound-notifications)):
- **Truncation detected**: Funk.aiff (3 beeps)
- **Fix attempt**: Blow.aiff (1 beep)
- **Validation failed**: Sosumi.aiff (2 beeps)
- **Critical error**: Basso.aiff (2 beeps)
- **Success**: Glass.aiff (1 beep)

### Trade-offs
- **Pro**: Automatic recovery, user awareness, high success rate
- **Con**: Extra LLM calls, may still fail after 3 attempts
- **Decision**: Enable by default, allow opt-out

---

## 7. Memory Compaction at 85% Threshold

### Principle
**Summarize old conversation history when token usage exceeds 85% of context window.**

### Why
1. **Proactive** - Prevent truncation before it happens
2. **Headroom** - Leave space for next response (15% buffer)
3. **Preserve context** - Keep recent messages intact (last 6)
4. **LLM-powered** - Use LLM to create intelligent summaries

### Implementation
```python
class HistoryCompactor:
    def compact(self, messages, system_prompt, context_window):
        trigger_limit = context_window * 0.85  # 85%
        total_tokens = estimate_tokens(messages, system_prompt)

        if total_tokens <= trigger_limit:
            return messages  # No compaction needed

        # Preserve recent messages
        recent = messages[-6:]  # Last 6 messages
        old = messages[:-6]     # Everything before

        # Summarize old messages using LLM
        summary = llm.chat("Summarize this conversation: ..." + old)

        # Return [summary] + [recent messages]
        return [{"role": "system", "content": summary}] + recent
```

### Why 85%?
- **Too high (95%)**: Risk truncation before compaction
- **Too low (50%)**: Waste tokens on unnecessary summaries
- **85%**: Sweet spot with safety buffer

### Why Keep Last 6 Messages?
- Provides immediate context
- Usually 1-2 full exchanges (user + assistant)
- Preserves task-specific details
- Configurable via `max_recent_messages`

### Trade-offs
- **Pro**: Prevents context overflow, intelligent summarization
- **Con**: Extra LLM call for summarization, may lose some details
- **Decision**: 85% threshold, 6 recent messages

---

## 8. All Outputs in One Place

### Principle
**All logs, generated code, and failure reports go in `output/` folder.**

### Why
1. **Organization** - One place to look for all outputs
2. **Git ignore** - Easy to exclude from version control
3. **Cleanup** - Easy to clear all generated files
4. **Portability** - Copy `output/` to share results

### Structure
```
project/
└── output/
    ├── logs/                      # Agent interaction logs
    │   ├── agent_log_*.json      # Detailed LLM logs
    │   └── workflow_steps_*/     # Step-by-step workflow
    │
    ├── fail_logs/                 # Failure reports
    │   └── failure_*.json        # When validation fails
    │
    └── generated_code/            # Successfully generated projects
        └── project_*/
```

### Previously (BAD)
```
project/
├── agent_log_*.json              # ❌ Root clutter
├── workflow_steps_*/             # ❌ Root clutter
├── azure_agent/
│   ├── fail_logs/                # ❌ Wrong location
│   └── output/
│       └── generated_code/       # ❌ Partial output
```

### Trade-offs
- **Pro**: Clean, organized, easy to manage
- **Con**: Requires updating existing code paths
- **Decision**: Worth the migration effort

---

## 9. Explicit Configuration Over Magic

### Principle
**All behavior is controlled by explicit configuration, not hidden defaults.**

### Why
1. **Predictability** - Users know what to expect
2. **Debuggability** - Can reproduce issues with same config
3. **Flexibility** - Easy to adjust for different use cases
4. **Documentation** - Config file serves as documentation

### Implementation
```python
@dataclass
class AgentConfig:
    # LLM Settings
    use_local_llm: bool = True
    model: str = "deepseek-ai/DeepSeek-R1"
    api_base: str = "http://localhost:1234/v1"
    temperature: float = 0.0

    # Context Settings
    context_window: int = 262144
    max_tokens: int = 50000

    # Workflow Settings
    max_iterations: int = 200
    enable_prompt_enhancement: bool = False
    enable_plan_enhancement: bool = False

    # Truncation Settings
    truncation_detection_enabled: bool = True
    auto_fix_truncation: bool = True
    max_continuation_attempts: int = 3
    truncation_threshold: float = 0.95

    # Logging
    log_file: str = "output/logs/agent_log_{timestamp}.json"
    log_thinking: bool = True
```

### No Magic Numbers
```python
# ❌ BAD: Magic numbers
if tokens > 262000:  # What's this number?
    compact()

# ✅ GOOD: Explicit config
if tokens > config.context_window * config.truncation_threshold:
    compact()
```

### Trade-offs
- **Pro**: Transparent, flexible, documented
- **Con**: More verbose, longer config file
- **Decision**: Clarity over brevity

---

## 10. Fail-Fast with Rich Diagnostics

### Principle
**When something goes wrong, fail immediately with detailed information.**

### Why
1. **Debugging** - Rich logs help identify root cause
2. **User experience** - Clear error messages
3. **Iteration** - Fail fast, fix fast, retry
4. **Accountability** - Know which component failed

### Implementation

**Logging**:
```python
# Every LLM call is logged
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
  "continuation_attempt": 0,
  "error": null  # Or error details if failed
}
```

**Workflow Steps**:
```
output/logs/workflow_steps_20251108_110714/
├── 0_original_prompt.md
├── 1_prompt_enhanced.md
├── 2_plan.md
├── 3_plan_enhanced.md
├── 4_code.md
├── 5_validation_1.md
├── 5_validation_2.md
└── final_result.md
```

**Failure Reports**:
```python
# When max_iterations exceeded
{
  "timestamp": "...",
  "reason": "Max validation iterations exceeded",
  "iterations": 200,
  "last_validation": "...",
  "last_code": "...",
  "config": {...}
}
```

### Trade-offs
- **Pro**: Excellent debuggability, clear error tracking
- **Con**: Large log files, disk space usage
- **Decision**: Debuggability is worth the disk space

---

## 11. Human-in-the-Loop via Sounds

### Principle
**Use sound notifications to keep user informed without interrupting workflow.**

### Why
1. **Non-blocking** - User can do other work while agents run
2. **Immediate awareness** - Know when something happens
3. **Context switching** - Different sounds = different events
4. **Accessibility** - Audio cues for visual impairment

### Sound Strategy
```python
# Success/Completion
play_completion_sound()  # "Everything's done!"

# Warnings (non-critical)
play_truncation_sound()  # "Response truncated, fixing..."
play_validation_failed_sound()  # "Code has issues, retrying..."
play_fix_attempt_sound()  # "Attempting auto-fix..."

# Errors (critical)
play_error_sound()  # "Something failed!"
```

### Cross-Platform Support
```python
if sys.platform == "darwin":  # macOS
    subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"])
elif sys.platform == "win32":  # Windows
    import winsound
    winsound.MessageBeep(winsound.MB_OK)
else:  # Linux
    print("\a")  # Terminal bell
```

### Trade-offs
- **Pro**: Great UX, non-blocking, accessible
- **Con**: May annoy users in quiet environments
- **Decision**: Implement with easy opt-out (mute system sounds)

---

## 12. Configuration Defaults Favor Production

### Principle
**Default settings prioritize quality and reliability over speed.**

### Why
Users can always opt for faster/cheaper settings, but can't recover from poor quality defaults.

### Examples

**Context Window**: 262,144 tokens (max supported by DeepSeek R1)
- Allows long conversations without compaction
- Supports complex projects
- Users can reduce if needed

**Max Tokens**: 50,000 (large responses)
- Allows complete code generation
- Reduces truncation risk
- Users can reduce for faster iteration

**Max Iterations**: 200 (many retries)
- High tolerance for auto-fix attempts
- Prioritizes success over speed
- Users can reduce for fail-fast behavior

**Temperature**: 0.0 (deterministic)
- Consistent, predictable output
- Better for code generation
- Users can increase for creativity

**Truncation Detection**: Enabled
- Auto-recovery from truncation
- Better user experience
- Users can disable for raw responses

### Trade-offs
- **Pro**: High-quality defaults, production-ready
- **Con**: Slower, higher token usage
- **Decision**: Quality over speed by default

---

## Summary

| Principle | Rationale | Trade-off |
|-----------|-----------|-----------|
| Agent Specialization | Better quality, easier debugging | More components |
| Stateless vs Stateful | Use memory only when needed | Complexity |
| Optional Enhancement | Faster default workflow | May miss edge cases |
| Composition over Inheritance | Clear separation, reusability | More setup code |
| Auto-Fix with Limits | Resilience vs infinite loops | May waste tokens |
| Truncation Auto-Fix | Quality vs extra LLM calls | Extra API calls |
| 85% Compaction Threshold | Proactive vs wasteful | Some lost detail |
| Centralized Output | Organization vs migration effort | Requires updates |
| Explicit Configuration | Clarity vs verbosity | Longer config |
| Fail-Fast with Diagnostics | Debuggability vs disk space | Large logs |
| Sound Notifications | Awareness vs potential annoyance | May need muting |
| Production Defaults | Quality vs speed/cost | Higher resource usage |

---

## Related Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and components
- **[COMPACTOR_DESIGN.md](COMPACTOR_DESIGN.md)** - Why compactor is a utility
- **[CONFIGURATION.md](CONFIGURATION.md)** - Complete configuration reference
- **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** - Setup and contributing

---

**Last Updated**: 2025-11-08
**Version**: 1.0.0
