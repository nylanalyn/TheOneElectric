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
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Handle messages and check for shut up commands"""
        # Check if someone told bot to shut up
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        
        for bot_name in bot_names:
            if re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\b(shut up|stfu|be quiet|shush)\b', message):
                self.shut_up_until = time.time() + self.shut_up_duration
                await bot.privmsg(channel, f"*sulks* Fine, I'll be quiet for {self.shut_up_duration // 60} minutes...")
                logging.info(f"Bot told to shut up by {nick} until {datetime.fromtimestamp(self.shut_up_until)}")
                return True
        
        # Block all other plugins if we're shut up
        return self.is_shut_up()
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        """Handle /me actions - block if shut up"""
        return self.is_shut_up()
    
    async def handle_join(self, bot, nick: str, channel: str):
        """Handle user joins - not used by this plugin"""
        pass
    
    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        """Handle user parts - not used by this plugin"""
        pass