#!/usr/bin/env python3
"""
Direct import test
"""

import sys
import os

# Add plugins directory to path
sys.path.insert(0, 'plugins')

try:
    from ai_response import AIResponsePlugin
    print("✅ Successfully imported AIResponsePlugin")
    
    plugin = AIResponsePlugin()
    print(f"✅ Created instance: {plugin.name}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()