"""
Actions Plugin for PyMotion
Responds to /me actions with friendship tracking
"""

import random
import re

class ActionPlugin:
    """Responds to /me actions"""

    def __init__(self):
        self.name = "actions"
        self.priority = 40
        self.enabled = True

        # Positive actions: +1 friendship
        self.positive_actions = {
            r'(?i).*(hugs?|hug) .*': [
                "*hugs back*", "*squeezes*", "*hugs tightly*", "Aww! *hugs*"
            ],
            r'(?i).*(pats?|pat).*': [
                "*purrs*", "*leans into the pat*", "*wags tail*", "*beams happily*", "^_^"
            ],
            r'(?i).*(waves?|wave).*': [
                "*waves back*", "*waves enthusiastically*", "*big wave*"
            ],
            r'(?i).*(pets?|pet).*': [
                "*purrs*", "*happy noises*", "^_^", "*wags tail*"
            ],
            r'(?i).*(dances?|dance).*': [
                "*dances too*", "*joins in*", "*boogie*", "*tap dances*"
            ],
            r'(?i).*(cries?|cry|sobs?).*': [
                "*offers tissue*", "*comforts*", "There, there", "*pat pat*"
            ],
            r'(?i).*(tickles?|tickle).*': [
                "*giggles*", "*squirms*", "Haha stop!", "*laughs*"
            ],
        }

        # Negative actions: -1 friendship
        self.negative_actions = {
            r'(?i).*(kicks?|kick).*': [
                "Ow! What was that for?", "*rubs shin*", "Hey!", "*whimpers*"
            ],
            r'(?i).*(throws?|throw|tosses?|toss).*': [
                "*catches it*", "*ducks*", "Whoa!", "*dodges*", "Hey, watch it!"
            ],
            r'(?i).*(bites?|bite).*': [
                "Ow!", "*yelps*", "That hurt!", "Hey! No biting!"
            ],
            r'(?i).*(pokes?|poke).*': [
                "*pokes back*", "Ow!", "*giggles*", "Hey, that tickles!"
            ],
        }

        # Generic responses for any action mentioning the bot
        self.generic_responses = [
            "*blinks*", "*beeps*", "o.o", "^_^", "*tilts head*",
            "*notices*", "Huh?", "*perks up*", "*responds in kind*",
            "*reacts*", "Hmm?", "*acknowledges*"
        ]

    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        return False

    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        # Check if action is directed at bot (including aliases)
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        bot_mentioned = any(bot_name in action.lower() for bot_name in bot_names)

        # Only respond if bot is mentioned in the action
        if not bot_mentioned:
            return False

        user_state = bot.get_user_state(channel, nick)

        # Check positive actions first
        for pattern, responses in self.positive_actions.items():
            if re.search(pattern, action):
                if random.random() < 0.7:
                    response = random.choice(responses)
                    await bot.action(channel, response)
                    user_state.friendship += 1
                    return True
                return False

        # Check negative actions
        for pattern, responses in self.negative_actions.items():
            if re.search(pattern, action):
                if random.random() < 0.7:
                    response = random.choice(responses)
                    await bot.action(channel, response)
                    user_state.friendship -= 1
                    return True
                return False

        # If no specific action matched, use generic response
        if random.random() < 0.5:
            response = random.choice(self.generic_responses)
            await bot.action(channel, response)
            return True

        return False

    async def handle_join(self, bot, nick: str, channel: str):
        pass

    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        pass
