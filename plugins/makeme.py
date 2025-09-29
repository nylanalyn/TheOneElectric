"""
Make Me Plugin for PyMotion
Craft things or transform people - it's ambiguous on purpose!
"""

import random
import re
import asyncio

class MakeMePlugin:
    """Handle 'make me a thing' commands with delightful ambiguity"""
    
    def __init__(self):
        self.name = "makeme"
        self.priority = 60
        self.enabled = True
        
        # Crafting responses (make/create an item)
        self.crafting_actions = [
            "carefully crafts {user} a fine {thing}",
            "forges {user} an exquisite {thing}",
            "constructs {user} a magnificent {thing}",
            "assembles {user} a premium {thing}",
            "whips up {user} a delightful {thing}",
            "conjures {user} a mystical {thing}",
            "3D prints {user} a high-quality {thing}",
            "lovingly handcrafts {user} a beautiful {thing}",
            "hastily slaps together {user} a mediocre {thing}",
            "summons from the abyss {user}'s very own {thing}"
        ]
        
        # Transformation responses (turn someone into something)
        self.transformation_spells = [
            "Blinga blonga! You're a {thing}",
            "Abracadabra! *poof* You're now a {thing}",
            "Alakazam! Behold, you are a {thing}",
            "Hocus pocus! *sparkles* You've become a {thing}",
            "Bibbidi-bobbidi-boo! You're a {thing} now",
            "Shazam! *flash of light* Welcome to being a {thing}",
            "Presto changeo! Say hello to your new life as a {thing}",
            "*mutters ancient incantation* ...and you're a {thing}",
            "By the power of random transformation, become a {thing}!",
            "*waves wand dramatically* Ta-da! One {thing}, as requested"
        ]
        
        # Refusal responses (5% chance)
        self.refusals = [
            "No.",
            "I don't think so.",
            "Hard pass.",
            "My union doesn't allow that kind of work.",
            "*shakes head* Not today.",
            "Ask someone else.",
            "That's above my pay grade.",
            "I refuse on principle.",
            "Nah.",
            "*pretends not to hear*",
            "Error 403: Forbidden",
            "My magic license expired, sorry.",
            "I'm on break.",
            "The warranty doesn't cover that.",
            "*crosses arms* Nope.",
            "I could, but I won't.",
            "Request denied. Next!",
            "That violates the Geneva Convention.",
            "My mom said I'm not allowed to.",
            "The spirits say no."
        ]
        
        # Misinterpretation responses (3% chance)
        self.misinterpretations = [
            "*makes you into an actual May* ...wait, that's not right",
            "*hands you a book titled 'How To Make A {thing}'* Here you go!",
            "*starts singing 'Make Me a {thing}' to the tune of your favorite song*",
            "Instructions unclear. *makes a {thing}* ...for myself",
            "Did you say bake you a {thing}? *turns on oven*",
            "Make? I thought you said BAKE! *pulls out flour*",
            "*Googles 'how to make a {thing}'* ...this looks complicated",
            "I heard 'fake you a {thing}' *starts printing counterfeit {thing}*",
            "*orders a {thing} from Amazon* ETA: 2-3 business days",
            "Make you? I barely know you!"
        ]
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Handle make me commands"""
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        
        for bot_name in bot_names:
            # Match "give X to Y" or "give Y an X"
            give_match = re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\bgive\s+(?:(\w+)\s+)?(?:a|an)?\s*(.+?)\s+to\s+(\w+)', message)
            if not give_match:
                # Try alternate pattern: "give Y X"
                give_match = re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\bgive\s+(\w+)\s+(?:a|an)?\s*(.+)', message)
                if give_match:
                    recipient = give_match.group(1)
                    thing = give_match.group(2).strip().rstrip('!?.,')
                    await self.give_thing(bot, channel, nick, recipient, thing)
                    return True
            else:
                # Pattern: "give [recipient] [thing] to [recipient]" or "give [thing] to [recipient]"
                if give_match.group(1):
                    # "give bob a cookie" format - group 1 is recipient, group 2 is thing
                    recipient = give_match.group(1)
                    thing = give_match.group(2).strip().rstrip('!?.,')
                else:
                    # "give a cookie to bob" format - group 2 is thing, group 3 is recipient
                    thing = give_match.group(2).strip().rstrip('!?.,')
                    recipient = give_match.group(3)
                
                await self.give_thing(bot, channel, nick, recipient, thing)
                return True
            
            # Match "make me a/an X" or just "make me X"
            make_match = re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\bmake\s+me\s+(?:a|an)?\s*(.+)', message)
            if make_match:
                thing = make_match.group(1).strip()
                
                # Don't process empty requests
                if not thing:
                    await bot.privmsg(channel, f"{nick}: Make you... what? You have to tell me what!")
                    return True
                
                # Remove trailing punctuation
                thing = thing.rstrip('!?.,')
                
                await self.make_thing(bot, channel, nick, thing)
                return True
        
        return False
    
    async def make_thing(self, bot, channel: str, nick: str, thing: str):
        """Process the make request with various outcomes"""
        
        # 5% chance of outright refusal
        if random.random() < 0.05:
            refusal = random.choice(self.refusals)
            await bot.privmsg(channel, f"{nick}: {refusal}")
            return
        
        # 3% chance of hilarious misinterpretation
        if random.random() < 0.03:
            misinterpretation = random.choice(self.misinterpretations).format(thing=thing)
            await bot.action(channel, misinterpretation)
            return
        
        # Choose between crafting (60%) and transformation (40%)
        if random.random() < 0.6:
            # Crafting path
            await bot.privmsg(channel, "OK!")
            await asyncio.sleep(0.5)
            
            action = random.choice(self.crafting_actions).format(user=nick, thing=thing)
            await bot.action(channel, action)
            
            # Occasional quality commentary (20% chance)
            if random.random() < 0.2:
                comments = [
                    "*chef's kiss* Perfect craftsmanship!",
                    "It's not much, but it's honest work.",
                    "That'll be $49.99 plus shipping.",
                    "*wipes sweat* That was tougher than expected.",
                    "Warranty not included.",
                    "Some assembly required.",
                    "Handle with care!",
                    "*stamps 'HANDMADE' label on it*",
                    "This is my best work yet!",
                    "I've outdone myself this time."
                ]
                await asyncio.sleep(0.8)
                await bot.privmsg(channel, random.choice(comments))
        
        else:
            # Transformation path
            spell = random.choice(self.transformation_spells).format(thing=thing)
            
            await bot.action(channel, "waves wand")
            await asyncio.sleep(1)
            await bot.privmsg(channel, spell)
            
            # Occasional transformation side-effects (15% chance)
            if random.random() < 0.15:
                side_effects = [
                    "*something went wrong* ...you also glow in the dark now",
                    "Side effects may include: existential dread",
                    "*checks spell book* ...that was permanent, by the way",
                    "Oops, you're also 3 inches taller now. My bad.",
                    "*transformation partially fails* ...you still have your original hands though",
                    "The spell will wear off in... *checks notes* ...never",
                    "*squints* Did you always have that extra arm?",
                    "Success! ...probably. Hard to tell.",
                    "That's covered by your transformation insurance, right?",
                    "*transformation complete* Please don't sue me."
                ]
                await asyncio.sleep(1)
                await bot.privmsg(channel, random.choice(side_effects))
    
    async def give_thing(self, bot, channel: str, giver: str, recipient: str, thing: str):
        """Give something to someone with occasional chaos"""
        
        # Check if trying to give to self
        if recipient.lower() == giver.lower():
            snarky_responses = [
                f"{giver}: You can just... keep it yourself?",
                f"{giver}: That's just called 'having' something.",
                "Instructions unclear. Created a paradox.",
                "*confused bot noises*",
                f"{giver}: Why don't you make it yourself and cut out the middleman?",
                "Error: Circular dependency detected.",
                f"{giver}: I'm not participating in whatever this is."
            ]
            await bot.privmsg(channel, random.choice(snarky_responses))
            return
        
        # Check if trying to give to the bot
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        if recipient.lower() in bot_names:
            bot_responses = [
                "For me? You shouldn't have! *accepts graciously*",
                "I don't have pockets, but thanks!",
                "*tries to eat it* ...I don't think I can process this",
                "Aww, you're too kind! *adds to collection*",
                "I'm not programmed to handle gifts. *malfunctions adorably*",
                "*stores in digital inventory* Item saved!",
                "That's very thoughtful! *files it under 'random stuff'*",
                "Thanks! This goes great with my other 47 {thing}s".format(thing=thing)
            ]
            await bot.privmsg(channel, random.choice(bot_responses))
            return
        
        # 7% chance of chaos/mishaps
        if random.random() < 0.07:
            mishaps = [
                "*attempts delivery* ...oh no, it broke",
                "*gives {recipient} the {thing}* Wait, that was supposed to go to someone else",
                "*trips and falls* The {thing} rolled under the couch, sorry",
                "*hands {recipient} a receipt* Your {thing} is on backorder",
                "*accidentally gives {recipient} a very similar but wrong {thing}*",
                "*delivery intercepted by a passing seagull*",
                "*teleportation error* The {thing} ended up in another dimension",
                "*gives {recipient} the {thing}* ...oh wait, this is a rental",
                "Shipping cost: One million dollars. Still want me to deliver?",
                "*{thing} spontaneously combusts during delivery* ...my bad"
            ]
            mishap = random.choice(mishaps).format(recipient=recipient, thing=thing)
            await bot.action(channel, mishap)
            return
        
        # 5% chance of refusal
        if random.random() < 0.05:
            refusals = [
                f"{giver}: Do it yourself, I'm busy.",
                f"{giver}: That sounds like a 'you' problem.",
                "I'm not a delivery service!",
                f"{giver}: My delivery union is on strike.",
                "*pretends not to hear*",
                f"{giver}: I charge $50 for deliveries.",
                "Ask me again later. Like, way later.",
                f"{giver}: I refuse on moral grounds.",
                "Delivery failed: Address not found in database."
            ]
            await bot.privmsg(channel, random.choice(refusals))
            return
        
        # Normal delivery (88% chance)
        delivery_actions = [
            "hands {recipient} a {thing}",
            "presents {recipient} with a lovely {thing}",
            "delivers a {thing} to {recipient}",
            "ceremoniously bestows upon {recipient} a {thing}",
            "tosses {recipient} a {thing}",
            "carefully places a {thing} in {recipient}'s hands",
            "materializes a {thing} and gives it to {recipient}",
            "summons a {thing} and hands it to {recipient}",
            "slides a {thing} across the table to {recipient}",
            "airdrop deploys a {thing} to {recipient}",
            "express delivers a {thing} to {recipient}",
            "ninja-delivers a {thing} to {recipient}",
            "teleports a {thing} directly to {recipient}"
        ]
        
        action = random.choice(delivery_actions).format(recipient=recipient, thing=thing)
        await bot.action(channel, action)
        
        # 15% chance of delivery commentary
        if random.random() < 0.15:
            comments = [
                "Handle with care!",
                "Signature required!",
                "That'll be... actually, it's on the house.",
                "*wipes sweat* Heavy package!",
                "Delivered fresh today!",
                "No returns or exchanges!",
                "*adds delivery to resume*",
                "Service with a smile! 😊",
                "Another satisfied customer!",
                "*stamps 'FRAGILE' on forehead*"
            ]
            await asyncio.sleep(0.7)
            await bot.privmsg(channel, random.choice(comments))
    
    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        """Handle /me actions - not used by this plugin"""
        return False
    
    async def handle_join(self, bot, nick: str, channel: str):
        """Handle user joins - not used by this plugin"""
        pass
    
    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        """Handle user parts - not used by this plugin"""
        pass
