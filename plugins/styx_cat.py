"""
Styx Cat Plugin for PyMotion
Gives a hint about styx's cat's name when asked
"""

import random
import re

class StyxCatPlugin:
    """Provides a cryptic hint about styx's cat's name"""

    def __init__(self):
        self.name = "styx_cat"
        self.priority = 70  # Run before most plugins
        self.enabled = True

        self.hints = [
            "if i went to a wedding and stood up, glass in hand to give a speech, i'd be giving a?",
            "when someone's about to get destroyed, you might say 'you're ____'",
            "at new year's eve, we raise our glasses and make a?",
            "what do you put butter and jam on in the morning?",
            "the life of the party, the talk of the town... the ____ of the town",
            "millennials are supposedly killing industries by spending all their money on avocado ____",
            "if you're warm and cozy, you might say you're 'warm as ____'",
            "raise your glass! let's propose a ____",
            "bread goes in, ____ comes out. you can't explain that",
            "eggs, bacon, and a couple slices of ____",
            "the brave little toaster's whole job was making ____",
            "what does a toaster make?",
            "cinnamon ____ crunch is a cereal",
            "french ____ is just eggy bread",
        ]

    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Handle message and check if styx is asking about their cat's name"""
        # Only respond to styx
        if nick.lower() != "styx":
            return False

        # Check if they're asking about their cat's name
        if re.search(r"(?i)what'?s?\s+my\s+cat'?s?\s+name", message):
            await bot.privmsg(channel, random.choice(self.hints))
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
