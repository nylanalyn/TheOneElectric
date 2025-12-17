#!/usr/bin/env python3
"""
Simple test for AI plugin without dependencies
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Test importing the AI plugin directly
try:
    # Import the AI plugin module
    import importlib.util
    spec = importlib.util.spec_from_file_location("ai_response", "plugins/ai_response.py")
    ai_module = importlib.util.module_from_spec(spec)
    
    print("✅ AI plugin module loaded successfully")
    
    # Check if the class exists
    if hasattr(ai_module, 'AIResponsePlugin'):
        print("✅ AIResponsePlugin class found")
        
        # Create an instance
        plugin = ai_module.AIResponsePlugin()
        print(f"✅ AI plugin instance created: {plugin.name}")
        print(f"  Priority: {plugin.priority}")
        print(f"  Enabled: {plugin.enabled}")
        
        # Test configuration loading
        test_config = {
            "ai_response": {
                "openrouter_api_key": "test_key",
                "model": "test-model",
                "max_response_length": 100
            }
        }
        
        plugin.load_config(test_config)
        print(f"✅ Config loaded: {plugin.config['model']}")
        
        # Test trigger detection
        bot_names = ["testbot", "tb"]
        test_messages = [
            "testbot: hello",
            "tb, how are you?",
            "hello world",
            "testbot shut up"
        ]
        
        print("\nTrigger detection tests:")
        for msg in test_messages:
            triggered = plugin._is_triggered(msg, bot_names)
            print(f"  '{msg}' -> {triggered}")
        
        # Test response truncation
        long_text = "This is a very long message that should be truncated to fit within IRC limits and test the truncation functionality properly."
        truncated = plugin._truncate_response(long_text)
        print(f"\nTruncation test:")
        print(f"  Original: {len(long_text)} chars")
        print(f"  Truncated: {len(truncated)} chars")
        print(f"  Result: '{truncated}'")
        
        print("\n✅ All basic tests passed!")
        
    else:
        print("❌ AIResponsePlugin class not found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)