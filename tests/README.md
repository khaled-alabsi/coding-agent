# Tests

This directory contains tests for the multi-agent coding system.

## Test Files

### `test_connection.py`
Tests the connection to LM Studio and the LLM client wrapper.

**Usage**:
```bash
python tests/test_connection.py
```

**What it tests**:
- LM Studio server is running and accessible
- LLM client wrapper can communicate with LM Studio
- Basic chat functionality works

### `test_agent.py`
Tests the multi-agent system configuration and initialization.

**Usage**:
```bash
python tests/test_agent.py
```

**What it tests**:
- Coder agent has all required instructions (package.json, README, CSS, etc.)
- All 5 agents are properly initialized
- Logger is properly initialized
- System configuration is correct

### `test_file_operations.py`
Tests the file operations system that agents use to create, read, and modify files.

**Usage**:
```bash
python tests/test_file_operations.py
```

**What it tests**:
- Writing files to the working directory
- Creating files in subdirectories
- Reading files back
- Executing bash commands
- File paths are correctly resolved to working directory
- Logging of tool calls (write_file, read_file, bash)

**When to run**:
- If no files are being created in the output folder
- If you suspect file writing is broken
- To verify the agent can write files correctly

### `test_logging.py`
Tests that logging to the JSON log file works correctly for all event types.

**Usage**:
```bash
python tests/test_logging.py
```

**What it tests**:
- Workflow start/complete logging
- LLM request/response logging
- Custom event logging (llm_waiting, llm_response_received, etc.)
- Action parsing events
- Tool call/result logging
- Iteration progress tracking
- All entries are written to the log file correctly

**When to run**:
- If logs appear incomplete or missing entries
- To verify new logging events are being captured
- When debugging workflow issues

## Running All Tests

```bash
# Run connection test first
python tests/test_connection.py

# If connection is good, run agent tests
python tests/test_agent.py

# Test file operations (if having issues with file creation)
python tests/test_file_operations.py

# Test logging system (if logs appear incomplete)
python tests/test_logging.py
```

## Prerequisites

Before running tests:
1. LM Studio should be running
2. Model (deepseek/deepseek-r1-0528-qwen3-8b) should be loaded
3. Local server should be started on port 1234

## Expected Output

**All tests passing**:
```
✅ ALL TESTS PASSED!
The multi-agent system is ready to use!
```

**Tests failing**:
- Fix LM Studio connection first if `test_connection.py` fails
- Check configuration if `test_agent.py` fails
