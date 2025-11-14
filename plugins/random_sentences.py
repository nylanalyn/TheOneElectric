"""
Random Sentences Plugin for PyMotion
Generates random sentences using templates with placeholders
"""

import random
import time
import logging
from collections import deque

class RandomSentencesPlugin:
    """Generates random sentences using templates with placeholders"""
    
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
            "the abandoned library", "the enchanted forest", "the bustling marketplace",
            "the ancient ruins", "the underground cave", "the floating island",
            "the clockwork city", "the misty mountains", "the crystal desert",
            "the forgotten temple", "the rainbow bridge", "the whispering woods",
            "the bottom of a well", "the back of a cupboard", "under the sofa",
            "in the fridge", "behind the shed", "atop a very tall tree",
            "inside a hollow log", "buried in the garden", "stuck in a vending machine",
            "floating in a puddle", "wedged between couch cushions", "in the pocket of last year's coat"
        ]
        
        self.verbs = [
            "danced", "sang", "argued", "negotiated", "played chess", "had a picnic",
            "discussed philosophy", "shared secrets", "told jokes", "debated politics",
            "exchanged recipes", "compared collections", "planned heists", "wrote poetry",
            "built a fort", "organized a protest", "started a band", "opened a bakery",
            "invented a language", "discovered gravity", "rearranged the furniture",
            "tried to bake a cake", "attempted synchronized swimming", "practiced interpretive dance",
            "had a staring contest", "played hide and seek", "told ghost stories", 
            "made friendship bracelets", "learned to juggle", "started a book club"
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
        
        # Sentence templates with placeholders
        self.templates = [
            "I found {thing} at {place}. Should never have {verb} with it.",
            "Yesterday I met {person} who was feeling {emotion}. We ended up {verb} together.",
            "If you ever find {thing} in {place}, be careful not to {verb}.",
            "{Person} told me they once found {thing} while {verb} in {place}.",
            "I wonder what would happen if I {verb} with {thing} from {place}.",
            "Remember that time {person} tried to {verb} with {thing}? It was {emotion}.",
            "I'm feeling {emotion} about {thing} I discovered in {place}.",
            "{Person} and I are planning to {verb} using {thing} we found at {place}.",
            "Never trust {person} who wants to {verb} with {thing} from {place}.",
            "The secret to {verb} is having the right {thing} and being in {place}.",
            "I once saw {person} {verb} with {thing} in {place}. It was {emotion}.",
            "If I had {thing} from {place}, I would definitely {verb} with {person}.",
            "{Person} claims that {verb} with {thing} makes them feel {emotion}.",
            "I'm not sure why, but {thing} from {place} always makes me want to {verb}.",
            "The legend says that {person} will {verb} with {thing} when they find {place}.",
            "I feel {emotion} whenever I think about {verb} with {thing} in {place}.",
            "{Person} taught me that {verb} requires {thing} and the right {place}.",
            "I dreamt that {person} and I were {verb} with {thing} at {place}.",
            "The best part of {place} is finding {thing} and then {verb}.",
            "{Person} says that {verb} with {thing} in {place} is {emotion}."
        ]
        
        # Track usage to balance variety
        self.sentence_usage = {}
        self.recent_sentences = deque(maxlen=8)
    
    def _generate_sentence(self) -> str:
        """Generate a random sentence using templates and word lists"""
        template = random.choice(self.templates)
        
        # Capitalize person if it's at the start of sentence
        if template.startswith("{person}"):
            person = random.choice(self.people).capitalize()
        else:
            person = random.choice(self.people)
        
        # Fill placeholders
        sentence = template.format(
            thing=random.choice(self.things),
            place=random.choice(self.places),
            verb=random.choice(self.verbs),
            person=person,
            emotion=random.choice(self.emotions),
            Person=random.choice(self.people).capitalize()  # For capitalized versions
        )
        
        return sentence
    
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