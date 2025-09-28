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
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        if not message.endswith('?'):
            return False
        
        # Check if bot is mentioned (including aliases)
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        bot_mentioned = any(bot_name in message.lower() for bot_name in bot_names)
        
        # Only respond sometimes and if bot is mentioned or question seems general
        if not bot_mentioned and random.random() > 0.2:  # 20% chance for general questions
            return False
        
        if bot_mentioned or random.random() < 0.3:  # 30% chance
            if re.search(r'(?i)\b(is|are|will|can|could|should|would|do|does|did)\b', message):
                response = random.choice(self.yes_no_responses)
            elif re.search(r'(?i)\bwhat\b', message):
                response = random.choice(self.what_responses)
            elif re.search(r'(?i)\bwho\b', message):
                response = random.choice(self.who_responses)
            else:
                response = random.choice(self.yes_no_responses)
            
            await bot.privmsg(channel, f"{nick}: {response}")
            return True
        
        return False
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        return False
    
    async def handle_join(self, bot, nick: str, channel: str):
        pass
    
    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        pass
