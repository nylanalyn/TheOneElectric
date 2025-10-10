"""
Random Responses Plugin for PyMotion
Responds to various triggers with random responses
"""

import random
import re
from datetime import datetime

class RandomResponsePlugin:
    """Responds to various triggers with random responses"""
    
    def __init__(self):
        self.name = "random_responses"
        self.priority = 30
        self.enabled = True
        
        # Greetings
        self.greetings = {
            r'(?i)\b(hi|hey|hello|yo|greetings|morning|afternoon|evening)\b.*': [
                "Hello there!", "Hi!", "Hey!", "Greetings!", "Well hello!",
                "*waves*", "Oh, hello!", "Hey there!", "Hiya!",
                "*looks up* Oh, hi!", "Hello! *beams*"
            ]
        }
        
        # Thanks
        self.thanks = {
            r'(?i)\b(thanks?|thx|ta|cheers|thank you)\b.*': [
                "You're welcome!", "No problem!", "My pleasure!", "*bows*",
                "Don't mention it!", "Anytime!", "Happy to help!",
                "*tips hat*", "Of course!", "Glad I could help!"
            ]
        }
        
        # Questions about time
        self.time_responses = {
            r'(?i)what.*(time|clock).*\?': [
                "Time for you to get a watch!", "It's time to party!",
                "Time flies when you're having fun!", "Miller time!",
                "Adventure time!", "It's always tea time somewhere!",
                f"It's {datetime.now().strftime('%H:%M')} somewhere!"
            ]
        }
        
        # Love declarations
        self.love_responses = {
            r'(?i).*(love|adore) (you|u)\b.*': [
                "*blushes*", "Aww, shucks!", "I love you too!", "*hugs*",
                "You're too kind!", "*giggles*", "Feeling's mutual!",
                "Love you too, human!", "*hearts*"
            ]
        }
        
        # Anger/insults
        self.anger_responses = {
            r'(?i).*(stupid|dumb|idiot|moron|shut up).*': [
                "*pouts*", "That's not very nice!", "Hey now!",
                "*sticks tongue out*", "Meanie!", "Rude!",
                "*crosses arms*", "I'm telling!", "Hmph!"
            ]
        }
        
        # All caps (shouting)
        self.caps_responses = [
            "*covers ears*", "Why are we shouting?", "Indoor voice please!",
            "Wow, that's loud!", "*ducks*", "Easy there, tiger!",
            "No need to shout!", "*winces*"
        ]
        
        self.patterns = {
            **self.greetings,
            **self.thanks, 
            **self.time_responses,
            **self.love_responses,
            **self.anger_responses
        }
    
    def _get_bot_names(self, bot):
        """Return lowercase bot names including aliases, if any."""
        return [bot.config['nick'].lower()] + [
            alias.lower() for alias in bot.config.get('aliases', [])
        ]

    def _is_addressed_to_bot(self, message: str, bot_names) -> bool:
        """Determine whether the incoming message addresses the bot directly."""
        lowered = message.lower()
        for name in bot_names:
            # Direct mention anywhere in the message
            if re.search(r'\b' + re.escape(name) + r'\b', lowered):
                return True
            # Messages starting with the name followed by punctuation or whitespace
            if lowered.startswith(f"{name} ") or lowered.startswith(f"{name},") or lowered.startswith(f"{name}:"):
                return True
        return False

    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        bot_names = self._get_bot_names(bot)
        addressed_to_bot = self._is_addressed_to_bot(message, bot_names)
        targeted_response_chance = 0.65  # respond most of the time when spoken to
        ambient_response_chance = 0.05   # otherwise respond only rarely

        # Check for all caps (shouting)
        if len(message) > 5 and message.isupper() and any(c.isalpha() for c in message):
            chance = 0.25 if addressed_to_bot else 0.03
            if random.random() < chance:
                response = random.choice(self.caps_responses)
                await bot.privmsg(channel, response)
                return True
        
        # Check other patterns
        for pattern, responses in self.patterns.items():
            if re.search(pattern, message):
                chance = targeted_response_chance if addressed_to_bot else ambient_response_chance
                if random.random() < chance:
                    response = random.choice(responses)
                    await bot.privmsg(channel, response)
                    return True
        
        return False
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        return False
    
    async def handle_join(self, bot, nick: str, channel: str):
        pass
    
    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        pass
