"""
Stealth Plugin for PyMotion
Sneak attacks and stealth mechanics
"""

import random
import re
import time

class StealthPlugin:
    """Handle stealth mechanics and sneak attacks"""
    
    def __init__(self):
        self.name = "stealth"
        self.priority = 80  # High priority to set stealth state
        self.enabled = True
        
        # Track stealth state per channel
        self.stealth_state = {}  # {channel: {"hidden": bool, "method": str, "time": float}}
        
        # Ways to go into stealth
        self.stealth_methods = [
            "dives behind a conveniently placed cardboard box",
            "throws on an invisibility cloak and vanishes",
            "activates optical camouflage",
            "puts on a ninja outfit and melts into the shadows",
            "hides behind a houseplant",
            "disguises as a lamp in the corner",
            "crawls into a sleeping bag and becomes a suspicious lump",
            "puts on a fake mustache and sunglasses",
            "becomes one with the wallpaper",
            "activates chameleon mode",
            "hides under a desk like a scared intern",
            "puts on a ghillie suit made of ethernet cables",
            "transforms into a filing cabinet",
            "deploys holographic decoy and sneaks away",
            "activates thermoptic camouflage",
            "hides inside a server rack",
            "disguises as a very tall coffee mug",
            "becomes a potted plant",
            "activates stealth mode like a spaceship",
            "puts on a 'Hello My Name Is: NOT HERE' sticker",
            "hides behind the fourth wall",
            "becomes temporarily two-dimensional",
            "activates ninja vanish technique *poof*",
            "disguises as ambient room temperature",
            "hides in plain sight by being incredibly boring"
        ]
        
        # Ways to reveal when attacking
        self.reveal_methods = [
            "leaps out dramatically",
            "drops the invisibility cloak",
            "emerges from the shadows",
            "throws off the disguise",
            "materializes suddenly",
            "pops out like a jack-in-the-box",
            "reveals their position with a battle cry",
            "steps out from behind cover",
            "deactivates camouflage",
            "drops the ninja act",
            "abandons stealth for MAXIMUM CHAOS",
            "bursts forth with theatrical flair",
            "makes a grand entrance",
            "reveals themselves with a dramatic pose",
            "springs the trap",
            "initiates surprise attack protocol",
            "breaks cover with style",
            "announces themselves like a superhero",
            "drops the pretense",
            "goes loud and proud"
        ]
    
    def get_stealth_state(self, channel: str) -> dict:
        """Get stealth state for a channel"""
        if channel not in self.stealth_state:
            self.stealth_state[channel] = {
                "hidden": False,
                "method": "",
                "time": 0
            }
        return self.stealth_state[channel]
    
    def is_hidden(self, channel: str) -> bool:
        """Check if bot is currently hidden in this channel"""
        return self.get_stealth_state(channel)["hidden"]
    
    def get_stealth_method(self, channel: str) -> str:
        """Get current stealth method"""
        return self.get_stealth_state(channel)["method"]
    
    def set_stealth(self, channel: str, hidden: bool, method: str = ""):
        """Set stealth state"""
        state = self.get_stealth_state(channel)
        state["hidden"] = hidden
        state["method"] = method
        state["time"] = time.time()
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Handle stealth commands"""
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        
        for bot_name in bot_names:
            # Sneak command
            if re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\bsneak\b', message):
                if self.is_hidden(channel):
                    await bot.privmsg(channel, "I'm already hidden! *whispers from the shadows*")
                else:
                    method = random.choice(self.stealth_methods)
                    self.set_stealth(channel, True, method)
                    await bot.action(channel, method)
                    await bot.privmsg(channel, "*is now hidden*")
                return True
            
            # Reveal/unhide command
            if re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\b(reveal|unhide|come out|show yourself)\b', message):
                if not self.is_hidden(channel):
                    await bot.privmsg(channel, "I'm not hiding! I'm right here!")
                else:
                    reveal = random.choice(self.reveal_methods)
                    old_method = self.get_stealth_method(channel)
                    self.set_stealth(channel, False)
                    await bot.action(channel, f"{reveal}!")
                    await bot.privmsg(channel, f"*is no longer hidden* (was: {old_method})")
                return True
        
        return False
    
    async def handle_stealth_attack(self, bot, channel: str, action_description: str):
        """Handle revealing during an attack - called by other plugins"""
        if self.is_hidden(channel):
            reveal = random.choice(self.reveal_methods)
            old_method = self.get_stealth_method(channel)
            self.set_stealth(channel, False)
            
            # Dramatic stealth attack sequence
            await bot.action(channel, f"{reveal} from {old_method}!")
            await bot.privmsg(channel, "*SNEAK ATTACK!* 🥷")
            
            # Small pause for effect
            import asyncio
            await asyncio.sleep(0.5)
            
            return True  # Indicates this was a stealth attack
        return False  # Not hidden, normal attack
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        """Handle /me actions - not used by this plugin"""
        return False
    
    async def handle_join(self, bot, nick: str, channel: str):
        """Handle user joins - not used by this plugin"""
        pass
    
    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        """Handle user parts - not used by this plugin"""
        pass
