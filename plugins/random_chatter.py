"""
Random Chatter Plugin for PyMotion
Occasionally says random things when bored
"""

import random
import time

class RandomChatterPlugin:
    """Occasionally says random things"""
    
    def __init__(self):
        self.name = "random_chatter"
        self.priority = 10
        self.enabled = True
        self.last_chatter = time.time()
        self.min_interval = 300  # 5 minutes minimum between random chatter
        
        self.random_phrases = [
            "*yawns*", "*stretches*", "*looks around*", "*hums quietly*",
            "It's quiet in here...", "*twiddles thumbs*", "Hmm...",
            "*counts ceiling tiles*", "Anyone else smell popcorn?",
            "*contemplates existence*", "I wonder what's for dinner...",
            "*practices being mysterious*", "Beep boop!", "*does robot dance*"
        ]
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        # Very low chance of random chatter, and only if enough time has passed
        now = time.time()
        if (now - self.last_chatter > self.min_interval and 
            random.random() < 0.005):  # 0.5% chance
            
            response = random.choice(self.random_phrases)
            await bot.privmsg(channel, response)
            self.last_chatter = now
            return True
        
        return False
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        return False
    
    async def handle_join(self, bot, nick: str, channel: str):
        pass
    
    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        pass
