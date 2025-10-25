"""
Quotes Plugin for PyMotion
Drops random nerd culture references and bot-original quotes inspired by popular shows
"""

import random
import time
import logging
from collections import deque

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
                "May the Force be with you.",
                "I find your lack of faith disturbing.",
                "I've got a bad feeling about this.",
                "Live long and prosper.",
                "The needs of the many outweigh the needs of the few.",
                "I'm sorry, Dave. I'm afraid I can't do that.",
                "I'll be back.",
                "There is no spoon.",
            ],
            
            "fantasy": [
                "You shall not pass!",
                "A wizard is never late, nor is he early. He arrives precisely when he means to.",
                "One Ring to rule them all, One Ring to find them.",
                "My precious.",
                "Winter is coming.",
                "Valar morghulis.",
                "When you play the game of thrones, you win or you die.",
                "I am fire. I am death.",
            ],
            
            "comedy": [
                "I'm not superstitious, but I am a little stitious.",
                "That's what she said.",
                "No soup for you!",
                "We were on a break!",
                "It's just a flesh wound.",
                "How you doin'?",
                "I want to go to there.",
                "This is fine.",
            ],
            
            "gaming": [
                "Would you kindly?",
                "The cake is a lie.",
                "It's dangerous to go alone! Take this.",
                "Finish him!",
                "War. War never changes.",
                "Stay awhile and listen.",
                "Do a barrel roll!",
                "You have died of dysentery.",
            ],
            
            "tech": [
                "Talk is cheap. Show me the code.",
                "Any sufficiently advanced technology is indistinguishable from magic.",
                "Stay hungry. Stay foolish.",
                "Programs must be written for people to read, and only incidentally for machines to execute.",
                "Premature optimization is the root of all evil.",
                "If debugging is the process of removing software bugs, then programming must be the process of putting them in.",
                "Never trust a computer you can't throw out a window.",
                "To err is human, but to really foul things up you need a computer."
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
                "I am The One Electric. I was sent by the Man-Machine of the West.",
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
        
        # Track usage to balance variety
        self.quote_usage = {quote: 0 for quote in self.all_quotes}
        self.recent_global = deque(maxlen=10)
        self.recent_by_category = {category: deque(maxlen=3) for category in self.quotes}
    
    def _select_quote(self, source_list, category: str = None) -> str:
        """Pick a quote biased toward least-used options and avoid recent repeats."""
        if not source_list:
            return ""
        
        recent_set = set(self.recent_global)
        if category and category in self.recent_by_category:
            recent_set |= set(self.recent_by_category[category])
        
        candidates = [quote for quote in source_list if quote not in recent_set]
        if not candidates:
            candidates = list(source_list)
        
        for quote in candidates:
            self.quote_usage.setdefault(quote, 0)
        
        min_usage = min(self.quote_usage[quote] for quote in candidates)
        least_used = [quote for quote in candidates if self.quote_usage[quote] == min_usage]
        quote = random.choice(least_used)
        self.quote_usage[quote] = self.quote_usage.get(quote, 0) + 1
        
        if category and category in self.recent_by_category:
            self.recent_by_category[category].append(quote)
        self.recent_global.append(quote)
        return quote
    
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
            quote = self._select_quote(self.all_quotes)
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
                    quote = self._select_quote(self.quotes[category], category)
                    await bot.privmsg(channel, f"[{category.replace('_', ' ').upper()}] {quote}")
                else:
                    quote = self._select_quote(self.all_quotes)
                    await bot.privmsg(channel, quote)
                
                self.last_quote = now
                return True
        
        return False
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool: return False
    async def handle_join(self, bot, nick: str, channel: str): pass
    async def handle_part(self, bot, nick: str, channel: str, reason: str): pass
