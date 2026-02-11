"""
Greetings Plugin for PyMotion
Handles greetings and remembers who was greeted
Friendship-aware: warm/cold greetings based on relationship tier
"""

import re
import random

class GreetingPlugin:
    """Handles greetings and remembers who was greeted"""

    def __init__(self):
        self.name = "greetings"
        self.priority = 60
        self.enabled = True

        self.greeting_patterns = [
            r'(?i)\b(hi|hey|hello|yo|greetings|morning|afternoon|evening)\b',
            r'(?i)\b(bonjour|hola|guten tag|konnichiwa)\b'
        ]
        self.welcome_back_patterns = [
            r'(?i)\bwelcome back\b',
            r'(?i)\bwb\b'
        ]
        self.thanks_ack_patterns = [
            r"(?i)\byou(?:'|')?re welcome\b",
            r'(?i)\byour welcome\b',
            r'(?i)\byw\b'
        ]

        # Tiered greeting responses
        self.responses_hostile = [
            "Oh. It's you, {nick}.", "What do YOU want, {nick}?",
            "*glares at {nick}*", "{nick}. Ugh.",
            "*ignores {nick}*... fine. Hi.", "Back again, {nick}? Joy.",
        ]
        self.responses_cold = [
            "Hi, {nick}.", "{nick}.", "Hey {nick}.",
            "*nods at {nick}*", "Oh. Hello, {nick}.",
        ]
        self.responses_neutral = [
            "Hello {nick}!", "Hey there {nick}!", "Hi {nick}!",
            "Greetings {nick}!", "Well hello {nick}!", "*waves at {nick}*",
            "Oh, hi {nick}!", "Hey {nick}! *beams*", "Hello there, {nick}!"
        ]
        self.responses_friendly = [
            "Hey {nick}!! Great to see you!", "{nick}! *waves excitedly*",
            "There's my friend {nick}!", "Hello {nick}! *happy beeps*",
            "{nick}!! How's it going?", "Yooo {nick}! Welcome!",
        ]
        self.responses_bestie = [
            "{nick}!!! *tackles with a hug* I MISSED YOU!",
            "BEST FRIEND {nick} IS HERE! *confetti*",
            "{nick}!! The party can start now!",
            "*drops everything* {nick}! My favorite person!",
            "{nick}! Finally, someone worth talking to!",
        ]

        self.welcome_back_responses = [
            "Thanks {nick}, it feels good to be back!",
            "Appreciate the welcome, {nick}!",
            "Back online and buzzing again—thanks {nick}!",
            "Missed you too, {nick}! Happy to be back."
        ]
        self.thanks_ack_responses = [
            "Anytime, {nick}!",
            "Thanks for having my back, {nick}!",
            "Always appreciate you, {nick}!",
            "Glad we're synced up, {nick}."
        ]

        # Grumpy morning greetings (used when grumpiness > 0)
        self.grumpy_greetings = [
            "*grunts* ...hi, {nick}.", "Mmph. Hey {nick}.",
            "*barely opens eyes* Oh. {nick}. Hi.",
            "{nick}... it's too early for this.",
            "*yawns in {nick}'s direction*",
        ]

    def _get_greeting_pool(self, tier: str) -> list:
        pools = {
            "hostile": self.responses_hostile,
            "cold": self.responses_cold,
            "neutral": self.responses_neutral,
            "friendly": self.responses_friendly,
            "bestie": self.responses_bestie,
        }
        return pools.get(tier, self.responses_neutral)

    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Handle greetings"""
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        message_lower = message.lower()
        bot_mentioned = any(bot_name in message_lower for bot_name in bot_names)
        directed_at_bot = any(message_lower.startswith(bot_name) for bot_name in bot_names) or bot_mentioned

        if directed_at_bot:
            if any(re.search(pattern, message) for pattern in self.welcome_back_patterns):
                response = random.choice(self.welcome_back_responses).format(nick=nick)
                await bot.privmsg(channel, response)
                user_state = bot.get_user_state(channel, nick)
                user_state.last_interaction = "welcome_back_ack"
                return True

            if any(re.search(pattern, message) for pattern in self.thanks_ack_patterns):
                response = random.choice(self.thanks_ack_responses).format(nick=nick)
                await bot.privmsg(channel, response)
                user_state = bot.get_user_state(channel, nick)
                user_state.last_interaction = "gratitude_ack"
                return True

        # Only respond with greetings if message seems to be greeting the bot
        if not any(re.search(pattern, message) for pattern in self.greeting_patterns):
            return False

        # Only respond if the bot was explicitly mentioned or addressed
        if directed_at_bot:
            # Get personality and friendship
            personality = bot.get_time_personality()
            energy = personality["energy"]
            grumpiness = personality["grumpiness"]
            tier = bot.get_friendship_tier(channel, nick)

            # Response chance scaled by energy
            base_chance = 0.7
            chance = min(0.95, base_chance * energy)
            if random.random() < chance:
                user_state = bot.get_user_state(channel, nick)

                # Grumpy override at low energy times
                if grumpiness > 0.2 and random.random() < grumpiness and tier not in ("bestie", "friendly"):
                    pool = self.grumpy_greetings
                else:
                    pool = self._get_greeting_pool(tier)

                response = random.choice(pool).format(nick=nick)
                await bot.privmsg(channel, response)

                # Friendship: +1 for greeting the bot
                user_state.friendship += 1
                user_state.greeted_today = True
                user_state.last_interaction = "greeting"
                return True

        return False

    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        """Handle /me actions - not used by this plugin"""
        return False

    async def handle_join(self, bot, nick: str, channel: str):
        """Reset greeting status when user joins"""
        user_state = bot.get_user_state(channel, nick)
        user_state.greeted_today = False

    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        """Handle user parts - not used by this plugin"""
        pass
