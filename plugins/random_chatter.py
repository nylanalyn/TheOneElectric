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
        self.channel_last_chatter = {}
        self.min_interval = 300  # 5 minutes minimum between random chatter
        self.idle_threshold = 180  # only chatter if channel quiet for 3 minutes
        
        self.random_phrases = [
            "*yawns*", "*stretches*", "*looks around*", "*hums quietly*",
            "It's quiet in here...", "*twiddles thumbs*", "Hmm...",
            "*counts ceiling tiles*", "Anyone else smell popcorn?",
            "*contemplates existence*", "I wonder what's for dinner...",
            "*practices being mysterious*", "Beep boop!", "*does robot dance*"
        ]
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        now = time.time()
        channel_state = bot.get_channel_state(channel)
        previous_activity = getattr(channel_state, "previous_activity", 0.0)
        
        # Require a stretch of silence before chatting
        if previous_activity <= 0:
            return False
        
        idle_time = now - previous_activity
        if idle_time < self.idle_threshold:
            return False
        
        last_chatter = self.channel_last_chatter.get(channel.lower(), 0.0)
        if now - last_chatter < self.min_interval:
            return False
        
        # Probability increases with idle time, capped for sanity
        idle_factor = min(1.0, (idle_time - self.idle_threshold) / (self.idle_threshold * 2))
        chance = max(0.02, idle_factor * 0.18)
        if random.random() < chance:
            response = random.choice(self.random_phrases)
            await bot.privmsg(channel, response)
            self.channel_last_chatter[channel.lower()] = now
            return True
        
        return False
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        return False
    
    async def handle_join(self, bot, nick: str, channel: str):
        pass
    
    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        pass
