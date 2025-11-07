#!/usr/bin/env python3
"""
Quick test to verify LM Studio connection
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
            model="local-model",  # Generic name that LM Studio accepts
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
        print("\nYou can now run the agent with:")
        print("  python run_local_llm.py")
        print("\nOr in Python:")
        print("  from azure_agent import run")
        print("  run(use_local_llm=True, local_model='deepseek/deepseek-r1-0528-qwen3-8b')")

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

if __name__ == "__main__":
    success = test_lm_studio_connection()
    sys.exit(0 if success else 1)
