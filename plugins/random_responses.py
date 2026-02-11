"""
Random Responses Plugin for PyMotion
Responds to various direct triggers with guarded randomness
Tracks friendship on thanks/love triggers
"""

import random
import re
import time
from collections import defaultdict, deque
from datetime import datetime

class RandomResponsePlugin:
    """Responds to triggers, biased toward direct mentions to reduce noise"""

    def __init__(self):
        self.name = "random_responses"
        self.priority = 30
        self.enabled = True

        self.targeted_response_chance = 0.75
        self.ambient_response_chance = 0.02
        self.user_cooldown_seconds = 90
        self.channel_cooldown_seconds = 35

        self.last_user_response = {}
        self.last_channel_response = {}
        self.recent_responses = defaultdict(lambda: deque(maxlen=3))

        # Triggers that adjust friendship
        self._friendship_triggers = {"thanks": 2, "love": 2}

        self.triggers = [
            {
                "name": "greeting",
                "pattern": re.compile(r'(?i)\b(hi|hey|hello|yo|greetings|morning|afternoon|evening)\b.*'),
                "responses": [
                    "Hello there!", "Hi!", "Hey!", "Greetings!", "Well hello!",
                    "*waves*", "Oh, hello!", "Hey there!", "Hiya!",
                    "*looks up* Oh, hi!", "Hello! *beams*"
                ],
                "allow_ambient": False,
            },
            {
                "name": "thanks",
                "pattern": re.compile(r'(?i)\b(thanks?|thx|ta|cheers|thank you)\b.*'),
                "responses": [
                    "You're welcome!", "No problem!", "My pleasure!", "*bows*",
                    "Don't mention it!", "Anytime!", "Happy to help!",
                    "*tips hat*", "Of course!", "Glad I could help!"
                ],
                "allow_ambient": False,
            },
            {
                "name": "time",
                "pattern": re.compile(r'(?i)what.*(time|clock).*\?'),
                "responses": [
                    "Time for you to get a watch!",
                    "It's time to party!",
                    "Time flies when you're having fun!",
                    "Miller time!",
                    "Adventure time!",
                    "It's always tea time somewhere!",
                    "It's {time} somewhere!"
                ],
                "allow_ambient": False,
            },
            {
                "name": "love",
                "pattern": re.compile(r'(?i).*(love|adore) (you|u)\b.*'),
                "responses": [
                    "*blushes*", "Aww, shucks!", "I love you too!", "*hugs*",
                    "You're too kind!", "*giggles*", "Feeling's mutual!",
                    "Love you too, human!", "*hearts*"
                ],
                "allow_ambient": False,
            },
            {
                "name": "anger",
                "pattern": re.compile(r'(?i).*(stupid|dumb|idiot|moron|shut up).*'),
                "responses": [
                    "*pouts*", "That's not very nice!", "Hey now!",
                    "*sticks tongue out*", "Meanie!", "Rude!",
                    "*crosses arms*", "I'm telling!", "Hmph!"
                ],
                "allow_ambient": False,
            },
        ]

        self.caps_responses = [
            "*covers ears*", "Why are we shouting?", "Indoor voice please!",
            "Wow, that's loud!", "*ducks*", "Easy there, tiger!",
            "No need to shout!", "*winces*"
        ]

    def _get_bot_names(self, bot):
        """Return lowercase bot names including aliases, if any."""
        return [bot.config['nick'].lower()] + [
            alias.lower() for alias in bot.config.get('aliases', [])
        ]

    def _is_addressed_to_bot(self, message: str, bot_names) -> bool:
        """Determine whether the incoming message addresses the bot directly."""
        lowered = message.lower()
        for name in bot_names:
            if re.search(r'\b' + re.escape(name) + r'\b', lowered):
                return True
            if lowered.startswith(f"{name} ") or lowered.startswith(f"{name},") or lowered.startswith(f"{name}:"):
                return True
        return False

    def _cooldowns_allow(self, nick: str, channel: str, now: float) -> bool:
        nick_key = nick.lower()
        channel_key = channel.lower()

        last_user = self.last_user_response.get(nick_key, 0)
        if now - last_user < self.user_cooldown_seconds:
            return False

        last_channel = self.last_channel_response.get(channel_key, 0)
        if now - last_channel < self.channel_cooldown_seconds:
            return False

        return True

    def _record_response(self, nick: str, channel: str, now: float):
        self.last_user_response[nick.lower()] = now
        self.last_channel_response[channel.lower()] = now

    def _select_response(self, trigger_name: str, responses):
        history = self.recent_responses[trigger_name]
        available = [resp for resp in responses if resp not in history]
        template = random.choice(available or responses)
        history.append(template)

        if "{time}" in template:
            return template.format(time=datetime.now().strftime('%H:%M'))
        return template

    def _should_respond(self, trigger: dict, addressed_to_bot: bool, message: str, energy: float = 1.0) -> bool:
        if addressed_to_bot:
            chance = self.targeted_response_chance * energy
            return random.random() < min(0.95, chance)

        if trigger.get("allow_ambient"):
            chance = trigger.get("ambient_chance", self.ambient_response_chance)
            return random.random() < chance

        return False

    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        bot_names = self._get_bot_names(bot)
        addressed_to_bot = self._is_addressed_to_bot(message, bot_names)
        now = time.time()
        personality = bot.get_time_personality()
        energy = personality["energy"]

        if len(message) > 5 and message.isupper() and any(c.isalpha() for c in message):
            chance = 0.30 if addressed_to_bot else 0.02
            if random.random() < chance and self._cooldowns_allow(nick, channel, now):
                response = self._select_response("caps", self.caps_responses)
                await bot.privmsg(channel, response)
                self._record_response(nick, channel, now)
                return True

        for trigger in self.triggers:
            if trigger["pattern"].search(message):
                if self._should_respond(trigger, addressed_to_bot, message, energy) and self._cooldowns_allow(nick, channel, now):
                    response = self._select_response(trigger["name"], trigger["responses"])
                    await bot.privmsg(channel, response)
                    self._record_response(nick, channel, now)

                    # Friendship gain on thanks/love
                    gain = self._friendship_triggers.get(trigger["name"], 0)
                    if gain and addressed_to_bot:
                        user_state = bot.get_user_state(channel, nick)
                        user_state.friendship += gain

                    return True

        return False

    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        return False

    async def handle_join(self, bot, nick: str, channel: str):
        pass

    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        pass
