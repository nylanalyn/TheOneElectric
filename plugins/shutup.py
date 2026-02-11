"""
Shut Up Plugin for PyMotion
Handles the shut up command - makes bot go quiet for a while
Tracks grudges and passive-aggressive responses after silence ends
"""

import re
import time
import random
import logging
from datetime import datetime

class ShutUpPlugin:
    """Handles shut up command - HIGHEST PRIORITY"""

    def __init__(self):
        self.name = "shutup"
        self.priority = 100  # Highest priority
        self.enabled = True
        self.shut_up_until = 0
        self.shut_up_duration = 300  # 5 minutes default

        # Grudge tracking
        self.silenced_by = {}  # {channel: nick}
        self.grudge_comments_remaining = {}  # {channel: {nick: int}}

        # Passive-aggressive responses when grudge is active
        self.grudge_comments = [
            "Oh, NOW {nick} wants to talk...",
            "Interesting. {nick} has opinions again.",
            "*side-eyes {nick}*",
            "Bold words from someone who told me to shut up.",
            "*mutters about {nick} under breath*",
            "{nick} speaking up? How brave.",
            "Oh look, {nick} found their voice. Unlike SOME of us who were SILENCED.",
            "Mmhmm. Sure, {nick}. Whatever you say.",
            "*passive-aggressively ignores {nick}*... wait, I just acknowledged them. Dang.",
            "Remember when {nick} told me to be quiet? Good times.",
        ]

        # Repeat offender callouts (shutup_count >= 3)
        self.repeat_offender_responses = [
            "Again, {nick}? This is getting old.",
            "*sulks* {nick} tells me to shut up EVERY time...",
            "You know what, {nick}? Fine. But I'm keeping count.",
            "{nick}... you realize this is the {count}th time, right?",
            "*sigh* {nick}'s favorite hobby: silencing me.",
            "At this point, {nick}, it's basically tradition.",
        ]

    def is_shut_up(self) -> bool:
        """Check if bot should be quiet"""
        return time.time() < self.shut_up_until

    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Handle messages and check for shut up commands"""
        # Check for grudge comments BEFORE checking silence (grudge fires after silence ends)
        if not self.is_shut_up() and channel in self.grudge_comments_remaining:
            nick_lower = nick.lower()
            grudges = self.grudge_comments_remaining[channel]
            if nick_lower in grudges and grudges[nick_lower] > 0:
                if random.random() < 0.6:  # 60% chance per message
                    comment = random.choice(self.grudge_comments).format(nick=nick)
                    await bot.privmsg(channel, comment)
                    grudges[nick_lower] -= 1
                    if grudges[nick_lower] <= 0:
                        del grudges[nick_lower]
                    if not grudges:
                        del self.grudge_comments_remaining[channel]
                    # Don't return True — let other plugins still process

        # Check if someone told bot to shut up
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]

        for bot_name in bot_names:
            if re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\b(shut up|stfu|be quiet|shush)\b', message):
                self.shut_up_until = time.time() + self.shut_up_duration

                # Track who silenced us
                self.silenced_by[channel] = nick

                # Friendship: -3
                user_state = bot.get_user_state(channel, nick)
                user_state.friendship -= 3
                user_state.shutup_count += 1
                user_state.last_shutup_time = time.time()

                # Repeat offender callout
                if user_state.shutup_count >= 3:
                    response = random.choice(self.repeat_offender_responses).format(
                        nick=nick, count=user_state.shutup_count
                    )
                    await bot.privmsg(channel, response)
                else:
                    await bot.privmsg(channel, f"*sulks* Fine, I'll be quiet for {self.shut_up_duration // 60} minutes...")

                logging.info(f"Bot told to shut up by {nick} (count: {user_state.shutup_count}) until {datetime.fromtimestamp(self.shut_up_until)}")

                # Set up grudge comments for when silence ends
                grudge_count = random.randint(2, 4)
                if channel not in self.grudge_comments_remaining:
                    self.grudge_comments_remaining[channel] = {}
                self.grudge_comments_remaining[channel][nick.lower()] = grudge_count

                return True

        # Block all other plugins if we're shut up
        return self.is_shut_up()

    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        """Handle /me actions - block if shut up"""
        return self.is_shut_up()

    async def handle_join(self, bot, nick: str, channel: str) -> bool:
        """Block join handlers while shut up"""
        return self.is_shut_up()

    async def handle_part(self, bot, nick: str, channel: str, reason: str) -> bool:
        """Block part handlers while shut up"""
        return self.is_shut_up()
