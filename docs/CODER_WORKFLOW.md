# Coder Agent Workflow

**Goal:** Explain exactly how the Coder agent plans, iterates, and creates files.

Source references:  
- `agents/coder.py`  
- `tools/runner.py`  
- `prompts/coder.md`

---

## 1. High-Level Flow

1. **Input** – The Orchestrator hands the raw user prompt to the Coder.
2. **Preparation Phase** – The Coder may call tools (`ENHANCE_PROMPT`, `CREATE_PLAN`, `ENHANCE_PLAN`) to clarify requirements before touching files.
3. **Implementation Loop** – The Coder repeatedly:
   - Sends a message to the LLM describing the current plan or progress.
   - Parses the LLM’s response for actions.
   - Executes those actions (write files, run commands, read files).
   - Feeds the results back into the conversation.
4. **Completion** – When the LLM response contains `COMPLETE`, the loop ends and validation begins.

This means files are *not* created in a single response. Instead, each loop iteration adds or modifies files based on the latest instructions.

---

## 2. Detailed Timeline

| Step | Description | Code |
|------|-------------|------|
| 1 | `execute_from_prompt` starts the conversation and seeds the first message (raw prompt + instructions). | `agents/coder.py:74-109` |
| 2 | The Coder enters a loop up to `config.max_iterations`. | `agents/coder.py:110-152` |
| 3 | For each LLM response, `_parse_and_execute_actions` looks for directives. | `agents/coder.py:187-272` |
| 4 | Actions are executed immediately: |  |
| • `WRITE_FILE: path …` → `FileOperations.write_file` | `core/file_operations.py` |
| • `BASH: command` → `FileOperations.execute_bash_command` |  |
| • `READ_FILE: path` → `FileOperations.read_file` (content fed back to LLM) |  |
| • `TOOL: ...` → `ToolRunner.run_calls` (see §3) | `tools/runner.py` |
| 5 | Execution results are summarized and sent back to the LLM via `self.chat`. | `agents/coder.py:274-319` |
| 6 | Loop repeats until `COMPLETE` or max iterations. | `agents/coder.py:120-152` |

---

## 3. Tool Usage & Phases

Tools are *only* commands inside the LLM response. The Coder does not decide on its own— it simply parses `TOOL:` sections and dispatches them.

- **Preparation Tools** (available throughout):
  - `ENHANCE_PROMPT`
  - `CREATE_PLAN`
  - `ENHANCE_PLAN`
- **Implementation Tools**:
  - None. During implementation, the Coder relies on `BASH/WRITE_FILE/READ_FILE`.

`ToolRunner` handles:
1. Parsing `TOOL: NAME` blocks.
2. Calling the correct helper (from `tools/prompt_tools.py`).
3. Logging tool input/output and writing snapshots to `workflow_steps…/tools`.

Even after switching to “implementation phase” (see `ToolRunner.switch_to_implementation_phase`), these tools remain recognized so any late tool call still works. If a tool is missing or spelled incorrectly, the Coder logs an error (`Unknown tool: …`).

---

## 4. File Creation Mechanics

1. LLM outputs:
   ```
   WRITE_FILE: personal-website/src/components/Hero.tsx
   ```tsx
   // component code…
   ```
   ```
2. Coder parses the block and calls `write_file`.
3. `FileOperations.write_file` resolves the relative path *under the working directory* (usually `output/…`). No “output/” prefix is required in the LLM response.
4. Success/failure is logged:
   - Agent log entry (`tool_call`/`tool_result` with `tool_name = write_file`).
   - Terminal output shows “📝 Writing file…” and the result message.

**Key point:** Files are written incrementally per WRITE_FILE block. Multiple WRITE_FILE blocks in one response are executed in sequence before the Coder asks the LLM for the next step.

---

## 5. Logging & Artifacts

- **Agent Log (`output/logs/agent_log_*.json`)**:
  - `llm_request / llm_response`
  - `tool_call / tool_result` (tools + bash/write_file/read_file)
  - Optional `log_event` entries (iteration progress).
- **Workflow Steps (`output/logs/workflow_steps_*/`)**:
  - `0_user_prompt.md`, `1_implementation_result.md`, `2_validation_result.json`, etc.
  - `tools/` directory with per-tool INPUT/OUTPUT snapshots.
- **Generated Code**:
  - Written directly under `output/…` (or custom `output_dir` if provided).

---

## 6. Summary

- The Coder is a conversational agent with an execution loop.
- It does **not** dump the entire project at once; it iterates, parses actions, executes them, and feeds back results.
- Tools are invoked by the LLM response itself; ToolRunner executes them and the logs record every call.
- Files are created by `WRITE_FILE` blocks (or generated via shell commands) under the working directory.

For a quick mental model: think of the Coder as an “LLM front-end” for the shell + filesystem, running a loop of “ask → act → report → ask again” until completion.
