"""
Actions Plugin for PyMotion
Responds to /me actions
"""

import random
import re

class ActionPlugin:
    """Responds to /me actions"""
    
    def __init__(self):
        self.name = "actions"
        self.priority = 40
        self.enabled = True
        
        self.action_responses = {
            r'(?i).*(hugs?|hug) .*': [
                "*hugs back*", "*squeezes*", "*hugs tightly*", "Aww! *hugs*"
            ],
            r'(?i).*(waves?|wave).*': [
                "*waves back*", "*waves enthusiastically*", "*big wave*"
            ],
            r'(?i).*(pokes?|poke).*': [
                "*pokes back*", "Ow!", "*giggles*", "Hey, that tickles!"
            ],
            r'(?i).*(dances?|dance).*': [
                "*dances too*", "*joins in*", "*boogie*", "*tap dances*"
            ],
            r'(?i).*(cries?|cry|sobs?).*': [
                "*offers tissue*", "*comforts*", "There, there", "*pat pat*"
            ]
        }
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        return False
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        for pattern, responses in self.action_responses.items():
            if re.search(pattern, action):
                if random.random() < 0.5:  # 50% chance
                    response = random.choice(responses)
                    await bot.action(channel, response)
                    return True
        return False
    
    async def handle_join(self, bot, nick: str, channel: str):
        pass
    
    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        pass
