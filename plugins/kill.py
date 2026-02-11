"""
Kill Plugin for PyMotion
Playful kill command with escalating ridiculous weapons
Tracks kill count per user, friendship-aware
"""

import asyncio
import random
import re

class KillPlugin:
    """Playful kill command with escalation tiers"""

    def __init__(self):
        self.name = "kill"
        self.priority = 70
        self.enabled = True

        # Tier 1: Gentle (kills 1-3) — original behavior
        self.weapons_gentle = [
            "a rubber duck", "harsh language", "a wet noodle", "a feather",
            "tickles", "bad puns", "a pillow", "stale cookies",
            "elevator music", "a strongly worded letter", "interpretive dance",
            "an uncomfortable stare", "a paper airplane", "social awkwardness"
        ]
        self.actions_gentle = [
            "gently pokes {target} with {weapon}",
            "threatens {target} with {weapon}",
            "waves {weapon} menacingly at {target}",
            "attempts to defeat {target} using {weapon}",
            "challenges {target} to combat with {weapon}",
            "pelts {target} with {weapon}"
        ]

        # Tier 2: Moderate (kills 4-7)
        self.weapons_moderate = [
            "a small army of rubber ducks", "a slightly larger noodle",
            "a grand piano", "a suspiciously heavy dictionary",
            "a rogue shopping cart", "a sentient vacuum cleaner",
            "an angry swarm of bees (rubber)", "a trebuchet loaded with pudding",
        ]
        self.actions_moderate = [
            "summons a small army of rubber ducks to overwhelm {target}",
            "drops a piano from the sky onto {target}",
            "launches {weapon} at {target} with surprising accuracy",
            "sends a rogue shopping cart careening toward {target}",
            "deploys {weapon} directly at {target}'s location",
            "orchestrates an elaborate ambush on {target} using {weapon}",
        ]

        # Tier 3: Dramatic (kills 8-12)
        self.weapons_dramatic = [
            "tactical cheese", "antimatter marshmallows",
            "a black hole generator", "weaponized glitter",
            "orbital laser pointer", "a portal to the shadow realm",
            "quantum-entangled rubber ducks", "a supernova in a bottle",
        ]
        self.actions_dramatic = [
            "calls in an airstrike of {weapon} on {target}'s position",
            "opens a portal to the {weapon} dimension and shoves {target} through",
            "activates the {weapon} protocol — {target} never stood a chance",
            "summons an ancient deity armed with {weapon} to smite {target}",
            "deploys {weapon} from orbit, targeting {target} specifically",
            "initiates Operation {weapon} — codename: Destroy {target}",
        ]

        # Tier 4: Overkill (kills 13-16)
        self.overkill_sequences = [
            [
                "deploys EVERY weapon simultaneously at {target}",
                "The sky darkens. The ground shakes.",
                "A thousand rubber ducks descend from the heavens upon {target}.",
            ],
            [
                "activates the Omega Protocol targeting {target}",
                "*alarms blare* OVERKILL MODE ENGAGED",
                "{target} has been vaporized, reconstituted, and vaporized again for good measure.",
            ],
            [
                "opens ALL the portals around {target}",
                "Weapons from every dimension converge on {target}'s location.",
                "The resulting explosion is visible from space. {target} is... somewhere.",
            ],
            [
                "dials the kill intensity to 11 for {target}",
                "*dramatic music intensifies*",
                "{target} has been eliminated with extreme prejudice and mild seasoning.",
            ],
        ]

        # Tier 5: Unkillable (kills 17+) — resets count
        self.unkillable_responses = [
            "*stares at {target}* ...you know what? They're unkillable. I declare {target} IMMORTAL.",
            "I've thrown everything I have at {target}. Nothing works. They're beyond my power now.",
            "*drops all weapons* {target} has transcended mortality. I... I can't do this anymore.",
            "ENOUGH! {target} has achieved immortality through sheer stubbornness. Congratulations, I guess.",
            "*checks notes* I've killed {target} so many times they've developed an immunity. They're unkillable.",
        ]

        # Tired/late-night flavor
        self.tired_prefix = [
            "*yawns* Fine, I'll do it...",
            "*rubs eyes* Another kill? At this hour?",
            "*barely awake* Yeah yeah, kill {target}, whatever...",
            "*half asleep* Hold on let me find my weapons...",
        ]

        # Bestie defense
        self.bestie_defense = [
            "*shields {target}* Not on my watch!",
            "Kill {target}? That's my BEST FRIEND. Absolutely not.",
            "*stands in front of {target}* You'll have to go through ME first!",
            "Touch {target} and I'll deploy every weapon I have at YOU, {nick}.",
            "*protectively hugs {target}* Nobody hurts my bestie!",
        ]

    def _get_tier(self, kill_count: int) -> str:
        if kill_count <= 3:
            return "gentle"
        elif kill_count <= 7:
            return "moderate"
        elif kill_count <= 12:
            return "dramatic"
        elif kill_count <= 16:
            return "overkill"
        else:
            return "unkillable"

    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]

        # Only respond when the bot is addressed
        addressed = any(
            re.search(rf'(?i)\b{re.escape(name)}\b', message)
            for name in bot_names
        )
        if not addressed:
            return False

        kill_match = re.search(r'(?i)kill (\w+)(?:\s+with\s+(.+))?', message)
        if not kill_match:
            return False

        target = kill_match.group(1)
        custom_weapon = kill_match.group(2)

        # Can't kill the bot
        if target.lower() == bot.config['nick'].lower():
            await bot.privmsg(channel, f"*dodges* You can't kill me, {nick}! I'm immortal!")
            return True

        # Self-kill
        if target.lower() == nick.lower():
            await bot.privmsg(channel, f"*hands {nick} a mirror* Here you go!")
            return True

        # Bestie defense
        target_tier = bot.get_friendship_tier(channel, target)
        if target_tier == "bestie":
            response = random.choice(self.bestie_defense).format(target=target, nick=nick)
            await bot.privmsg(channel, response)
            return True

        # Get and increment kill count
        target_state = bot.get_user_state(channel, target)
        target_state.kill_count += 1
        count = target_state.kill_count
        tier = self._get_tier(count)

        # Get time personality for tired flavor
        personality = bot.get_time_personality()

        # Tired prefix for late night
        tired_intro = ""
        if personality["energy"] <= 0.7 and random.random() < 0.5:
            tired_intro = random.choice(self.tired_prefix).format(target=target)

        if tier == "unkillable":
            response = random.choice(self.unkillable_responses).format(target=target)
            if tired_intro:
                await bot.privmsg(channel, tired_intro)
                await asyncio.sleep(1)
            await bot.privmsg(channel, response)
            target_state.kill_count = 10  # Reset to dramatic tier
            return True

        if tier == "overkill":
            if tired_intro:
                await bot.privmsg(channel, tired_intro)
                await asyncio.sleep(1)
            sequence = random.choice(self.overkill_sequences)
            for line in sequence:
                formatted = line.format(target=target, nick=nick)
                await bot.action(channel, formatted) if not formatted[0].isupper() else await bot.privmsg(channel, formatted)
                await asyncio.sleep(1.5)
            return True

        # Gentle / Moderate / Dramatic tiers
        if tier == "gentle":
            weapon = custom_weapon if custom_weapon else random.choice(self.weapons_gentle)
            action = random.choice(self.actions_gentle).format(target=target, weapon=weapon)
        elif tier == "moderate":
            weapon = custom_weapon if custom_weapon else random.choice(self.weapons_moderate)
            action = random.choice(self.actions_moderate).format(target=target, weapon=weapon)
        else:  # dramatic
            weapon = custom_weapon if custom_weapon else random.choice(self.weapons_dramatic)
            action = random.choice(self.actions_dramatic).format(target=target, weapon=weapon)

        if tired_intro:
            await bot.privmsg(channel, tired_intro)
            await asyncio.sleep(1)
        await bot.action(channel, action)
        return True

    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        return False

    async def handle_join(self, bot, nick: str, channel: str):
        pass

    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        pass
