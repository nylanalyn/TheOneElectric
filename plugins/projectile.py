"""
Projectile Plugin for PyMotion
Fire random things at people with ridiculous devices
Mood-aware: channel mood affects firing flavor
"""

import asyncio
import random
import re

class ProjectilePlugin:
    """Fire things at people with various absurd devices"""

    def __init__(self):
        self.name = "projectile"
        self.priority = 65  # High priority to catch fire commands
        self.enabled = True

        # Launching devices/methods
        self.launchers = [
            "aims a trebuchet",
            "loads a cannon",
            "prepares a catapult",
            "charges up a railgun",
            "readies a slingshot",
            "primes a potato gun",
            "sets up a t-shirt cannon",
            "calibrates a nerf launcher",
            "activates a tennis ball machine",
            "deploys a medieval siege engine",
            "configures a confetti cannon",
            "powers up a leaf blower",
            "assembles a makeshift launcher",
            "cranks up a pitching machine",
            "loads a marshmallow gun",
            "prepares orbital bombardment",
            "summons a mystical projectile portal",
            "constructs an elaborate Rube Goldberg device",
            "commandeers a nearby vending machine",
            "repurposes a toaster as artillery"
        ]

        # Random projectiles for when they say "fire everything" or "fire something"
        self.random_projectiles = [
            "cheese", "rubber ducks", "glitter", "confetti", "marshmallows",
            "silly string", "foam darts", "water balloons", "ping pong balls",
            "banana peels", "cotton candy", "bubble wrap", "spaghetti",
            "rainbow sprinkles", "bouncy balls", "stress balls", "pool noodles",
            "paper airplanes", "rubber chickens", "googly eyes", "sticky notes",
            "bubble solution", "feathers", "packing peanuts", "jello",
            "whipped cream", "silly putty", "slime", "plastic spoons",
            "sock puppets", "fortune cookies", "rubber bands", "crayons",
            "disco balls", "emoji stickers", "temporary tattoos", "kazoos",
            "rubber stamps", "magic 8-balls", "fidget spinners", "slinkies",
            "whoopie cushions", "fake mustaches", "tiny umbrellas", "cheese puffs"
        ]

        # Dramatic effects/results
        self.effects = [
            "covers them in {projectile}",
            "completely drenches them with {projectile}",
            "buries them under a mountain of {projectile}",
            "paints them head-to-toe with {projectile}",
            "transforms them into a {projectile} sculpture",
            "creates a {projectile} explosion around them",
            "engulfs them in a cloud of {projectile}",
            "decorates them festively with {projectile}",
            "gives them a stylish {projectile} makeover",
            "turns them into the {projectile} champion",
            "makes them one with the {projectile}",
            "bestows upon them the blessing of {projectile}",
            "initiates them into the cult of {projectile}",
            "grants them temporary {projectile} powers",
            "encases them in a protective shell of {projectile}"
        ]

        # Special responses for firing at the bot
        self.self_defense = [
            "*dodges with matrix-like reflexes*",
            "*activates force field* Nice try!",
            "*teleports behind you* Nothing personnel, kid",
            "*reflects it back with a mirror*",
            "*catches it and eats it* Tasty!",
            "*transforms into a robot* DAMAGE: 0",
            "*becomes incorporeal* You can't hit what you can't touch!",
            "*pulls out an umbrella* I came prepared!",
            "*uses uno reverse card*",
            "*summons a black hole to absorb the attack*"
        ]

        # Mood flavor: high mood crowd excitement
        self.high_mood_crowd = [
            "*the crowd goes WILD!*",
            "*standing ovation from the audience*",
            "*fireworks go off*",
            "*air horns blare*",
            "*confetti rains from the ceiling*",
        ]

        # Mood flavor: low mood half-hearted
        self.low_mood_flavor = [
            "*fires halfheartedly*",
            "*doesn't even aim properly*",
            "*sighs and pulls the trigger*",
            "I guess we're doing this...",
            "*lackluster pew pew*",
        ]

    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Handle fire commands"""
        # Check if someone is trying to fire something
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]

        for bot_name in bot_names:
            # Pattern: "botnick fire <projectile> at <target>"
            fire_match = re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\bfire\s+(.+?)\s+at\s+(\w+)', message)
            if fire_match:
                projectile_raw = fire_match.group(1).strip()
                target = fire_match.group(2)

                # Handle special projectiles
                if projectile_raw.lower() in ['everything', 'something', 'anything', 'stuff']:
                    projectile = random.choice(self.random_projectiles)
                else:
                    projectile = projectile_raw

                await self.fire_at_target(bot, channel, nick, target, projectile)
                return True

            # Pattern: "botnick fire at <target>" (no projectile specified)
            fire_match_no_projectile = re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\bfire\s+at\s+(\w+)', message)
            if fire_match_no_projectile:
                target = fire_match_no_projectile.group(1)
                projectile = random.choice(self.random_projectiles)

                await self.fire_at_target(bot, channel, nick, target, projectile)
                return True

        return False

    async def fire_at_target(self, bot, channel: str, firer: str, target: str, projectile: str):
        """Execute the firing sequence"""

        # Don't fire at yourself (the person giving the command)
        if target.lower() == firer.lower():
            await bot.privmsg(channel, f"{firer}: You can't fire at yourself! That's just called 'eating'.")
            return

        # Special response if firing at the bot
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        if target.lower() in bot_names:
            defense = random.choice(self.self_defense)
            await bot.privmsg(channel, defense)
            return

        # Check if we need to handle stealth reveal (try to find stealth plugin)
        stealth_plugin = None
        for plugin in bot.plugins:
            if hasattr(plugin, 'handle_stealth_attack'):
                stealth_plugin = plugin
                break

        was_stealth_attack = False
        if stealth_plugin:
            was_stealth_attack = await stealth_plugin.handle_stealth_attack(bot, channel, "projectile attack")

        # Get channel mood for flavor
        channel_state = bot.get_channel_state(channel)
        mood = channel_state.mood

        # Normal firing sequence
        launcher = random.choice(self.launchers)
        effect = random.choice(self.effects).format(projectile=projectile)

        # Modify launcher description if it was a stealth attack
        if was_stealth_attack:
            launcher = f"quickly {launcher.lower()}"  # "quickly aims a trebuchet"

        # Low mood: half-hearted intro
        if mood <= 0.3 and not was_stealth_attack and random.random() < 0.5:
            await bot.privmsg(channel, random.choice(self.low_mood_flavor))
            await asyncio.sleep(0.5)

        # Two-part dramatic sequence
        await bot.action(channel, f"{launcher} loaded with {projectile} and aims at {target}...")

        # Brief pause for drama (longer if stealth attack for extra suspense)
        pause_time = 2.0 if was_stealth_attack else 1.5
        await asyncio.sleep(pause_time)

        # The impact!
        impact_message = f"DIRECT HIT! The attack {effect}!"
        if was_stealth_attack:
            impact_message = f"SNEAK ATTACK SUCCESS! The surprise assault {effect}!"

        await bot.action(channel, impact_message)

        # High mood: crowd excitement
        if mood >= 0.7 and random.random() < 0.5:
            await asyncio.sleep(0.5)
            await bot.privmsg(channel, random.choice(self.high_mood_crowd))
            return  # Skip normal bonus comment

        # Occasional bonus comment (higher chance for stealth attacks)
        bonus_chance = 0.5 if was_stealth_attack else 0.3
        if random.random() < bonus_chance:
            if was_stealth_attack:
                bonus_comments = [
                    f"*chef's kiss* Beautiful stealth work!",
                    f"{target} never saw the {projectile} coming!",
                    f"Ninja skills: MAXIMUM! {firer} is the {projectile} master!",
                    f"Critical sneak attack! {target} takes {random.randint(1, 9000)} stealth {projectile} damage!",
                    f"Achievement unlocked: Shadow {projectile} Assassin!",
                    f"*crowd gasps* What incredible {projectile} stealth tactics!",
                    f"{target} has been {projectile}ified by a ghost!",
                    f"The element of surprise makes the {projectile} twice as effective!"
                ]
            else:
                bonus_comments = [
                    f"*chef's kiss* Beautiful shot!",
                    f"{target} has been {projectile}ified!",
                    f"Bullseye! {firer} wins this round!",
                    f"Critical hit! {target} takes {random.randint(1, 9000)} {projectile} damage!",
                    f"Achievement unlocked: {projectile} Master!",
                    f"*crowd cheers* What a spectacular display of {projectile}!",
                    f"{target} will remember this {projectile} for years to come!",
                    f"Scientists are baffled by this advanced {projectile} technology!"
                ]
            await bot.privmsg(channel, random.choice(bonus_comments))

    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        """Handle /me actions - not used by this plugin"""
        return False

    async def handle_join(self, bot, nick: str, channel: str):
        """Handle user joins - not used by this plugin"""
        pass

    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        """Handle user parts - not used by this plugin"""
        pass
