#!/usr/bin/env python3
"""Test that phase system works correctly - tools are removed after preparation."""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from config import AgentConfig
from tools.runner import ToolRunner

def test_phase_system():
    """Test that tools change based on phase."""

    print("=" * 70)
    print("PHASE SYSTEM TEST")
    print("=" * 70)

    # Create config
    config = AgentConfig(use_local_llm=True)

    # Create mock LLM client (just needs to be an object)
    class MockLLMClient:
        pass

    llm_client = MockLLMClient()

    # Create tool runner
    tool_runner = ToolRunner(llm_client, config)

    print("\n1. PREPARATION Phase - Initial State")
    print(f"   Current phase: {tool_runner._phase}")
    print(f"   Available tools: {list(tool_runner._registry.keys())}")

    # Verify preparation tools are available
    assert tool_runner._phase == "preparation", "Should start in preparation phase"
    assert "ENHANCE_PROMPT" in tool_runner._registry, "ENHANCE_PROMPT should be available"
    assert "CREATE_PLAN" in tool_runner._registry, "CREATE_PLAN should be available"
    assert "ENHANCE_PLAN" in tool_runner._registry, "ENHANCE_PLAN should be available"
    assert len(tool_runner._registry) == 3, "Should have 3 planning tools"
    print("   ✅ All planning tools available")

    print("\n2. Switching to IMPLEMENTATION Phase")
    tool_runner.switch_to_implementation_phase()
    print(f"   Current phase: {tool_runner._phase}")
    print(f"   Available tools: {list(tool_runner._registry.keys())}")

    # Verify planning tools are removed
    assert tool_runner._phase == "implementation", "Should be in implementation phase"
    assert "ENHANCE_PROMPT" not in tool_runner._registry, "ENHANCE_PROMPT should be removed"
    assert "CREATE_PLAN" not in tool_runner._registry, "CREATE_PLAN should be removed"
    assert "ENHANCE_PLAN" not in tool_runner._registry, "ENHANCE_PLAN should be removed"
    assert len(tool_runner._registry) == 0, "Should have no tools in implementation"
    print("   ✅ All planning tools removed")

    print("\n3. Testing tool parsing in IMPLEMENTATION phase")
    # Simulate agent trying to use planning tools during implementation
    fake_response = """
TOOL: ENHANCE_PROMPT
INPUT:
This should not work
"""

    results = tool_runner.run_calls(fake_response)
    print(f"   Parsed calls: {tool_runner.parse_calls(fake_response)}")
    print(f"   Execution results: {results}")

    # Verify the tool call failed because it doesn't exist
    if results:
        assert results[0].get("error"), "Should have an error"
        assert "Unknown tool" in results[0]["error"], "Should say tool is unknown"
        print(f"   ✅ Tool correctly rejected: {results[0]['error']}")
    else:
        print("   ✅ No tool calls executed (tools not recognized)")

    print("\n4. Testing double switch (should be idempotent)")
    tool_runner.switch_to_implementation_phase()
    assert tool_runner._phase == "implementation", "Should still be in implementation"
    assert len(tool_runner._registry) == 0, "Should still have no tools"
    print("   ✅ Double switch handled correctly")

    print("\n" + "=" * 70)
    print("✅ ALL PHASE SYSTEM TESTS PASSED!")
    print("=" * 70)
    print("\nSummary:")
    print("- Planning tools available in PREPARATION phase")
    print("- Planning tools completely removed in IMPLEMENTATION phase")
    print("- Phase switch is irreversible and idempotent")
    print("- Unknown tools are properly rejected")

if __name__ == "__main__":
    test_phase_system()
