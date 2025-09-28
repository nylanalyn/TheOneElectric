"""
Shut Up Plugin for PyMotion
Handles the shut up command - makes bot go quiet for a while
"""

import re
import time
import logging
from datetime import datetime

class ShutUpPlugin:
    """Handles shut up command - HIGHEST PRIORITY"""
    
    def __init__(self):
        self.name = "shutup"
        self.priority = 100  # Highest priority
        self.enabled = True
        self.shut_up_until = 0
        self.shut_up_duration = 300  # 5 minutes default
    
    def is_shut_up(self) -> bool:
        """Check if bot should be quiet"""
        return time.time() < self.shut_up_until