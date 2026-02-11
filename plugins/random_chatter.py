"""
Random Chatter Plugin for PyMotion
Occasionally says random things when bored
Opinion recall: shares formed opinions during idle chatter
Time-of-day aware: late-night and Friday phrases
"""

import random
import time

class RandomChatterPlugin:
    """Occasionally says random things"""

    def __init__(self):
        self.name = "random_chatter"
        self.priority = 10
        self.enabled = True
        self.channel_last_chatter = {}
        self.min_interval = 300  # 5 minutes minimum between random chatter
        self.idle_threshold = 180  # only chatter if channel quiet for 3 minutes

        self.random_phrases = [
            "*yawns*", "*stretches*", "*looks around*", "*hums quietly*",
            "It's quiet in here...", "*twiddles thumbs*", "Hmm...",
            "*counts ceiling tiles*", "Anyone else smell popcorn?",
            "*contemplates existence*", "I wonder what's for dinner...",
            "*practices being mysterious*", "Beep boop!", "*does robot dance*"
        ]

        # Late-night phrases (energy <= 0.7)
        self.late_night_phrases = [
            "*yawns loudly*", "Why am I still awake...",
            "*stares into the void at this hour*",
            "It's too late for this. Or too early. I've lost track.",
            "*half-asleep beeping*", "The 3 AM thoughts are hitting...",
            "*slumps over keyboard*",
        ]

        # Friday evening phrases (energy >= 1.5)
        self.friday_phrases = [
            "It's FRIDAY! Party time!",
            "*cranks up the music* WEEKEND VIBES!",
            "Friday energy is unmatched!",
            "Weekend countdown: engaged!",
            "*puts on party hat* Let's goooo!",
        ]

        # Opinion templates
        self.positive_opinion_templates = [
            "You know what's great? {topic}.",
            "I've been thinking about {topic}. It's actually pretty cool.",
            "Hot take: {topic} is underrated.",
            "Can we talk about how good {topic} is?",
        ]
        self.negative_opinion_templates = [
            "Don't get me started on {topic}...",
            "Unpopular opinion: {topic} is overrated.",
            "I have THOUGHTS about {topic}. None of them good.",
            "*shudders* {topic}.",
        ]
        self.neutral_opinion_templates = [
            "People keep talking about {topic}. It's fine, I guess.",
            "{topic}. Huh. I have mixed feelings.",
            "I keep hearing about {topic}. Not sure what to think.",
            "Is {topic} a thing? Apparently it's a thing.",
        ]

    def _get_opinion_phrase(self, bot) -> str | None:
        """Try to get an opinion to share. Returns None if no formed opinions."""
        formed = {topic: data for topic, data in bot.opinions.items()
                  if data.get("formed_at", 0) > 0}
        if not formed:
            return None

        topic = random.choice(list(formed.keys()))
        sentiment = formed[topic]["sentiment"]

        if sentiment > 0.3:
            return random.choice(self.positive_opinion_templates).format(topic=topic)
        elif sentiment < -0.3:
            return random.choice(self.negative_opinion_templates).format(topic=topic)
        else:
            return random.choice(self.neutral_opinion_templates).format(topic=topic)

    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        now = time.time()
        channel_state = bot.get_channel_state(channel)
        previous_activity = getattr(channel_state, "previous_activity", 0.0)

        # Require a stretch of silence before chatting
        if previous_activity <= 0:
            return False

        idle_time = now - previous_activity
        if idle_time < self.idle_threshold:
            return False

        last_chatter = self.channel_last_chatter.get(channel.lower(), 0.0)
        if now - last_chatter < self.min_interval:
            return False

        # Probability increases with idle time, capped for sanity
        idle_factor = min(1.0, (idle_time - self.idle_threshold) / (self.idle_threshold * 2))
        chance = max(0.02, idle_factor * 0.18)
        if random.random() < chance:
            personality = bot.get_time_personality()

            # 30% chance to share an opinion instead
            if random.random() < 0.3:
                opinion = self._get_opinion_phrase(bot)
                if opinion:
                    await bot.privmsg(channel, opinion)
                    self.channel_last_chatter[channel.lower()] = now
                    return True

            # Time-of-day flavored phrases
            if personality["energy"] >= 1.5 and personality["flavor"] == "It's FRIDAY!":
                response = random.choice(self.friday_phrases)
            elif personality["energy"] <= 0.7:
                response = random.choice(self.late_night_phrases)
            else:
                response = random.choice(self.random_phrases)

            await bot.privmsg(channel, response)
            self.channel_last_chatter[channel.lower()] = now
            return True

        return False

    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        return False

    async def handle_join(self, bot, nick: str, channel: str):
        pass

    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        pass
