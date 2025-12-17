"""
Lil Jon Plugin for PyMotion
Only active in #crunk - responds to !GETCRUNK and sends random quotes periodically
"""

import random
import time
import asyncio

class LilJonPlugin:
    """Brings the crunkness of Lil Jon to #crunk"""

    def __init__(self):
        self.name = "liljon"
        self.priority = 100  # High priority - in #crunk this should take over
        self.enabled = True
        self.target_channel = "#crunk"

        # Cooldown settings for the trigger command
        self.trigger_command = "!getcrunk"
        self.cooldown_duration = 300  # 5 minutes in seconds
        self.last_triggered_time = 0

        # Passive quote timing
        self.last_passive_quote = 0
        self.next_passive_delay = self._get_random_delay()

        # Lil Jon's greatest hits
        self.quotes = [
            "YEEEEEEAH!",
            "OKAY!",
            "WHAT!?",
            "LET'S GO!",
            "GET CRUNK!",
            "DON'T START NO SHIT, WON'T BE NO SHIT!",
            "GET LOW!",
            "SHOTS! SHOTS! SHOTS!",
            "TURN DOWN FOR WHAT!?",
            "HUUUUH!?",
            "BEND OVA!",
            "TO THE WINDOW! TO THE WALL!",
            "BIA'BIA'!",
            "Y'ALL DON'T WANT NONE!",
            "WORK IT!",
            "MOVE, BITCH!",
            "ALL SKEET SKEET!",
            "SAY WHAT!?",
            "PUT YO HOOD UP!",
            "Y'ALL AIN'T READY!",
            "WE GON' RIDE TONIGHT!",
            "CLAP YO HANDS!",
            "CRUNK AIN'T DEAD!",
            "WHO YOU WIT!?",
            "BACK IT UP!",
            "EVERYBODY SCREAM!",
            "WHERE DEM GIRLS AT!?",
            "LET ME SEE YOU WOBBLE!",
            "AYE!",
            "C'MON!",
            "HOLD UP!",
            "THAT'S RIGHT!",
            "GET OUTTA YO MIND!",
            "THROW EM UP!",
            "ONE MORE TIME!",
            "HERE WE GO!",
            "BRING IT BACK!",
            "HEY!",
            "MAKE SOME NOISE!",
            "BOUNCE!",
            "DROP IT!",
            "LET'S GET IT!",
            "FIRE IT UP!"
        ]

    def _get_random_delay(self):
        """Get a random delay between 15 and 45 minutes (in seconds)"""
        return random.randint(900, 2700)

    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        # Only active in #crunk
        if channel.lower() != self.target_channel:
            return False

        now = time.time()

        # Check for !GETCRUNK command (case insensitive)
        if message.strip().lower() == self.trigger_command:
            if (now - self.last_triggered_time) > self.cooldown_duration:
                quote = random.choice(self.quotes)
                await bot.privmsg(channel, quote)
                self.last_triggered_time = now
            # Always return True in #crunk to block other plugins
            return True

        # Check if it's time for a passive quote
        if self.last_passive_quote == 0:
            # First message since bot started, initialize the timer
            self.last_passive_quote = now
        elif (now - self.last_passive_quote) > self.next_passive_delay:
            # Time for a random quote!
            quote = random.choice(self.quotes)
            await bot.privmsg(channel, quote)
            self.last_passive_quote = now
            self.next_passive_delay = self._get_random_delay()

        # Return True to block all other plugins in #crunk
        return True

    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        # Block other plugins in #crunk but don't respond to actions
        if channel.lower() == self.target_channel:
            return True
        return False

    async def handle_join(self, bot, nick: str, channel: str):
        pass

    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        pass
