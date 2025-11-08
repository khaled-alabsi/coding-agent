# Coder Agent File-Creation Tutorial

Understanding exactly how the Coder generates files—one instruction at a time—helps you debug issues and craft better prompts. This tutorial walks through the execution pipeline using concrete snippets from the codebase.

> References:  
> • `agents/coder.py` (execution loop)  
> • `prompts/coder.md` (system prompt + rules)  
> • `tools/runner.py` (TOOL call handling)  
> • `output/logs/agent_log_*.json` (real transcripts)

---

## 1. Conversation Loop Overview

1. **Seed message** – `CoderAgent.execute_from_prompt(...)` sends the raw prompt plus instructions (lines 74‑109).  
2. **LLM response** – The language model replies with a block containing commands such as:
   ```text
   WRITE_FILE: src/App.tsx
   ```tsx
   // component code
   ```
   READ_FILE: package.json
   ```
3. **Parser + executor** – `_parse_and_execute_actions` scans the response for `BASH`, `WRITE_FILE`, `READ_FILE`, and `TOOL` blocks (lines 187‑272), executes them **immediately**, and logs results.
4. **Feedback** – `_format_action_results` summarizes the execution results (stdout, errors, truncated file contents) and feeds that back to the LLM (lines 274‑319).  
5. **Repeat** – The loop continues until the response contains `COMPLETE` or `max_iterations` is reached.

Files are therefore created incrementally across iterations, not all at once.

---

## 2. Concrete Example (from agent log)

Suppose the LLM responds with:

```
WRITE_FILE: package.json
```json
{ ... }
```

WRITE_FILE: src/main.tsx
```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```
```

**Execution Flow:**
1. Parser detects two `WRITE_FILE` commands.
2. `FileOperations.write_file` writes each file relative to the working directory (`output/…`).  
3. The log records `tool_call` / `tool_result` entries with metadata (file path, content length, success).
4. `_format_action_results` replies to the LLM with:
   ```
   Write File: package.json
   Result: Successfully wrote to output/package.json

   Write File: src/main.tsx
   Result: Successfully wrote to output/src/main.tsx
   ```
5. The LLM uses this feedback to decide the next step—maybe generating CSS, running `npm install`, etc.

---

## 3. Signaling Completion

The Coder loop looks for `COMPLETE` inside the LLM response (lines 119‑134). Once present:
- The agent logs `coder_complete`.
- The Orchestrator stops the implementation phase and hands off to the Result Validator.

**Key points for prompts:**
- The Coder system prompt (prompts/coder.md) insists on running tests (`npm run dev` / `curl`) before emitting `COMPLETE`.
- If the LLM emits `COMPLETE` prematurely, validation may fail; the Orchestrator cycle will try to fix issues up to `max_fix_iterations`.

---

## 4. Where to Control Behavior

| Component | Purpose | File |
|-----------|---------|------|
| System Prompt | “General Requirements”, NO-GO rules, verification checklist | `prompts/coder.md` |
| Execution Loop | Iteration logic, parsing, command dispatch | `agents/coder.py` |
| File/Bash operations | Actual I/O with logging | `core/file_operations.py` |
| Tool invocations | Parsing `TOOL:` blocks and calling enhancers/planners | `tools/runner.py` |
| Logging | `agent_log_*.json`, workflow steps, tool snapshots | `utils/logger.py`, `core/orchestrator.py` |

To “tell the agent to create one file at a time,” you don’t need to change anything—`WRITE_FILE` blocks and a reasonable plan already enforce that behavior. If you want explicit step-by-step instructions, include them in the user prompt or add new checklist items in the system prompt.

---

## 5. Best Practices for Reliable Generation

1. **Detailed File List** – Encourage the planner (or user prompt) to enumerate files with paths and high-level content. The Coder stays more deterministic.
2. **Verification Checklist** – The Coder prompt already enforces checks (e.g., `index.html` must exist). Update this list whenever you hit a repeated failure mode.
3. **Tool Snapshots** – Inspect `output/logs/workflow_steps_*/tools/` to understand tool decisions (prompt enhancement, planning).
4. **Logging** – Use `output/logs/agent_log_*.json` to debug; every `tool_call` includes inputs. If you need more context, add a `log_event` call inside the agent.
5. **Max Iterations & Fix Loop** – Tune `config.max_iterations` and `max_fix_iterations` based on project complexity.

---

## 6. Potential Enhancements

1. **Structured Plan Snapshot** – Save the plan/tool outputs as JSON to give the validator more context.
2. **Action Budgeting** – Track time per iteration (`log_event`) and abort early if productivity drops.
3. **File Checksum Verification** – Before `COMPLETE`, hash key files to detect accidental corruption.
4. **Per-Action Snapshots** – We already snapshot tools; extend the same to `BASH`/`WRITE_FILE` actions for auditing.
5. **LLM Health Check** – Before running validation, send a quick “ping” to the LLM to avoid hanging on a failing model.

---

## 7. Summary Checklist

- The Coder loop is conversational: ask → act → report → repeat.
- `WRITE_FILE` / `BASH` / `READ_FILE` are executed as soon as they appear.
- `COMPLETE` ends the loop; the Result Validator then runs.
- Prompts and configuration (especially `prompts/coder.md`) govern expectations.
- Logs and workflow steps show every action; use them when debugging.
