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

## Running All Tests

```bash
# Run connection test first
python tests/test_connection.py

# If connection is good, run agent tests
python tests/test_agent.py
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
