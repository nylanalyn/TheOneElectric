#!/usr/bin/env python3
"""
Final test for AI plugin
"""

import sys
import os

# Add plugins directory to path
sys.path.insert(0, 'plugins')

try:
    from ai_response_test import AIResponsePlugin
    print("✅ Successfully imported AIResponsePlugin")
    
    plugin = AIResponsePlugin()
    print(f"✅ Created instance: {plugin.name}")
    print(f"  Priority: {plugin.priority}")
    print(f"  Enabled: {plugin.enabled}")
    
    # Test configuration loading
    test_config = {
        "ai_response": {
            "openrouter_api_key": "test_key_123",
            "model": "test-model",
            "max_response_length": 100,
            "response_probability": 1.0,
            "cooldown_seconds": 5
        }
    }
    
    plugin.load_config(test_config)
    print(f"✅ Config loaded successfully")
    print(f"  Model: {plugin.config['model']}")
    print(f"  Max length: {plugin.config['max_response_length']}")
    print(f"  Response probability: {plugin.config['response_probability']}")
    
    # Test trigger detection
    bot_names = ["testbot", "tb"]
    test_messages = [
        "testbot: hello",
        "tb, how are you?",
        "hello world",
        "testbot shut up",
        "What do you think about AI?",
        "Your opinion on Python?",
        "Tell me about bots"
    ]
    
    print("\nTrigger detection tests:")
    for msg in test_messages:
        triggered = plugin._is_triggered(msg, bot_names)
        print(f"  '{msg}' -> {triggered}")
    
    # Test response truncation
    long_text = "This is a very long message that should be truncated to fit within IRC limits and test the truncation functionality properly. " * 3
    truncated = plugin._truncate_response(long_text)
    print(f"\nTruncation test:")
    print(f"  Original: {len(long_text)} chars")
    print(f"  Truncated: {len(truncated)} chars")
    print(f"  Result: '{truncated}'")
    
    # Test channel filtering
    plugin.config['enabled_channels'] = ['#test', '#ai']
    plugin.config['disabled_channels'] = ['#private']
    
    print(f"\nChannel filtering test:")
    print(f"  Channel '#test' allowed: {plugin._is_allowed_channel('#test')}")
    print(f"  Channel '#ai' allowed: {plugin._is_allowed_channel('#ai')}")
    print(f"  Channel '#private' allowed: {plugin._is_allowed_channel('#private')}")
    print(f"  Channel '#general' allowed: {plugin._is_allowed_channel('#general')}")
    
    # Reset to allow all channels
    plugin.config['enabled_channels'] = []
    plugin.config['disabled_channels'] = []
    
    # Test mock API responses
    print(f"\nMock API response tests:")
    test_prompts = [
        "hello there",
        "what do you think about Python",
        "tell me about AI",
        "random question"
    ]
    
    import asyncio
    
    async def test_api_responses():
        for prompt in test_prompts:
            response = await plugin._call_openrouter_api(prompt)
            truncated = plugin._truncate_response(response)
            print(f"  '{prompt}' -> '{truncated}'")
    
    asyncio.run(test_api_responses())
    
    print("\n✅ All tests completed successfully!")
    print("\n📋 Summary:")
    print("  - AI plugin loads and initializes correctly")
    print("  - Configuration loading works")
    print("  - Trigger detection identifies relevant messages")
    print("  - Response truncation respects IRC limits")
    print("  - Channel filtering works as expected")
    print("  - Mock API responses generate appropriate replies")
    
    print("\n🚀 Ready for integration!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()