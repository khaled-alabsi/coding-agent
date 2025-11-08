#!/usr/bin/env python3
"""
Convenient script to run the Azure Code Agent.

Usage:
    python run_agent.py                    # Use prompt.md
    python run_agent.py "Create a todo app"  # Direct prompt
    python run_agent.py --interactive      # Interactive mode
"""

import sys
import argparse
from azure_agent import run, run_interactive


def main():
    parser = argparse.ArgumentParser(
        description="Azure Code Agent - Multi-Agent Coding System"
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="Project prompt (if not provided, uses prompt.md)"
    )

    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )

    parser.add_argument(
        "-f", "--file",
        help="Path to prompt file"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output directory (default: ./output)"
    )

    parser.add_argument(
        "--azure",
        action="store_true",
        help="Use Azure OpenAI instead of local LLM"
    )

    parser.add_argument(
        "--model",
        default="deepseek/deepseek-r1-0528-qwen3-8b",
        help="Local model name (default: deepseek/deepseek-r1-0528-qwen3-8b)"
    )

    parser.add_argument(
        "--max-fixes",
        type=int,
        default=3,
        help="Maximum fix iterations (default: 3)"
    )

    parser.add_argument(
        "--enable-prompt-enhancement",
        action="store_true",
        help="Enable prompt enhancement phase (disabled by default)"
    )

    parser.add_argument(
        "--enable-plan-enhancement",
        action="store_true",
        help="Enable plan enhancement phase (disabled by default)"
    )

    args = parser.parse_args()

    # Interactive mode
    if args.interactive:
        run_interactive()
        return

    # Prepare arguments
    run_args = {
        "use_local_llm": not args.azure,
        "local_model": args.model,
        "skip_prompt_enhancement": not args.enable_prompt_enhancement,
        "skip_plan_enhancement": not args.enable_plan_enhancement,
        "max_fix_iterations": args.max_fixes
    }

    if args.output:
        run_args["output_dir"] = args.output

    if args.file:
        run_args["prompt_file"] = args.file
    elif args.prompt:
        run_args["prompt"] = args.prompt

    # Run
    try:
        results = run(**run_args)

        # Print final summary
        print("\n" + "=" * 70)
        print("DONE!")
        print("=" * 70)
        print(f"Status: {results['final_status']}")
        print(f"Score: {results['validation_result'].get('score', 0)}/100")
        print(f"Output: {results['output_directory']}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
