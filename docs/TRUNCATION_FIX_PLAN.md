# Dynamic Truncation Detection & Fix Plan

**Goal**: Automatically detect when LLM responses are truncated and fix them in real-time

---

## PROBLEM ANALYSIS

### Current Issue
1. **Plan Enhancer** response was truncated at 35,500 tokens
2. File saved incomplete: `3_plan_enhanced.md` ends mid-sentence
3. No detection or warning - fails silently
4. User only discovers when reading output files

### Root Causes
- `max_tokens` too small for task complexity
- No truncation detection in response pipeline
- No automatic retry/continuation mechanism
- No warnings logged or displayed

---

## DETECTION STRATEGY

### Method 1: Token Usage Analysis (BEST)
```python
# After each LLM call, check actual usage
response = client.chat.completions.create(...)

if hasattr(response, 'usage'):
    used_tokens = response.usage.completion_tokens
    max_tokens = config.max_tokens

    # Detect truncation
    if used_tokens >= max_tokens * 0.95:  # 95% threshold
        # TRUNCATED!
        truncation_detected = True
```

**Pros**: Accurate, uses real token counts
**Cons**: Requires API support (OpenAI, Azure)

### Method 2: Response Ending Analysis (FALLBACK)
```python
# Check if response ends naturally
response_text = response.choices[0].message.content

truncation_indicators = [
    # Incomplete sentences
    not response_text.strip().endswith(('.', '!', '?', '```', '}')),

    # Expected markers missing
    "COMPLETE" not in response_text,  # For Coder

    # Mid-word cutoff
    response_text[-1].isalnum() and response_text[-2].isalnum()
]

if any(truncation_indicators):
    truncation_detected = True
```

**Pros**: Works without token usage API
**Cons**: Less accurate, false positives possible

### Method 3: Estimated vs Actual (HYBRID)
```python
# Estimate expected response size
estimated_tokens = estimate_task_size(task)

# Compare with actual
if used_tokens >= max_tokens * 0.95 and estimated_tokens > used_tokens:
    truncation_detected = True
```

---

## FIX STRATEGIES

### Strategy 1: Continuation Request (QUICK FIX)
**When**: Truncation detected, context allows
**How**: Ask LLM to continue from where it stopped

```python
if truncation_detected:
    continuation_prompt = "Continue from where you left off. Complete the remaining content."

    continuation = llm_client.chat(
        messages=messages + [continuation_prompt],
        max_tokens=max_tokens  # Same limit
    )

    # Merge responses
    full_response = original_response + continuation
```

**Pros**: Fast, preserves context
**Cons**: May truncate again, context grows

### Strategy 2: Adaptive Max Tokens (MEDIUM FIX)
**When**: Truncation detected, can increase limit
**How**: Increase max_tokens and retry

```python
if truncation_detected:
    # Calculate needed tokens
    estimated_needed = used_tokens * 1.5  # 50% buffer

    # Increase max_tokens
    new_max_tokens = min(estimated_needed, 100000)  # Cap at 100k

    print(f"⚠️  Truncation detected! Retrying with {new_max_tokens} tokens...")

    # Retry with higher limit
    response = llm_client.chat(
        messages=messages,
        max_tokens=new_max_tokens
    )
```

**Pros**: Prevents future truncation
**Cons**: Requires retry, slower

### Strategy 3: Task Decomposition (COMPLEX FIX)
**When**: Response too large even with max limit
**How**: Split task into smaller chunks

```python
if truncation_detected and used_tokens >= 100000:
    # Task too large, decompose
    print("⚠️  Task too large. Splitting into chunks...")

    # For Plan Enhancer: split by implementation phases
    chunks = split_plan_by_phases(plan)

    enhanced_chunks = []
    for chunk in chunks:
        result = enhance_chunk(chunk)
        enhanced_chunks.append(result)

    # Merge results
    full_response = merge_chunks(enhanced_chunks)
```

**Pros**: Handles very large tasks
**Cons**: Complex, may lose coherence

### Strategy 4: Streaming with Size Limit (ADVANCED)
**When**: Want to prevent truncation upfront
**How**: Stream response and stop at natural boundaries

```python
def stream_with_limit(prompt, max_chars=200000):
    accumulated = ""

    for chunk in llm_client.stream_chat(prompt):
        accumulated += chunk

        # Check if approaching limit
        if len(accumulated) >= max_chars * 0.9:
            # Find natural stopping point
            if is_natural_boundary(accumulated):
                break

    return accumulated
```

**Pros**: Prevents truncation, stops naturally
**Cons**: Requires streaming support

---

## IMPLEMENTATION PLAN

### Phase 1: Detection Layer (Priority 1 - QUICK WIN)

**Where**: `core/llm_client.py`

**Changes**:
```python
class LLMClient:
    def chat(self, ...):
        response = self.client.chat.completions.create(...)
        response_content = response.choices[0].message.content

        # NEW: Detect truncation
        truncation_info = self._detect_truncation(
            response,
            max_tokens,
            agent_name
        )

        if truncation_info['truncated']:
            self._handle_truncation(truncation_info, ...)

        return response_content

    def _detect_truncation(self, response, max_tokens, agent_name):
        """Detect if response was truncated."""
        truncated = False
        used_tokens = None

        # Method 1: Token usage (if available)
        if hasattr(response, 'usage'):
            used_tokens = response.usage.completion_tokens
            if used_tokens >= max_tokens * 0.95:
                truncated = True

        # Method 2: Response ending analysis (fallback)
        response_text = response.choices[0].message.content
        if not truncated:
            truncated = self._check_response_ending(response_text, agent_name)

        return {
            'truncated': truncated,
            'used_tokens': used_tokens,
            'max_tokens': max_tokens,
            'response_text': response_text,
            'agent_name': agent_name
        }

    def _check_response_ending(self, text, agent_name):
        """Check if response ends naturally."""
        text = text.strip()

        # Agent-specific completion markers
        completion_markers = {
            'Coder': ['COMPLETE'],
            'Plan Enhancer': ['```'],  # Should end with code block
            'Planner': ['IMPLEMENTATION PHASE']
        }

        # Check for expected markers
        expected = completion_markers.get(agent_name, [])
        if expected and not any(marker in text for marker in expected):
            return True

        # Check sentence ending
        if not text.endswith(('.', '!', '?', '```', '}')):
            return True

        return False
```

### Phase 2: Auto-Fix with Continuation (Priority 2 - MEDIUM)

**Where**: `core/llm_client.py`

**Changes**:
```python
class LLMClient:
    def _handle_truncation(self, truncation_info, messages, system_message, temperature, agent_name):
        """Handle truncation by requesting continuation."""
        print(f"\n⚠️  TRUNCATION DETECTED!")
        print(f"   Agent: {agent_name}")
        print(f"   Used: {truncation_info['used_tokens']:,} / {truncation_info['max_tokens']:,} tokens")
        print(f"   Attempting automatic fix...")

        # Strategy 1: Try continuation first
        full_response = self._try_continuation(
            truncation_info, messages, system_message, temperature, agent_name
        )

        if full_response:
            print(f"   ✅ Fixed via continuation")
            return full_response

        # Strategy 2: Retry with increased max_tokens
        full_response = self._try_increase_tokens(
            truncation_info, messages, system_message, temperature, agent_name
        )

        if full_response:
            print(f"   ✅ Fixed via increased max_tokens")
            return full_response

        # Strategy 3: Give up, return truncated
        print(f"   ❌ Could not fix truncation automatically")
        return truncation_info['response_text']

    def _try_continuation(self, truncation_info, messages, system_message, temperature, agent_name, max_attempts=3):
        """Try to get continuation of truncated response."""
        full_response = truncation_info['response_text']

        for attempt in range(max_attempts):
            # Build continuation messages
            continuation_messages = messages.copy()
            continuation_messages.append({
                "role": "assistant",
                "content": full_response
            })
            continuation_messages.append({
                "role": "user",
                "content": "Continue from where you left off. Complete the remaining content."
            })

            # Request continuation
            continuation_response = self.client.chat.completions.create(
                model=self.model_name,
                messages=continuation_messages,
                temperature=temperature,
                max_tokens=self.config.max_tokens
            )

            continuation_text = continuation_response.choices[0].message.content
            full_response += "\n" + continuation_text

            # Check if still truncated
            if hasattr(continuation_response, 'usage'):
                used = continuation_response.usage.completion_tokens
                if used < self.config.max_tokens * 0.95:
                    # Success!
                    return full_response
            else:
                # No usage info, assume success if looks complete
                if self._looks_complete(continuation_text, agent_name):
                    return full_response

        # Failed after max attempts
        return None

    def _try_increase_tokens(self, truncation_info, messages, system_message, temperature, agent_name):
        """Retry with increased max_tokens."""
        current_max = truncation_info['max_tokens']
        new_max = min(current_max * 2, 100000)  # Double, cap at 100k

        if new_max == current_max:
            return None  # Already at max

        print(f"   🔄 Retrying with max_tokens={new_max:,}...")

        retry_response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=new_max
        )

        retry_text = retry_response.choices[0].message.content

        # Check if still truncated
        truncation_check = self._detect_truncation(retry_response, new_max, agent_name)
        if not truncation_check['truncated']:
            return retry_text

        # Still truncated, give up
        return None

    def _looks_complete(self, text, agent_name):
        """Check if response looks complete."""
        return not self._check_response_ending(text, agent_name)
```

### Phase 3: Logging & Monitoring (Priority 3 - LOW)

**Where**: `utils/logger.py`

**Changes**:
```python
class AgentLogger:
    def log_truncation_detected(self, agent_name, used_tokens, max_tokens, fix_strategy):
        """Log truncation detection and fix attempt."""
        self._log_entry({
            "type": "truncation_detected",
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "used_tokens": used_tokens,
            "max_tokens": max_tokens,
            "utilization": f"{(used_tokens/max_tokens)*100:.1f}%",
            "fix_strategy": fix_strategy
        })

    def log_truncation_fixed(self, agent_name, strategy, attempts, final_tokens):
        """Log successful truncation fix."""
        self._log_entry({
            "type": "truncation_fixed",
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "fix_strategy": strategy,
            "attempts": attempts,
            "final_tokens": final_tokens
        })
```

---

## CONFIGURATION

### New Settings (add to `config/settings.py`)

```python
@dataclass
class AgentConfig:
    # ... existing fields ...

    # Truncation detection & fix
    truncation_detection_enabled: bool = True
    truncation_threshold: float = 0.95  # 95% of max_tokens
    auto_fix_truncation: bool = True
    continuation_max_attempts: int = 3
    adaptive_max_tokens: bool = True
    max_tokens_limit: int = 100000  # Hard limit for auto-increase
```

---

## TESTING PLAN

### Test Case 1: Plan Enhancer Truncation
```python
# Trigger truncation with complex plan
result = run(
    prompt="Create a massive portfolio with 50+ components",
    max_tokens=10000,  # Intentionally low
    truncation_detection_enabled=True,
    auto_fix_truncation=True
)

# Expected: Auto-fix via continuation or retry
assert "3_plan_enhanced.md" ends naturally
assert no truncation in output
```

### Test Case 2: Coder Truncation
```python
# Trigger truncation with large codebase
result = run(
    prompt="Create complete e-commerce platform",
    max_tokens=20000,
    auto_fix_truncation=True
)

# Expected: Continuation requests or adaptive max_tokens
assert all files complete
assert "COMPLETE" in final response
```

### Test Case 3: Multiple Continuations
```python
# Test continuation chaining
result = run(
    prompt="Extremely detailed plan...",
    max_tokens=5000,
    continuation_max_attempts=5
)

# Expected: Multiple continuations merged
assert response_length > 5000 * 4  # At least 4 continuations
```

---

## ROLLOUT PLAN

### Step 1: Detection Only (Week 1)
- Implement detection in `llm_client.py`
- Log warnings, no fixes
- Monitor for false positives
- Tune detection thresholds

### Step 2: Manual Fix (Week 2)
- Add `--auto-fix-truncation` flag
- Implement continuation strategy
- Test on known truncation cases
- Collect metrics

### Step 3: Auto-Fix Default (Week 3)
- Enable auto-fix by default
- Add adaptive max_tokens
- Monitor performance impact
- Fine-tune strategies

### Step 4: Advanced Features (Week 4)
- Task decomposition for huge tasks
- Streaming with size limits
- Predictive max_tokens estimation
- Dashboard for truncation stats

---

## METRICS TO TRACK

```python
class TruncationMetrics:
    total_requests: int = 0
    truncated_requests: int = 0
    auto_fixed: int = 0
    fix_failures: int = 0

    avg_continuation_attempts: float = 0
    avg_tokens_saved: int = 0  # By not retrying from scratch

    by_agent: Dict[str, AgentMetrics] = {}
```

**Dashboard View**:
```
Truncation Stats (Last 30 days)
─────────────────────────────────────
Total Requests:         1,234
Truncated:             45 (3.6%)
Auto-Fixed:            42 (93.3%)
Failed:                3 (6.7%)

By Agent:
  Plan Enhancer:       15 truncations, 14 fixed
  Coder:              20 truncations, 20 fixed
  Planner:            10 truncations, 8 fixed
```

---

## FALLBACK STRATEGY

If auto-fix fails, provide clear guidance:

```python
if fix_failed:
    print(f"""
    ⚠️  TRUNCATION DETECTED - AUTO-FIX FAILED

    Agent: {agent_name}
    Used: {used_tokens:,} / {max_tokens:,} tokens (95%+)

    Manual Fix Options:
    1. Increase max_tokens in config:
       max_tokens: {used_tokens * 1.5:.0f}  # Recommended

    2. Simplify the prompt:
       - Break into smaller tasks
       - Remove optional requirements

    3. Skip enhancement phases:
       --skip-prompt-enhancement --skip-plan-enhancement

    4. Review output manually:
       {output_file}
    """)
```

---

## ESTIMATED EFFORT

| Phase | Effort | Risk | Value |
|-------|--------|------|-------|
| Detection Layer | 2-3 hours | Low | High |
| Continuation Fix | 3-4 hours | Medium | High |
| Adaptive Tokens | 2 hours | Low | Medium |
| Logging & Monitoring | 1-2 hours | Low | Medium |
| Testing | 2-3 hours | Low | High |
| **TOTAL** | **10-14 hours** | **Low-Medium** | **High** |

---

## BENEFITS

1. **User Experience**: No more silent failures
2. **Reliability**: Auto-recovery from truncation
3. **Debugging**: Clear logs and metrics
4. **Cost Savings**: Continuation vs full retry saves tokens
5. **Insight**: Metrics show which agents/tasks need tuning

---

## NEXT STEPS

1. ✅ Review and approve plan
2. ⬜ Implement Phase 1 (Detection)
3. ⬜ Test on existing truncation case
4. ⬜ Implement Phase 2 (Auto-fix)
5. ⬜ Deploy and monitor
