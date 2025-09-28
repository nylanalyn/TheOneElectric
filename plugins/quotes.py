"""
Quotes Plugin for PyMotion
Drops random nerd culture references and bot-original quotes inspired by popular shows.
Now includes actual quotes from various TV shows and anime.
"""

import random
import time
import logging

class QuotesPlugin:
    """Randomly quotes nerd culture (bot-original and actual quotes from shows)"""
    
    def __init__(self):
        self.name = "quotes"
        self.priority = 15  # Low priority - just random chatter
        self.enabled = True
        self.last_quote = time.time()
        self.min_interval = 600  # 10 minutes minimum between quotes
        
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
            
            # --- New Section: Actual Quotes from Shows ---

            "invader_zim": [
                "I'm gonna sing the Doom Song now!",
                "THE HORRIBLE SINGING! IT BURNS!",
                "Not scientifically possible!",
                "I'm a mongoose! The deadliest mongoose of all!",
                "Why was there bacon in the soap?!",
                "I am ZIM!"
            ],

            "adventure_time": [
                "What time is it? Adventure Time!",
                "Sucking at something is the first step towards being sorta good at something.",
                "Mathematical!",
                "Oh my Glob!",
                "Responsibility demands sacrifice.",
                "Bacon pancakes, makin' bacon pancakes..."
            ],

            "big_bang_theory": [
                "Bazinga!",
                "That's my spot.",
                "One cries because one is sad. For example, I cry because others are stupid, and that makes me sad.",
                "It’s a Saturnalia miracle!",
                "Scissors cuts paper, paper covers rock, rock crushes lizard..."
            ],
            
            "rick_and_morty": [
                "Wubba lubba dub dub!",
                "And that's the way the news goes.",
                "I'm Pickle Riiick!",
                "Existence is pain to a Meeseeks, Jerry!",
                "Get schwifty.",
                "To live is to risk it all."
            ],
            
            "star_wars_tv": [
                "This is the Way.",
                "I can bring you in warm, or I can bring you in cold.",
                "I have spoken.",
                "I am on my way. On my way.",
                "One way out!",
                "I'd rather die trying to take them down than die giving them what they want."
            ],
            
            "doctor_who": [
                "Allons-y!",
                "Wibbly wobbly, timey wimey... stuff.",
                "Bow ties are cool.",
                "Fantastic!",
                "In 900 years of time and space, I've never met anyone who wasn't important."
            ],

            "futurama": [
                "Good news, everyone!",
                "Shut up and take my money!",
                "Bite my shiny metal ass.",
                "I don't want to live on this planet anymore.",
                "The spirit is willing, but the flesh is spongy and bruised."
            ],

            "the_it_crowd": [
                "Have you tried turning it off and on again?",
                "I'm disabled!",
                "I'll just put this over here, with the rest of the fire.",
                "0118 999 881 999 119 725... 3!",
                "People... what a bunch of bastards."
            ],

            "anime": [
                # Naruto
                "Believe it!",
                # Dragon Ball Z
                "It's over nine thousand!",
                "This isn't even my final form!",
                # Attack on Titan
                "If you win, you live. If you lose, you die. If you don't fight, you can't win!",
                "Dedicate your hearts! (Shinzou wo Sasageyo!)",
                # Elfen Lied
                "Aren't we all monsters inside?",
                # Devilman Crybaby
                "Love doesn't exist. There is no such thing as love. Therefore, there's no sadness.",
                # Existing quotes
                "I choose you, Random Number Generator!",
                "Notice me, senpai... I mean, admin",
                "I'll take a potato chip... AND EAT IT!",
                "This is the choice of Steins;Gate... and also my random function"
            ]
        }
        
        # Flatten all quotes into one list for random selection
        self.all_quotes = []
        for category, quote_list in self.quotes.items():
            self.all_quotes.extend(quote_list)
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Occasionally drop random quotes"""
        now = time.time()
        
        # Check if enough time has passed and we get lucky with the random chance
        if (now - self.last_quote > self.min_interval and 
            random.random() < 0.008):  # 0.8% chance per message
            
            quote = random.choice(self.all_quotes)
            await bot.privmsg(channel, quote)
            self.last_quote = now
            
            logging.debug(f"Dropped random quote in {channel}: {quote}")
            return True
        
        # Also respond to direct requests for quotes
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        
        for bot_name in bot_names:
            if f"{bot_name} quote" in message.lower() or f"{bot_name}, quote" in message.lower():
                category = None
                
                # Check if they want a specific category
                message_lower = message.lower()
                if "sci" in message_lower or "space" in message_lower:
                    category = "sci_fi"
                elif "fantasy" in message_lower or "magic" in message_lower:
                    category = "fantasy"
                elif "anime" in message_lower or "manga" in message_lower:
                    category = "anime"
                elif "funny" in message_lower or "comedy" in message_lower:
                    category = "comedy"
                elif "game" in message_lower or "gaming" in message_lower:
                    category = "gaming"
                elif "tech" in message_lower or "code" in message_lower:
                    category = "tech"
                # --- New category matching logic ---
                elif "zim" in message_lower:
                    category = "invader_zim"
                elif "adventure" in message_lower:
                    category = "adventure_time"
                elif "bang" in message_lower or "bazinga" in message_lower:
                    category = "big_bang_theory"
                elif "rick" in message_lower or "morty" in message_lower:
                    category = "rick_and_morty"
                elif "star wars" in message_lower or "mandalorian" in message_lower or "andor" in message_lower:
                    category = "star_wars_tv"
                elif "doctor" in message_lower or "who" in message_lower:
                    category = "doctor_who"
                elif "futurama" in message_lower or "bender" in message_lower:
                    category = "futurama"
                elif "it crowd" in message_lower:
                    category = "the_it_crowd"

                # Select quote from category or all quotes
                if category and category in self.quotes:
                    quote = random.choice(self.quotes[category])
                    # Format category name for display
                    display_category = category.replace("_", " ").title()
                    await bot.privmsg(channel, f"[{display_category}] {quote}")
                else:
                    quote = random.choice(self.all_quotes)
                    await bot.privmsg(channel, quote)
                
                self.last_quote = now
                return True
        
        return False
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        """Handle /me actions - not used by this plugin"""
        return False
    
    async def handle_join(self, bot, nick: str, channel: str):
        """Handle user joins - not used by this plugin"""
        pass
    
    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        """Handle user parts - not used by this plugin"""
        pass