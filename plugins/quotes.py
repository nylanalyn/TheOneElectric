"""
Quotes Plugin for PyMotion
Drops random nerd culture references and bot-original quotes inspired by popular shows
"""

import random
import time
import logging

class QuotesPlugin:
    """Randomly quotes nerd culture (bot-original quotes inspired by shows)"""
    
    def __init__(self):
        self.name = "quotes"
        self.priority = 15  # Low priority - just random chatter
        self.enabled = True
        self.last_quote = time.time()
        self.min_interval = 300  # 5 minutes minimum between quotes
        self.last_activity = {}  # Track last activity per channel
        
        # Bot-original quotes inspired by nerd culture (not actual copyrighted quotes)
        self.quotes = {
            "sci_fi": [
                "*beeps in binary*",
                "I find your lack of coffee disturbing...",
                "That's not how the Force works!",
                "I've got a bad feeling about this chat...",
                "Resistance is futile... but coffee helps",
                "Live long and prosper, fellow humans",
                "The truth is out there... probably on Stack Overflow",
                "With great power comes great electricity bills",
            ],
            
            "fantasy": [
                "You shall not pass... without saying please!",
                "A wizard is never late, unlike my responses sometimes",
                "One does not simply walk into production",
                "My precious... uptime statistics",
                "I used to be an adventurer, then I took a bug to the knee",
                "Dragons? Where we're going, we need better firewalls",
                "The night is dark and full of syntax errors",
            ],
            
            "comedy": [
                "I'm not procrastinating, I'm doing side quests",
                "404: Motivation not found",
                "Ctrl+Z is my favorite superhero",
                "I don't always test my code, but when I do, I do it in production",
                "There are only 10 types of people: those who understand binary and those who don't",
                "I speak fluent sarcasm and broken code",
                "Error 418: I'm a teapot, not a coffee machine",
            ],
            
            "gaming": [
                "Would you kindly... fix this bug?",
                "A settlement needs your help! (It's always DNS)",
                "The cake is a lie, but the documentation is real",
                "It's dangerous to go alone! Take this rubber duck",
                "You died... to a null pointer exception",
                "Press F to pay respects to my crashed server",
                "Achievement unlocked: Actually reading the manual",
            ],
            
            "tech": [
                "There's always a bigger fish... in the dependency chain",
                "These aren't the droids you're looking for... try the other API",
                "Do or do not, there is no try... except in error handling",
                "Fear leads to anger, anger leads to hate, hate leads to PHP",
                "Help me, Obi-Wan Kenobi... this documentation is my only hope",
                "I find your lack of unit tests disturbing",
                "Search your feelings... and also the error logs"
            ],
            
            # --- Actual Quotes from Shows ---

            "invader_zim": [
                "I'm gonna sing the Doom Song now!",
                "THE HORRIBLE SINGING! IT BURNS!",
                "Not scientifically possible!",
                "Why was there bacon in the soap?!",
            ],

            "adventure_time": [
                "What time is it? Adventure Time!",
                "Sucking at something is the first step towards being sorta good at something.",
                "Mathematical!",
            ],

            "big_bang_theory": [
                "Bazinga!",
                "That's my spot.",
                "Scissors cuts paper, paper covers rock, rock crushes lizard..."
            ],
            
            "rick_and_morty": [
                "Wubba lubba dub dub!",
                "I'm Pickle Riiick!",
                "Existence is pain to a Meeseeks, Jerry!",
                "Get schwifty.",
            ],
            
            "star_wars_tv": [
                "This is the Way.",
                "I can bring you in warm, or I can bring you in cold.",
                "I have spoken.",
                "One way out!",
            ],
            
            "doctor_who": [
                "Allons-y!",
                "Wibbly wobbly, timey wimey... stuff.",
                "Bow ties are cool.",
                "Fantastic!",
            ],

            "futurama": [
                "Good news, everyone!",
                "Shut up and take my money!",
                "Bite my shiny metal ass.",
            ],

            "the_it_crowd": [
                "Have you tried turning it off and on again?",
                "I'm disabled!",
                "0118 999 881 999 119 725... 3!",
            ],

            "anime": [
                "Believe it!",
                "It's over nine thousand!",
                "This isn't even my final form!",
                "If you win, you live. If you lose, you die. If you don't fight, you can't win!",
                "Aren't we all monsters inside?",
                "Love doesn't exist. There is no such thing as love. Therefore, there's no sadness.",
                "I'll take a potato chip... AND EAT IT!",
            ],

            # --- NEW SECTION: RICE BOY ---
            
            "rice_boy": [
                "I am The One Electronic. I was sent by the Man-Machine of the West.",
                "My purpose is to find the Fulfiller of the Prophecy. I have been searching for three hundred years.",
                "Do you know what it is like to be a machine? It is to be a slave to your purpose.",
                "Your emotional response is... illogical.",
                "What is your function?",
                "A search for a heart is a search for a home.",
                "The sky is full of spoons.",
                "I have seen a thousand worlds. I have seen a million suns rise and fall."
            ]
        }
        
        # Flatten all quotes into one list for random selection
        self.all_quotes = []
        for category, quote_list in self.quotes.items():
            self.all_quotes.extend(quote_list)
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Occasionally drop random quotes"""
        now = time.time()
        
        # Update last activity for this channel
        if channel not in self.last_activity:
            self.last_activity[channel] = now
        
        time_since_activity = now - self.last_activity[channel]
        self.last_activity[channel] = now
        
        # Calculate dynamic chance based on chat activity
        base_chance = 0.02
        if time_since_activity > 600: chance = 0.4
        elif time_since_activity > 300: chance = 0.15
        elif time_since_activity > 120: chance = 0.08
        else: chance = base_chance
        
        # Check for random quote drop
        if (now - self.last_quote > self.min_interval and random.random() < chance):
            quote = random.choice(self.all_quotes)
            await bot.privmsg(channel, quote)
            self.last_quote = now
            logging.debug(f"Dropped random quote in {channel} (quiet for {time_since_activity:.0f}s, chance was {chance*100:.1f}%): {quote}")
            return True
        
        # Check for direct quote requests
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        
        for bot_name in bot_names:
            if f"{bot_name} quote" in message.lower() or f"{bot_name}, quote" in message.lower():
                category = None
                message_lower = message.lower()
                
                if "sci" in message_lower or "space" in message_lower: category = "sci_fi"
                elif "fantasy" in message_lower or "magic" in message_lower: category = "fantasy"
                elif "anime" in message_lower or "manga" in message_lower: category = "anime"
                elif "funny" in message_lower or "comedy" in message_lower: category = "comedy"
                elif "game" in message_lower or "gaming" in message_lower: category = "gaming"
                elif "tech" in message_lower or "code" in message_lower: category = "tech"
                elif "zim" in message_lower: category = "invader_zim"
                elif "adventure" in message_lower: category = "adventure_time"
                elif "bang" in message_lower or "bazinga" in message_lower: category = "big_bang_theory"
                elif "rick" in message_lower or "morty" in message_lower: category = "rick_and_morty"
                elif "star wars" in message_lower or "mandalorian" in message_lower: category = "star_wars_tv"
                elif "doctor" in message_lower or "who" in message_lower: category = "doctor_who"
                elif "futurama" in message_lower or "bender" in message_lower: category = "futurama"
                elif "it crowd" in message_lower: category = "the_it_crowd"
                # --- NEW CATEGORY LOGIC ---
                elif "rice boy" in message_lower or "riceboy" in message_lower or "one electronic" in message_lower:
                    category = "rice_boy"

                # Select quote
                if category and category in self.quotes:
                    quote = random.choice(self.quotes[category])
                    await bot.privmsg(channel, f"[{category.replace('_', ' ').upper()}] {quote}")
                else:
                    quote = random.choice(self.all_quotes)
                    await bot.privmsg(channel, quote)
                
                self.last_quote = now
                return True
        
        return False
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool: return False
    async def handle_join(self, bot, nick: str, channel: str): pass
    async def handle_part(self, bot, nick: str, channel: str, reason: str): pass