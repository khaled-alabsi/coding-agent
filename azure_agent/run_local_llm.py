#!/usr/bin/env python3
"""
Example script to run the coding agent with local LLM (LM Studio)

Make sure:
1. LM Studio is running at http://localhost:1234
2. You have loaded your model (e.g., deepseek/deepseek-r1-0528-qwen3-8b)
3. The server is started in LM Studio

Usage:
    python run_local_llm.py
"""

from azure_agent import run, AzureCodeAgent
from pathlib import Path

def run_with_local_llm():
    """Run the agent using local LLM through LM Studio."""

    print("=" * 70)
    print("Starting Coding Agent with Local LLM (LM Studio)")
    print("=" * 70)

    # Option 1: Use the run() function
    run(
        use_local_llm=True,                        # Enable local LLM mode
        local_model="deepseek/deepseek-r1-0528-qwen3-8b",  # Your model name
        local_api_base="http://localhost:1234/v1", # LM Studio default URL
        continue_from_history=True,                # Continue from previous session
        inactivity_timeout=300,                    # Stop after 5 min of inactivity
        auto_save_interval=30,                     # Save every 30 seconds
        context_window=8000,                       # Adjust based on your model
        max_tokens=2000,                           # Max response length
        temperature=0.7                            # Creativity level
    )

def run_with_custom_prompt():
    """Run the agent with a custom prompt instead of prompt.md."""

    print("=" * 70)
    print("Running Custom Task with Local LLM")
    print("=" * 70)

    # Create agent
    agent = AzureCodeAgent(
        use_local_llm=True,
        local_model="deepseek/deepseek-r1-0528-qwen3-8b",
        local_api_base="http://localhost:1234/v1",
        max_tokens=2000,
        temperature=0.7
    )

    # Send custom task
    agent.chat("""
    Create a simple Python project with the following:

    1. A file called 'calculator.py' with functions for:
       - add(a, b)
       - subtract(a, b)
       - multiply(a, b)
       - divide(a, b)

    2. A file called 'test_calculator.py' with unit tests for all functions

    3. A README.md explaining how to use the calculator

    Please implement this step by step.
    """, display=True)

def run_with_env_vars():
    """Run using environment variables from .env file."""

    from dotenv import load_dotenv
    import os

    # Load .env file
    load_dotenv()

    print("=" * 70)
    print("Running with environment variables from .env")
    print("=" * 70)

    # Check if LOCAL_LLM_MODEL is set
    if os.getenv("LOCAL_LLM_MODEL"):
        print(f"Using model: {os.getenv('LOCAL_LLM_MODEL')}")
        print(f"API Base: {os.getenv('LOCAL_LLM_API_BASE', 'http://localhost:1234/v1')}")

        # Run with environment variables
        run(
            use_local_llm=True,
            continue_from_history=True,
            inactivity_timeout=300,
            auto_save_interval=30
        )
    else:
        print("⚠️  LOCAL_LLM_MODEL not set in .env file")
        print("Please set LOCAL_LLM_MODEL in your .env file")

if __name__ == "__main__":
    # Choose which method to use:

    # Method 1: Run with explicit parameters
    run_with_local_llm()

    # Method 2: Run with custom prompt
    # run_with_custom_prompt()

    # Method 3: Run with environment variables
    # run_with_env_vars()
