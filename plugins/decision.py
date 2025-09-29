"""
Decision Plugin for PyMotion
Helps make important life decisions through highly scientific coin flips and dice rolls
"""

import random
import re

class DecisionPlugin:
    """Flip coins, roll dice, and make terrible decisions"""
    
    def __init__(self):
        self.name = "decision"
        self.priority = 55
        self.enabled = True
        
        # Coin flip outcomes
        self.coin_normal = ["Heads!", "Tails!"]
        
        # Rare coin disasters (1% chance)
        self.coin_disasters = [
            "*POOF!* What the heck? Coin just disappeared whilst in the air!",
            "*coin lands on its edge* ...well that's inconclusive",
            "*coin splits in half mid-flip* I think that's a maybe?",
            "*coin transforms into a butterfly and flies away*",
            "*coin phases through the floor into another dimension*",
            "*coin gets intercepted by a passing bird*",
            "*coin explodes into confetti* ...was that a yes?",
            "*coin refuses to land* It's just... hovering there. Spinning.",
            "*quantum superposition detected* The coin is both heads AND tails!",
            "*coin lands on heads, then flips itself to tails* Make up your mind, coin!"
        ]
        
        # Rare third option responses (2% chance)
        self.third_options = [
            "I'm thinking neither option, actually",
            "How about... *neither*?",
            "Plot twist: Do something completely different!",
            "My sensors indicate the correct answer is: None of the above",
            "Neither. Next question.",
            "I choose chaos. Do both at the same time!",
            "Actually, flip a coin to decide between those two",
            "The universe suggests you avoid both options",
            "I'm getting strong 'neither' vibes from this decision",
            "Counter-proposal: Don't do either of those things",
            "My highly scientific analysis says: Run away from both options",
            "Neither! And I'm not explaining why.",
            "The correct answer is actually option C: Panic",
            "Both options are terrible. I choose violence. 🥊"
        ]
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Handle decision-making commands"""
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        
        for bot_name in bot_names:
            # Coin flip
            if re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\b(flip|toss)\s+(a\s+)?coin', message):
                await self.flip_coin(bot, channel, nick)
                return True
            
            # Dice roll - matches "roll dice", "roll a die", "roll 2d6", etc.
            dice_match = re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\broll\s+(?:a\s+)?(?:(?:(\d+)d(\d+))|(?:dice?|die))', message)
            if dice_match:
                # Check if they specified XdY format
                if dice_match.group(1) and dice_match.group(2):
                    num_dice = int(dice_match.group(1))
                    num_sides = int(dice_match.group(2))
                else:
                    # Default to 1d6
                    num_dice = 1
                    num_sides = 6
                
                await self.roll_dice(bot, channel, nick, num_dice, num_sides)
                return True
            
            # This or that decision
            # Matches: "should I X or Y", "do I X or Y", "X or Y?"
            this_or_that = re.search(rf'(?i)\b{re.escape(bot_name)}\b.*(?:should|do|shall)\s+(?:I|we)\s+(.+?)\s+or\s+(.+?)[\?\.!]*$', message)
            if this_or_that:
                option1 = this_or_that.group(1).strip()
                option2 = this_or_that.group(2).strip()
                await self.choose_option(bot, channel, nick, option1, option2)
                return True
        
        return False
    
    async def flip_coin(self, bot, channel: str, nick: str):
        """Flip a coin with rare disasters"""
        # 1% chance of disaster
        if random.random() < 0.01:
            result = random.choice(self.coin_disasters)
            await bot.action(channel, f"flips a coin for {nick}...")
            import asyncio
            await asyncio.sleep(1)
            await bot.privmsg(channel, result)
        else:
            result = random.choice(self.coin_normal)
            await bot.action(channel, f"flips a coin for {nick}...")
            import asyncio
            await asyncio.sleep(0.8)
            await bot.privmsg(channel, result)
    
    async def roll_dice(self, bot, channel: str, nick: str, num_dice: int, num_sides: int):
        """Roll dice with reasonable limits"""
        # Sanity checks
        if num_dice < 1 or num_dice > 100:
            await bot.privmsg(channel, f"{nick}: Let's keep it between 1 and 100 dice, okay?")
            return
        
        if num_sides < 2 or num_sides > 1000:
            await bot.privmsg(channel, f"{nick}: Dice sides must be between 2 and 1000!")
            return
        
        # Roll the dice
        rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
        total = sum(rolls)
        
        # Format the response
        if num_dice == 1:
            await bot.action(channel, f"rolls a d{num_sides} for {nick}: {rolls[0]}")
        elif num_dice <= 10:
            # Show individual rolls for small amounts
            rolls_str = ", ".join(str(r) for r in rolls)
            await bot.action(channel, f"rolls {num_dice}d{num_sides} for {nick}: [{rolls_str}] = {total}")
        else:
            # Just show total for large amounts
            await bot.action(channel, f"rolls {num_dice}d{num_sides} for {nick}: Total = {total}")
    
    async def choose_option(self, bot, channel: str, nick: str, option1: str, option2: str):
        """Choose between two options, with rare third option"""
        # 2% chance of rejecting both options
        if random.random() < 0.02:
            response = random.choice(self.third_options)
            await bot.privmsg(channel, f"{nick}: {response}")
        else:
            # Choose one of the two options
            choice = random.choice([option1, option2])
            await bot.privmsg(channel, f"{nick}: {choice}")
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        """Handle /me actions - not used by this plugin"""
        return False
    
    async def handle_join(self, bot, nick: str, channel: str):
        """Handle user joins - not used by this plugin"""
        pass
    
    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        """Handle user parts - not used by this plugin"""
        pass
