#!/usr/bin/env python3
"""
Test to verify the multi-agent system configuration
"""

from config import AgentConfig
from core.orchestrator import AgentOrchestrator
from agents import CoderAgent


def test_coder_system_instructions():
    """Test that coder agent system instructions mention all required files."""

    config = AgentConfig(
        use_local_llm=True,
        local_model="test-model"
    )

    # Create orchestrator to get the coder agent
    orchestrator = AgentOrchestrator(config)

    instructions = orchestrator.coder.system_prompt

    # Check for key requirements
    required_terms = [
        "COMPLETE",
        "package.json",
        "README",
        "npm install",
        "requirements.txt",
        "tsconfig",
        ".gitignore",
        "CSS",
        "STYLING"
    ]

    print("🧪 Testing Multi-Agent System Configuration")
    print("=" * 70)

    all_found = True
    for term in required_terms:
        found = term in instructions
        status = "✅" if found else "❌"
        print(f"{status} '{term}' mentioned: {found}")
        if not found:
            all_found = False

    print("=" * 70)
    if all_found:
        print("✅ SUCCESS! All required terms found in coder instructions")
        print("\nThe multi-agent system is properly configured!")
    else:
        print("❌ FAILED! Some requirements missing")

    return all_found


def test_agents_initialized():
    """Test that all 5 agents are properly initialized."""

    config = AgentConfig(
        use_local_llm=True,
        local_model="test-model"
    )

    orchestrator = AgentOrchestrator(config)

    print("\n🧪 Testing Agent Initialization")
    print("=" * 70)

    agents = [
        ("Prompt Enhancer", orchestrator.prompt_enhancer),
        ("Planner", orchestrator.planner),
        ("Plan Enhancer", orchestrator.plan_enhancer),
        ("Coder", orchestrator.coder),
        ("Validator", orchestrator.validator)
    ]

    all_initialized = True
    for name, agent in agents:
        if agent is not None:
            print(f"✅ {name} - Initialized")
        else:
            print(f"❌ {name} - NOT initialized")
            all_initialized = False

    print("=" * 70)
    if all_initialized:
        print("✅ SUCCESS! All 5 agents initialized!")
    else:
        print("❌ FAILED! Some agents missing")

    return all_initialized


def test_logger_initialized():
    """Test that logger is initialized."""

    config = AgentConfig(
        use_local_llm=True,
        local_model="test-model"
    )

    orchestrator = AgentOrchestrator(config)

    print("\n🧪 Testing Logger Initialization")
    print("=" * 70)

    if orchestrator.logger is not None:
        print(f"✅ Logger initialized")
        print(f"   Log file: {orchestrator.logger.log_file}")
        print(f"   Session ID: {orchestrator.logger.session_id}")
        return True
    else:
        print("❌ Logger NOT initialized")
        return False


if __name__ == "__main__":
    print("\n🔧 Testing Multi-Agent System\n")

    # Test 1: Coder agent instructions
    test1 = test_coder_system_instructions()

    # Test 2: All agents initialized
    test2 = test_agents_initialized()

    # Test 3: Logger initialized
    test3 = test_logger_initialized()

    print("\n" + "=" * 70)
    print("📊 RESULTS:")
    print("=" * 70)
    print(f"Coder Instructions: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Agents Initialized: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"Logger Initialized: {'✅ PASS' if test3 else '❌ FAIL'}")
    print("=" * 70)

    if test1 and test2 and test3:
        print("✅ ALL TESTS PASSED!")
        print("\nThe multi-agent system is ready to use!")
    else:
        print("❌ SOME TESTS FAILED")

    print("=" * 70)
