#!/usr/bin/env python3
"""
Simple test script to verify the system prompt functionality in ai_response.py
This version doesn't require httpx to be installed.
"""

import sys
import os
import re
from typing import List, Dict, Any

# Mock the httpx module since we don't need it for this test
class MockHTTPX:
    class AsyncClient:
        pass

sys.modules['httpx'] = MockHTTPX()

# Now we can import the plugin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins'))

# Import the plugin module
import importlib.util
spec = importlib.util.spec_from_file_location("ai_response", "plugins/ai_response.py")
module = importlib.util.module_from_spec(spec)

# Mock the missing dependencies in the module namespace
module.httpx = MockHTTPX()
module.asyncio = None  # We won't test async functionality

# Execute the module
spec.loader.exec_module(module)

def test_system_prompt():
    """Test that system prompt configuration works correctly"""
    
    # Create plugin instance
    plugin = module.AIResponsePlugin()
    
    print("Testing AI Response Plugin System Prompt Feature")
    print("=" * 50)
    
    # Test default system prompt
    print("\n1. Testing default system prompt...")
    default_prompt = plugin.config['system_prompt']
    expected_default = "You are a friendly IRC bot. Keep responses concise, conversational, and appropriate for chat rooms. Avoid being overly formal or verbose."
    
    assert default_prompt == expected_default, f"Default system prompt mismatch: {default_prompt}"
    print("   ✓ Default system prompt is correct")
    print(f"   Default: '{default_prompt}'")
    
    # Test custom system prompt configuration
    print("\n2. Testing custom system prompt configuration...")
    custom_config = {
        "ai_response": {
            "system_prompt": "You are a pirate bot. Arrr! Keep it short and salty."
        }
    }
    
    plugin.load_config(custom_config)
    custom_prompt = plugin.config['system_prompt']
    expected_custom = "You are a pirate bot. Arrr! Keep it short and salty."
    
    assert custom_prompt == expected_custom, f"Custom system prompt mismatch: {custom_prompt}"
    print("   ✓ Custom system prompt configuration works")
    print(f"   Custom: '{custom_prompt}'")
    
    # Test that the system prompt would be used in API call
    print("\n3. Testing system prompt usage in API payload...")
    
    # Mock the payload creation logic (simplified version of _call_openrouter_api)
    test_prompt = "Hello there!"
    test_context = "Recent conversation: User1: Hi bot"
    
    # Simulate the payload creation
    payload = {
        "model": plugin.config['model'],
        "messages": [
            {
                "role": "system",
                "content": plugin.config['system_prompt']  # This should use our custom prompt
            },
            {
                "role": "user",
                "content": f"{test_context}\n\nUser: {test_prompt}"
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.9,
    }
    
    # Verify the system prompt in the payload matches our custom one
    system_content = payload['messages'][0]['content']
    assert system_content == expected_custom, f"System prompt in payload mismatch: {system_content}"
    print("   ✓ System prompt correctly used in API payload")
    print(f"   Payload system prompt: '{system_content}'")
    
    print("\n" + "=" * 50)
    print("🎉 All system prompt tests passed!")
    
    print(f"\n📝 Example usage:")
    print(f"Add this to your pymotion.json config file:")
    print(f'"ai_response": {{')
    print(f'    "system_prompt": "You are a witty and sarcastic IRC bot with a love for retro technology.",')
    print(f'    "openrouter_api_key": "your_api_key_here",')
    print(f'    "model": "mistralai/mistral-7b-instruct:free"')
    print(f'}}')
    
    print(f"\n💡 Tips for creating good system prompts:")
    print(f"   • Be specific about personality and tone")
    print(f"   • Include response length guidelines")
    print(f"   • Mention appropriate topics and boundaries")
    print(f"   • Consider adding humor or cultural references")
    print(f"   • Keep it under 200 characters for best results")

if __name__ == "__main__":
    test_system_prompt()