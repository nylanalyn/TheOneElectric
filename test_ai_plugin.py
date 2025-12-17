#!/usr/bin/env python3
"""
Test script for AI plugin
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to Python path so we can import the bot
sys.path.insert(0, str(Path(__file__).parent))

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_ai_plugin():
    """Test AI plugin loading and basic functionality"""
    
    print("Testing AI plugin...")
    
    # Import the bot
    from pymotion_bot import PyMotion
    
    try:
        # Create bot with test config
        bot = PyMotion("test_ai_config.json")
        
        # Check if AI plugin is loaded
        ai_plugin = None
        for plugin in bot.plugins:
            if plugin.name == "ai_response":
                ai_plugin = plugin
                break
        
        if ai_plugin is None:
            print("❌ AI plugin not found in loaded plugins")
            return False
        
        print("✅ AI plugin found and loaded")
        
        # Check plugin configuration
        print(f"AI plugin enabled: {ai_plugin.enabled}")
        print(f"AI plugin priority: {ai_plugin.priority}")
        print(f"AI model: {ai_plugin.config.get('model', 'not configured')}")
        print(f"Max response length: {ai_plugin.config.get('max_response_length', 'not configured')}")
        
        # Test trigger detection
        bot_names = ["PyMotionTest", "pybot", "motion"]
        
        test_messages = [
            "PyMotionTest: what do you think about AI?",
            "pybot, tell me about Python",
            "motion what's your opinion on bots?",
            "Hello everyone!",
            "PyMotionTest shut up"
        ]
        
        print("\nTesting message triggers:")
        for msg in test_messages:
            is_triggered = ai_plugin._is_triggered(msg, bot_names)
            print(f"  '{msg}' -> Triggered: {is_triggered}")
        
        # Test response truncation
        long_response = "This is a very long response that should be truncated to fit within the IRC message length limits. " * 5
        truncated = ai_plugin._truncate_response(long_response)
        print(f"\nResponse truncation test:")
        print(f"  Original length: {len(long_response)}")
        print(f"  Truncated length: {len(truncated)}")
        print(f"  Truncated response: '{truncated}'")
        
        # Test channel filtering
        print(f"\nChannel filtering test:")
        print(f"  Channel '#test' allowed: {ai_plugin._is_allowed_channel('#test')}")
        print(f"  Channel '#private' allowed: {ai_plugin._is_allowed_channel('#private')}")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_plugin())
    sys.exit(0 if success else 1)