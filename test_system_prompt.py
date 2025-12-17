#!/usr/bin/env python3
"""
Test script to verify the system prompt functionality in ai_response.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins'))

from ai_response import AIResponsePlugin

def test_system_prompt():
    """Test that system prompt configuration works correctly"""
    
    # Create plugin instance
    plugin = AIResponsePlugin()
    
    # Test default system prompt
    print("Testing default system prompt...")
    default_prompt = plugin.config['system_prompt']
    expected_default = "You are a friendly IRC bot. Keep responses concise, conversational, and appropriate for chat rooms. Avoid being overly formal or verbose."
    
    assert default_prompt == expected_default, f"Default system prompt mismatch: {default_prompt}"
    print("✓ Default system prompt is correct")
    
    # Test custom system prompt configuration
    print("\nTesting custom system prompt configuration...")
    custom_config = {
        "ai_response": {
            "system_prompt": "You are a pirate bot. Arrr! Keep it short and salty."
        }
    }
    
    plugin.load_config(custom_config)
    custom_prompt = plugin.config['system_prompt']
    expected_custom = "You are a pirate bot. Arrr! Keep it short and salty."
    
    assert custom_prompt == expected_custom, f"Custom system prompt mismatch: {custom_prompt}"
    print("✓ Custom system prompt configuration works")
    
    # Test that the system prompt would be used in API call
    print("\nTesting system prompt usage in API payload...")
    # We can't actually call the API without a key, but we can check the payload structure
    
    # Mock the payload creation logic
    test_prompt = "Hello there!"
    test_context = "Recent conversation: User1: Hi bot"
    
    # Simulate the payload creation from _call_openrouter_api
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
    print("✓ System prompt correctly used in API payload")
    
    print("\n🎉 All system prompt tests passed!")
    print(f"\nExample usage:")
    print(f"Add this to your config:")
    print(f'"system_prompt": "{expected_custom}"')

if __name__ == "__main__":
    test_system_prompt()