"""
Random Sentences Plugin for PyMotion
Generates random but natural-sounding sentences by mixing structured fragments.
"""

import random
import time
import logging
from dataclasses import dataclass
from collections import deque


@dataclass(frozen=True)
class Activity:
    """Verb forms used to keep tense consistent."""
    gerund: str
    past: str
    infinitive: str


@dataclass(frozen=True)
class Place:
    """Location plus default preposition for fluent phrasing."""
    name: str
    default_preposition: str = "at"

    def describe(self, prefix: str | None = None) -> str:
        preposition = self.default_preposition if prefix is None else prefix
        if not preposition:
            return self.name
        return f"{preposition} {self.name}"


class RandomSentencesPlugin:
    """Generates random sentences using structured templates and word lists."""
    
    def __init__(self):
        self.name = "random_sentences"
        self.priority = 12  # Medium priority - between chatter and quotes
        self.enabled = True
        self.last_sentence = time.time()
        self.min_interval = 240  # 4 minutes minimum between sentences
        self.last_activity = {}  # Track last activity per channel
        
        # Word lists for placeholders
        self.things = [
            "a mysterious key", "a glowing rock", "a talking cat", "a rusty sword", 
            "a forgotten book", "a strange device", "a magical hat", "a broken clock",
            "a silver coin", "a crystal ball", "a leather journal", "a wooden flute",
            "a mechanical bird", "a velvet pouch", "a brass compass", "a silk scarf",
            "a stone tablet", "a glass orb", "a copper wire", "a feather quill",
            "a rubber chicken", "a spork", "a half-eaten sandwich", "a suspiciously clean sock",
            "a collection of mismatched buttons", "a jar of pickles", "a squeaky toy",
            "a single dice", "a tangled ball of yarn", "a very important rock"
        ]
        
        self.places = [
            Place("the abandoned library", "in"),
            Place("the enchanted forest", "in"),
            Place("the bustling marketplace", "at"),
            Place("the ancient ruins", "among"),
            Place("the underground observatory", "inside"),
            Place("the floating island", "on"),
            Place("the clockwork city", "around"),
            Place("the misty mountains", "through"),
            Place("the crystal desert", "across"),
            Place("the forgotten temple", "inside"),
            Place("the whispering woods", "in"),
            Place("the rooftop garden", "on"),
            Place("the lantern-lit alley", "in"),
            Place("the seaside observatory", "at"),
            Place("the underground archive", "inside"),
            Place("the midnight bakery", "inside"),
            Place("the quiet workshop", "inside"),
            Place("the sleepy harbor", "around"),
            Place("the hillside café", "at"),
            Place("the old tram depot", "inside"),
        ]

        self.activities = [
            Activity("repairing", "repaired", "repair"),
            Activity("studying", "studied", "study"),
            Activity("collecting", "collected", "collect"),
            Activity("mapping", "mapped", "map"),
            Activity("sketching", "sketched", "sketch"),
            Activity("researching", "researched", "research"),
            Activity("composing", "composed", "compose"),
            Activity("cooking", "cooked", "cook"),
            Activity("rehearsing", "rehearsed", "rehearse"),
            Activity("teaching", "taught", "teach"),
            Activity("experimenting", "experimented", "experiment"),
            Activity("restoring", "restored", "restore"),
            Activity("explaining", "explained", "explain"),
            Activity("debating", "debated", "debate"),
            Activity("navigating", "navigated", "navigate"),
        ]
        
        self.people = [
            "a wizard", "a pirate", "a robot", "a ghost", "a time traveler", "a detective",
            "a chef", "a librarian", "a gardener", "a blacksmith", "a cartographer",
            "a bard", "a knight", "a scientist", "an artist", "a merchant", "a spy",
            "a talking squirrel", "a sentient toaster", "a very confused duck",
            "a retired superhero", "a professional napper", "a part-time dragon",
            "a freelance ninja", "a hobbyist alchemist", "an amateur detective",
            "a reluctant hero", "an enthusiastic sidekick", "a grumpy gnome"
        ]
        
        self.emotions = [
            "happy", "sad", "confused", "excited", "bored", "curious", "nervous",
            "proud", "embarrassed", "surprised", "disappointed", "hopeful",
            "frustrated", "amused", "terrified", "delighted", "suspicious",
            "nostalgic", "optimistic", "pessimistic", "indifferent", "ecstatic",
            "melancholy", "bewildered", "content", "anxious", "gleeful", "grumpy"
        ]
        
        self.intros = [
            "Earlier today",
            "Apparently",
            "Rumor has it",
            "For reasons I can't explain",
            "Just between us",
            "Out of nowhere",
            "When nobody was looking",
        ]

        self.observations = [
            "the entire moment felt {emotion}",
            "the air kept turning {emotion}",
            "it left everyone surprisingly {emotion}",
            "we all wound up oddly {emotion}",
            "the silence turned distinctly {emotion}",
            "everybody nearby went a little {emotion}",
            "I couldn't help feeling {emotion}",
        ]
        
        # Sentence templates with placeholders
        self.templates = [
            "{intro}, {subject} was {activity_gerund} with {thing} {place_setting}, and {observation}.",
            "I bumped into {subject} {place_setting} right after they {activity_past} {thing}; {observation}.",
            "Rumor has it {subject} convinced {companion} to {activity_infinitive} {thing} {place_setting}, which left them both {emotion}.",
            "Whenever we're {place_setting}, {subject} insists on {activity_gerund} beside {thing}, and it always feels {emotion}.",
            "{subject} asked {companion} to help {activity_infinitive} {thing} {place_setting}, and the plan somehow turned out {emotion}.",
            "{intro}, {subject} quietly {activity_past} {thing} {place_setting} while {companion} took notes, and the whole room went {emotion}.",
            "Back when we visited {place_plain}, {subject} kept {activity_gerund} with {companion} until {thing} finally cooperated, and that memory remains {emotion}.",
            "People still talk about how {subject} {activity_past} {thing} {place_setting} while {companion} narrated the whole thing, leaving the crowd {emotion}.",
            "On the way to {place_plain}, {subject} insisted we {activity_infinitive} with {thing}, and somehow it made everyone {emotion}.",
            "{intro}, {subject} reserved {place_plain} just so they could {activity_infinitive} {thing}, and honestly everyone stayed {emotion} about it.",
        ]
        
        # Track usage to balance variety
        self.sentence_usage = {}
        self.recent_sentences = deque(maxlen=8)
    
    def _generate_sentence(self) -> str:
        """Generate a random sentence using templates and word lists."""
        template = random.choice(self.templates)
        activity = random.choice(self.activities)
        place = random.choice(self.places)
        emotion = random.choice(self.emotions)
        subject = random.choice(self.people)
        companion = random.choice(self.people)
        if companion == subject and len(self.people) > 1:
            alternatives = [p for p in self.people if p != subject]
            companion = random.choice(alternatives)

        data = {
            "intro": random.choice(self.intros),
            "subject": subject,
            "companion": companion,
            "thing": random.choice(self.things),
            "emotion": emotion,
            "observation": random.choice(self.observations).format(emotion=emotion),
            "place_setting": place.describe(),
            "place_plain": place.name,
            "activity_gerund": activity.gerund,
            "activity_past": activity.past,
            "activity_infinitive": activity.infinitive,
        }
        return template.format(**data)
    
    def _select_sentence(self) -> str:
        """Pick a sentence biased toward least-used options and avoid recent repeats"""
        recent_set = set(self.recent_sentences)
        
        # Generate several candidates and pick the least used
        candidates = []
        for _ in range(5):  # Generate 5 candidates
            sentence = self._generate_sentence()
            if sentence not in recent_set:
                candidates.append(sentence)
        
        if not candidates:
            # If all recent, just pick any
            candidates = [self._generate_sentence() for _ in range(3)]
        
        # Track usage
        for sentence in candidates:
            self.sentence_usage.setdefault(sentence, 0)
        
        # Pick the least used candidate
        min_usage = min(self.sentence_usage[sentence] for sentence in candidates)
        least_used = [s for s in candidates if self.sentence_usage[s] == min_usage]
        selected = random.choice(least_used)
        
        self.sentence_usage[selected] = self.sentence_usage.get(selected, 0) + 1
        self.recent_sentences.append(selected)
        
        return selected
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Occasionally generate random sentences"""
        now = time.time()
        
        # Update last activity for this channel
        if channel not in self.last_activity:
            self.last_activity[channel] = now
        
        time_since_activity = now - self.last_activity[channel]
        self.last_activity[channel] = now
        
        # Calculate dynamic chance based on chat activity
        base_chance = 0.015
        if time_since_activity > 600: chance = 0.25
        elif time_since_activity > 300: chance = 0.10
        elif time_since_activity > 120: chance = 0.05
        else: chance = base_chance
        
        # Check for random sentence generation
        if (now - self.last_sentence > self.min_interval and random.random() < chance):
            sentence = self._select_sentence()
            await bot.privmsg(channel, sentence)
            self.last_sentence = now
            logging.debug(f"Generated random sentence in {channel} (quiet for {time_since_activity:.0f}s, chance was {chance*100:.1f}%): {sentence}")
            return True
        
        # Check for direct sentence requests
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        
        for bot_name in bot_names:
            if f"{bot_name} sentence" in message.lower() or f"{bot_name}, sentence" in message.lower():
                sentence = self._select_sentence()
                await bot.privmsg(channel, sentence)
                self.last_sentence = now
                return True
        
        return False
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        return False
    
    async def handle_join(self, bot, nick: str, channel: str):
        pass
    
    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        pass
