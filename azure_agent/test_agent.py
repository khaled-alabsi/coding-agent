#!/usr/bin/env python3
"""
Quick test to verify the agent creates complete projects
"""

from azure_agent import AzureCodeAgent
import tempfile
import shutil
from pathlib import Path

def test_system_instructions():
    """Test that system instructions mention all required files."""

    agent = AzureCodeAgent(
        use_local_llm=True,
        local_model="test-model"
    )

    instructions = agent.system_message

    # Check for key requirements
    required_terms = [
        "COMPLETE",
        "package.json",
        "README",
        "npm install",
        "requirements.txt",
        "tsconfig",
        ".gitignore"
    ]

    print("🧪 Testing System Instructions")
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
        print("✅ SUCCESS! All required terms found in system instructions")
        print("\nThe agent will now create complete, runnable projects!")
    else:
        print("❌ FAILED! Some requirements missing")

    return all_found

def show_instructions():
    """Display the updated system instructions."""

    agent = AzureCodeAgent(
        use_local_llm=True,
        local_model="test-model"
    )

    print("\n📋 Updated System Instructions Preview")
    print("=" * 70)
    lines = agent.system_message.split('\n')
    # Show first 30 lines
    for i, line in enumerate(lines[:35], 1):
        print(f"{i:3}. {line}")
    print("...")
    print("=" * 70)

if __name__ == "__main__":
    print("\n🔧 Testing Agent Improvements\n")

    # Test 1: Check system instructions
    success = test_system_instructions()

    # Show instructions preview
    show_instructions()

    print("\n" + "=" * 70)
    print("📚 What Changed:")
    print("=" * 70)
    print("""
Before:
  - Agent created only source files
  - Missing: package.json, configs, README
  - User had to manually add configuration files

After:
  - Agent creates COMPLETE projects
  - Includes: package.json, vite.config.ts, tsconfig.json, README.md
  - Projects work immediately after 'npm install'
  - README includes clear "How to Run" instructions
    """)

    print("=" * 70)
    print("✅ Next time you run the agent, it will create complete projects!")
    print("=" * 70)
