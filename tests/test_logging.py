#!/usr/bin/env python3
"""Test that logging to file works correctly."""

import sys
from pathlib import Path
import json
import time

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from config import AgentConfig
from utils.logger import AgentLogger

def test_logging_to_file():
    """Test that all log events are written to the file."""

    print("=" * 70)
    print("LOGGING TO FILE TEST")
    print("=" * 70)

    # Create test logger
    test_log_dir = Path("output/logs")
    test_log_dir.mkdir(parents=True, exist_ok=True)
    test_log_file = test_log_dir / "test_logging.json"

    # Remove old test log if exists
    if test_log_file.exists():
        test_log_file.unlink()

    logger = AgentLogger(test_log_file)

    print(f"\n1. Created logger, file: {test_log_file}")
    print(f"   File exists: {test_log_file.exists()}")

    # Test 1: Log workflow start
    print("\n2. Testing workflow_start logging...")
    logger.log_workflow_start("Test prompt")
    time.sleep(0.1)

    # Test 2: Log LLM request
    print("\n3. Testing llm_request logging...")
    request_id = logger.log_llm_request(
        agent_name="TestAgent",
        messages=[{"role": "user", "content": "Hello"}],
        system_message="You are a test agent",
        temperature=0.7,
        max_tokens=1000,
        model="test-model"
    )
    time.sleep(0.1)

    # Test 3: Log custom event (llm_waiting)
    print("\n4. Testing custom event logging (llm_waiting)...")
    logger.log_event(
        event_type="llm_waiting",
        agent="TestAgent",
        message="Waiting for LLM response"
    )
    time.sleep(0.1)

    # Test 4: Log LLM response
    print("\n5. Testing llm_response logging...")
    logger.log_llm_response(
        request_id=request_id,
        agent_name="TestAgent",
        response="Test response content",
        tokens_used=50
    )
    time.sleep(0.1)

    # Test 5: Log response received event
    print("\n6. Testing custom event (llm_response_received)...")
    logger.log_event(
        event_type="llm_response_received",
        agent="TestAgent",
        data={"response_length": 100, "has_content": True},
        message="Received LLM response"
    )
    time.sleep(0.1)

    # Test 6: Log action parsing
    print("\n7. Testing action parsing events...")
    logger.log_event(
        event_type="action_parsing_start",
        agent="TestAgent",
        data={"response_length": 500},
        message="Starting action parsing"
    )
    time.sleep(0.1)

    # Test 7: Log tool call
    print("\n8. Testing tool_call logging...")
    call_id = logger.log_tool_call(
        agent_name="TestAgent",
        tool_name="write_file",
        tool_input={"filepath": "test.txt", "content": "test"}
    )
    time.sleep(0.1)

    # Test 8: Log tool result
    print("\n9. Testing tool_result logging...")
    logger.log_tool_result(
        call_id=call_id,
        agent_name="TestAgent",
        tool_name="write_file",
        tool_output={"success": True},
        success=True
    )
    time.sleep(0.1)

    # Test 9: Log action parsing complete
    print("\n10. Testing action_parsing_complete event...")
    logger.log_event(
        event_type="action_parsing_complete",
        agent="TestAgent",
        data={
            "total_actions": 3,
            "bash_commands": 1,
            "files_written": 1,
            "files_read": 1,
            "tool_calls": 0
        },
        message="Parsed and executed 3 actions"
    )
    time.sleep(0.1)

    # Test 10: Log iteration progress
    print("\n11. Testing iteration_progress event...")
    logger.log_event(
        event_type="iteration_progress",
        agent="TestAgent",
        data={
            "iteration": 1,
            "max_iterations": 200,
            "response_preview": "WRITE_FILE: test.txt",
            "has_complete": False
        },
        message="Iteration 1/200"
    )
    time.sleep(0.1)

    # Read and verify log file
    print("\n12. Verifying log file contents...")
    with open(test_log_file, 'r', encoding='utf-8') as f:
        log_data = json.load(f)

    print(f"\n   Session ID: {log_data['session_id']}")
    print(f"   Start time: {log_data['start_time']}")
    print(f"   Total entries: {len(log_data['entries'])}")

    print("\n13. Log entries by type:")
    entry_types = {}
    for entry in log_data['entries']:
        entry_type = entry['type']
        entry_types[entry_type] = entry_types.get(entry_type, 0) + 1

    for entry_type, count in sorted(entry_types.items()):
        print(f"   - {entry_type}: {count}")

    # Verify expected entries
    expected_types = [
        'workflow_start',
        'llm_request',
        'llm_waiting',
        'llm_response',
        'llm_response_received',
        'action_parsing_start',
        'tool_call',
        'tool_result',
        'action_parsing_complete',
        'iteration_progress'
    ]

    print("\n14. Checking for expected entry types...")
    all_found = True
    for expected in expected_types:
        if expected in entry_types:
            print(f"   ✅ {expected}")
        else:
            print(f"   ❌ {expected} - MISSING!")
            all_found = False

    # Print summary
    print("\n" + "=" * 70)
    if all_found and len(log_data['entries']) >= 10:
        print("✅ ALL LOGGING TESTS PASSED!")
        print(f"   File: {test_log_file}")
        print(f"   Total entries: {len(log_data['entries'])}")
    else:
        print("❌ SOME TESTS FAILED!")
        if not all_found:
            print("   - Some entry types are missing")
        if len(log_data['entries']) < 10:
            print(f"   - Expected at least 10 entries, found {len(log_data['entries'])}")
    print("=" * 70)

if __name__ == "__main__":
    test_logging_to_file()
