"""
Questions Plugin for PyMotion
Responds to questions with silly answers
"""

import random
import re

class QuestionPlugin:
    """Responds to questions"""
    
    def __init__(self):
        self.name = "questions"
        self.priority = 35
        self.enabled = True

        self.yes_no_responses = [
            "Yes!", "No!", "Maybe!", "Definitely!", "Absolutely not!",
            "I think so!", "Probably not...", "Ask again later!",
            "Signs point to yes!", "Don't count on it!", "Most likely!",
            "Cannot predict now!", "Yes, definitely!", "Very doubtful!"
        ]

        self.what_responses = [
            "That's a mystery!", "Beats me!", "Good question!",
            "I have no idea!", "Your guess is as good as mine!",
            "Something interesting, I'm sure!", "Nobody knows!",
            "The answer is 42!", "That would be telling!"
        ]

        self.who_responses = [
            "Someone special!", "A person!", "Nobody important!",
            "Your mom!", "The person behind you!", "A mystery person!",
            "Someone you know!", "Not me!", "The usual suspect!"
        ]

        # How many responses
        self.how_many_responses = [
            "3! No, wait! 4. NO! I lost 2... so 2. 1?",
            "Seven! Definitely seven. Or was it eight?",
            "All of them! *counts on fingers* Wait, none of them!",
            "42! No! 17! Actually... *shrugs* maybe 5?",
            "More than you! Less than... wait, what was the question?",
            "Eleventy-seven! Is that a number?",
            "Let me count... 1, 2, skip a few... 99, 100!",
            "Not enough! Or too many? *panics* I don't know!"
        ]

        # Favorite/which responses
        self.favorite_responses = [
            "Cat! No! French fries! No! Can I ask my master?",
            "The purple one! Wait, the shiny one! *spins*",
            "Uh... *sweats* ...yes?",
            "All of them! None of them! The one in the middle!",
            "That's like asking me to pick a favorite electron!",
            "The one that goes 'beep'! Or was it 'boop'?",
            "I plead the fifth! Wait, what's a fifth?",
            "Ooh! Ooh! The... uh... *forgets* ...what were we talking about?"
        ]

        # When/where responses
        self.when_where_responses = [
            "Tuesday! No, wait! Next week! Or was it last year?",
            "Over there! *points vaguely in all directions*",
            "At precisely... *checks nonexistent watch* ...time o'clock!",
            "In the place! You know, THE place!",
            "Soon! Or later! Definitely one of those!",
            "Behind you! No, in front! To the left! *spins*",
            "When the moon is full and the chickens dance!",
            "Right here! No, there! Everywhere? Nowhere?"
        ]

        # Why/how responses
        self.why_how_responses = [
            "Because reasons! Very important reasons!",
            "With my hands! Or feet! Or... wings? Do I have wings?",
            "Very carefully! Or not at all! One of those!",
            "The universe works in mysterious ways!",
            "Magic! It's always magic! Or science! One of those!",
            "By pressing the buttons! All the buttons!",
            "Because someone told me to! Or didn't! I forget!",
            "Through the power of friendship! And explosions!"
        ]
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        if not message.endswith('?'):
            return False

        # Check if bot is mentioned (including aliases)
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        bot_mentioned = any(bot_name in message.lower() for bot_name in bot_names)

        # Always respond if bot is mentioned, otherwise only 10% of the time
        if not bot_mentioned and random.random() > 0.1:
            return False

        # Choose response based on question type (order matters - check specific types first)
        if re.search(r'(?i)\bhow many\b', message):
            response = random.choice(self.how_many_responses)
        elif re.search(r'(?i)\bhow much\b', message):
            response = random.choice(self.how_many_responses)
        elif re.search(r'(?i)\b(favorite|favourite|which)\b', message):
            response = random.choice(self.favorite_responses)
        elif re.search(r'(?i)\bwhen\b', message):
            response = random.choice(self.when_where_responses)
        elif re.search(r'(?i)\bwhere\b', message):
            response = random.choice(self.when_where_responses)
        elif re.search(r'(?i)\bwhy\b', message):
            response = random.choice(self.why_how_responses)
        elif re.search(r'(?i)\bhow\b', message):
            response = random.choice(self.why_how_responses)
        elif re.search(r'(?i)\bwho\b', message):
            response = random.choice(self.who_responses)
        elif re.search(r'(?i)\bwhat\b', message):
            response = random.choice(self.what_responses)
        elif re.search(r'(?i)\b(is|are|will|can|could|should|would|do|does|did)\b', message):
            response = random.choice(self.yes_no_responses)
        else:
            response = random.choice(self.yes_no_responses)

        await bot.privmsg(channel, f"{nick}: {response}")
        return True
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        return False
    
    async def handle_join(self, bot, nick: str, channel: str):
        pass
    
    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        pass
