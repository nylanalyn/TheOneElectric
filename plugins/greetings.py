"""
Greetings Plugin for PyMotion
Handles greetings and remembers who was greeted
"""

import re
import random

class GreetingPlugin:
    """Handles greetings and remembers who was greeted"""
    
    def __init__(self):
        self.name = "greetings"
        self.priority = 60
        self.enabled = True
        
        self.greeting_patterns = [
            r'(?i)\b(hi|hey|hello|yo|greetings|morning|afternoon|evening)\b',
            r'(?i)\b(bonjour|hola|guten tag|konnichiwa)\b'
        ]
        
        self.responses = [
            "Hello {nick}!", "Hey there {nick}!", "Hi {nick}!",
            "Greetings {nick}!", "Well hello {nick}!", "*waves at {nick}*",
            "Oh, hi {nick}!", "Hey {nick}! *beams*", "Hello there, {nick}!"
        ]
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Handle greetings"""
        # Only respond if message seems to be greeting the bot
        if not any(re.search(pattern, message) for pattern in self.greeting_patterns):
            return False
        
        # Check if greeting is directed at bot (including aliases)
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        bot_mentioned = any(bot_name in message.lower() for bot_name in bot_names)
        directed_at_bot = any(message.lower().startswith(bot_name) for bot_name in bot_names) or bot_mentioned
        
        user_state = bot.get_user_state(channel, nick)
        
        # Only respond if:
        # 1. Bot was mentioned/addressed directly, OR
        # 2. User hasn't been greeted today and it's a general greeting
        if directed_at_bot or not user_state.greeted_today:
            if random.random() < 0.7:  # 70% chance
                response = random.choice(self.responses).format(nick=nick)
                await bot.privmsg(channel, response)
                user_state.greeted_today = True
                user_state.last_interaction = "greeting"
                return True
        
        return False
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        """Handle /me actions - not used by this plugin"""
        return False
    
    async def handle_join(self, bot, nick: str, channel: str):
        """Handle user joins - not used by this plugin"""
        pass
    
    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        """Handle user parts - not used by this plugin"""
        pass