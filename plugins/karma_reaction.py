"""
Karma Reaction Plugin for PyMotion
Reacts when the bot receives ++ or -- karma
"""

import re
import random


class KarmaReactionPlugin:
    """Reacts to karma given to the bot"""

    def __init__(self):
        self.name = "karma_reaction"
        self.priority = 50
        self.enabled = True

        self.positive_responses = [
            "Aww, thanks {nick}! *beams*",
            "You're too kind, {nick}!",
            "*blushes* Thanks {nick}!",
            "Right back at ya, {nick}! *grins*",
            "Yay! I appreciate you {nick}!",
            "*does a little dance* Thanks {nick}!",
            "You just made my day, {nick}!",
            "{nick}! You're the best!",
            "Aww shucks, {nick} *shuffles feet*",
            "*happy beeping noises* Thanks {nick}!",
        ]

        self.negative_responses = [
            "Hey! What did I do to you, {nick}?!",
            "Rude! *glares at {nick}*",
            "Oh that's just mean, {nick}...",
            "*sad beeping* Why, {nick}?",
            "Well, {nick}-- right back at you!",
            "I see how it is, {nick}. I see how it is.",
            "*huffs* Fine, {nick}. Be that way.",
            "Ouch, {nick}. That hurt. Right in the circuits.",
            "{nick}, you wound me!",
            "*makes note* {nick} is on the naughty list now.",
            "Et tu, {nick}?",
        ]

    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """React to karma given to the bot"""
        # Get bot names (nick + aliases)
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]

        # Check for positive karma
        for bot_name in bot_names:
            # Match patterns like "botnick++", "botnick ++" or "botnick ++"
            if re.search(rf'(?i)\b{re.escape(bot_name)}\s*\+\+', message):
                response = random.choice(self.positive_responses).format(nick=nick)
                await bot.privmsg(channel, response)
                return True

            # Check for negative karma
            if re.search(rf'(?i)\b{re.escape(bot_name)}\s*--', message):
                response = random.choice(self.negative_responses).format(nick=nick)
                await bot.privmsg(channel, response)
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
