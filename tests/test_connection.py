#!/usr/bin/env python3
"""
Test LM Studio connection and multi-agent system integration
"""

from openai import OpenAI
import sys


def test_lm_studio_connection():
    """Test if LM Studio is responding."""

    print("=" * 70)
    print("Testing LM Studio Connection")
    print("=" * 70)

    try:
        print("\n1️⃣ Creating client...")
        client = OpenAI(
            api_key="lm-studio",
            base_url="http://localhost:1234/v1"
        )
        print("   ✅ Client created")

        print("\n2️⃣ Sending test message...")
        print("   (This might take 10-30 seconds depending on your model)")

        response = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "user", "content": "Hello! Reply with just 'Hi' please."}
            ],
            max_tokens=50,
            temperature=0.7
        )

        print("   ✅ Response received!")
        print(f"\n📩 Response: {response.choices[0].message.content}")

        print("\n" + "=" * 70)
        print("✅ SUCCESS! LM Studio is working correctly!")
        print("=" * 70)

        return True

    except ConnectionError as e:
        print("\n❌ Connection Error!")
        print(f"   {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Open LM Studio")
        print("   2. Load your model (deepseek/deepseek-r1-0528-qwen3-8b)")
        print("   3. Go to 'Local Server' tab")
        print("   4. Click 'Start Server'")
        print("   5. Make sure it shows: 'Server running at http://localhost:1234'")
        return False

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}")
        print(f"   {e}")
        print("\n🔧 Possible issues:")
        print("   - LM Studio server not started")
        print("   - Model not loaded in LM Studio")
        print("   - Port 1234 is used by another application")
        print("   - Firewall blocking localhost connection")
        return False


def test_llm_client():
    """Test the LLM client wrapper."""

    print("\n" + "=" * 70)
    print("Testing LLM Client Wrapper")
    print("=" * 70)

    try:
        from config import AgentConfig
        from core.llm_client import LLMClient

        print("\n1️⃣ Creating config...")
        config = AgentConfig(
            use_local_llm=True,
            local_model="local-model",
            local_api_base="http://localhost:1234/v1"
        )
        print("   ✅ Config created")

        print("\n2️⃣ Creating LLM client...")
        client = LLMClient(config)
        print("   ✅ Client created")

        print("\n3️⃣ Testing chat...")
        response = client.chat(
            messages=[{"role": "user", "content": "Say 'test successful'"}],
            agent_name="test"
        )
        print(f"   ✅ Response: {response[:100]}")

        print("\n" + "=" * 70)
        print("✅ LLM Client wrapper working!")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}")
        print(f"   {e}")
        return False


if __name__ == "__main__":
    print("\n🔧 Connection Tests\n")

    # Test 1: Raw LM Studio connection
    test1 = test_lm_studio_connection()

    # Test 2: LLM Client wrapper (only if test1 passed)
    test2 = False
    if test1:
        test2 = test_llm_client()

    print("\n" + "=" * 70)
    print("📊 RESULTS:")
    print("=" * 70)
    print(f"LM Studio Connection: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"LLM Client Wrapper:   {'✅ PASS' if test2 else '❌ FAIL (skipped)' if not test1 else '❌ FAIL'}")
    print("=" * 70)

    if test1 and test2:
        print("✅ ALL TESTS PASSED!")
        print("\nYou can now run the multi-agent system:")
        print("  • Open main.ipynb in Jupyter")
        print("  • Or run: python run_agent.py")
    else:
        print("❌ SOME TESTS FAILED")
        if not test1:
            print("\n⚠️  Fix LM Studio connection first!")

    print("=" * 70)

    sys.exit(0 if (test1 and test2) else 1)
