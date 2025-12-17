#!/usr/bin/env python3
"""
Debug test to see what's in the AI module
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the AI plugin module
import importlib.util
spec = importlib.util.spec_from_file_location("ai_response", "plugins/ai_response.py")
ai_module = importlib.util.module_from_spec(spec)

print("Module attributes:")
for attr in dir(ai_module):
    print(f"  {attr}")

print("\nModule contents:")
for name, obj in vars(ai_module).items():
    if not name.startswith('_'):
        print(f"  {name}: {type(obj)}")