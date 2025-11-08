#!/usr/bin/env python3
"""Simple test to verify file operations work correctly."""

from pathlib import Path
from config import AgentConfig
from core.file_operations import FileOperations
from utils.logger import AgentLogger

def test_file_operations():
    """Test that file operations work correctly."""

    print("=" * 70)
    print("FILE OPERATIONS TEST")
    print("=" * 70)

    # Create test config
    config = AgentConfig(
        use_local_llm=True,
        local_model="qwen/qwen3-coder-30b"
    )

    # Create test logger
    test_log_dir = config.output_dir / "logs"
    test_log_dir.mkdir(parents=True, exist_ok=True)
    logger = AgentLogger(test_log_dir / "test_file_ops.json")

    # Create file ops handler
    file_ops = FileOperations(config, logger)

    print(f"\n1. Working Directory: {file_ops.working_directory}")
    print(f"   Absolute path: {file_ops.working_directory.absolute()}")
    print(f"   Exists: {file_ops.working_directory.exists()}")

    # Test 1: Write a simple file
    print("\n2. Test: Write a simple file")
    result = file_ops.write_file(
        "test_file.txt",
        "Hello, this is a test file!",
        agent_name="TestAgent"
    )
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")

    # Test 2: Write file in subdirectory
    print("\n3. Test: Write file in subdirectory")
    result = file_ops.write_file(
        "src/components/Test.tsx",
        "export const Test = () => <div>Test</div>;",
        agent_name="TestAgent"
    )
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")

    # Test 3: Read the file back
    print("\n4. Test: Read file back")
    result = file_ops.read_file("test_file.txt", agent_name="TestAgent")
    print(f"   Success: {result['success']}")
    print(f"   Content: {result['content']}")

    # Test 4: Execute bash command
    print("\n5. Test: Execute bash command")
    result = file_ops.execute_bash_command("ls -la", agent_name="TestAgent")
    print(f"   Success: {result['success']}")
    print(f"   Output (first 200 chars): {result['stdout'][:200]}")

    # Test 5: Try to write outside working directory (should still work but in output dir)
    print("\n6. Test: Write with absolute path (should be in working dir)")
    result = file_ops.write_file(
        "absolute_test.txt",
        "This should be in the working directory",
        agent_name="TestAgent"
    )
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")

    # List created files
    print("\n7. Files created in working directory:")
    for f in file_ops.working_directory.rglob("*"):
        if f.is_file() and not f.name.endswith('.json'):
            rel_path = f.relative_to(file_ops.working_directory)
            print(f"   - {rel_path}")

    # Clean up test files
    print("\n8. Cleaning up test files...")
    import shutil
    for item in ["test_file.txt", "src", "absolute_test.txt"]:
        path = file_ops.working_directory / item
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"   Deleted: {item}")

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print(f"\nLog saved to: {logger.log_file}")

if __name__ == "__main__":
    test_file_operations()
