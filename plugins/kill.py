"""
Kill Plugin for PyMotion
Playful kill command with ridiculous weapons
"""

import random
import re

class KillPlugin:
    """Playful kill command"""
    
    def __init__(self):
        self.name = "kill"
        self.priority = 70
        self.enabled = True
        
        self.weapons = [
            "a rubber duck", "harsh language", "a wet noodle", "a feather",
            "tickles", "bad puns", "a pillow", "stale cookies",
            "elevator music", "a strongly worded letter", "interpretive dance",
            "an uncomfortable stare", "a paper airplane", "social awkwardness"
        ]
        
        self.actions = [
            "gently pokes {target} with {weapon}",
            "threatens {target} with {weapon}",
            "waves {weapon} menacingly at {target}",
            "attempts to defeat {target} using {weapon}",
            "challenges {target} to combat with {weapon}",
            "pelts {target} with {weapon}"
        ]
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        kill_match = re.search(r'(?i)kill (\w+)(?:\s+with\s+(.+))?', message)
        if not kill_match:
            return False
        
        target = kill_match.group(1)
        weapon = kill_match.group(2) if kill_match.group(2) else random.choice(self.weapons)
        
        if target.lower() == bot.config['nick'].lower():
            await bot.privmsg(channel, f"*dodges* You can't kill me, {nick}! I'm immortal!")
        elif target.lower() == nick.lower():
            await bot.privmsg(channel, f"*hands {nick} a mirror* Here you go!")
        else:
            action = random.choice(self.actions).format(target=target, weapon=weapon)
            await bot.action(channel, action)
        
        return True
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        return False
    
    async def handle_join(self, bot, nick: str, channel: str):
        pass
    
    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        pass
