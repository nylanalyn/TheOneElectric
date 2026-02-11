"""
Lil Jon Plugin for PyMotion
Only active in #crunk - responds to !GETCRUNK and sends random quotes periodically
"""

import random
import time
import asyncio
import logging

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

        # Passive quote timing (every 15 minutes)
        self.passive_interval_seconds = 15 * 60
        self._passive_task: asyncio.Task | None = None

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
            "FIRE IT UP!",
            "It's a piece of cake to bake a pretty cake",
            "You gotta do the cooking by the book",
            "Never use a messy recipe",
            "If you do the cooking by the book",
            "Making food is just like science",
            "With tools that blend and baste"
                      ]

    async def start(self, bot):
        if self._passive_task and not self._passive_task.done():
            return
        if hasattr(bot, "create_background_task"):
            self._passive_task = bot.create_background_task(
                self._passive_quote_loop(bot),
                name="liljon_passive_quote_loop",
            )
        else:
            self._passive_task = asyncio.create_task(self._passive_quote_loop(bot))

    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        # Only active in #crunk
        if channel.lower() != self.target_channel.lower():
            return False

        # Check for !GETCRUNK command (case insensitive)
        if message.strip().lower() == self.trigger_command:
            now = time.time()
            if (now - self.last_triggered_time) > self.cooldown_duration:
                quote = random.choice(self.quotes)
                await bot.privmsg(channel, quote)
                self.last_triggered_time = now
            return True

        # Let other plugins (admin, shutup, etc.) handle non-crunk messages
        return False

    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        return False

    async def handle_join(self, bot, nick: str, channel: str):
        pass

    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        pass

    async def _passive_quote_loop(self, bot):
        try:
            while True:
                await asyncio.sleep(self.passive_interval_seconds)
                if not self.enabled:
                    continue
                if not getattr(bot, "connected", False):
                    continue
                if self.target_channel not in getattr(bot, "channels", set()):
                    continue
                quote = random.choice(self.quotes)
                await bot.privmsg(self.target_channel, quote)
        except asyncio.CancelledError:
            return
        except Exception as e:
            logging.error(f"LilJon passive quote loop crashed: {e}")

    async def cleanup(self):
        if self._passive_task:
            self._passive_task.cancel()
            try:
                await self._passive_task
            except asyncio.CancelledError:
                pass
            self._passive_task = None
