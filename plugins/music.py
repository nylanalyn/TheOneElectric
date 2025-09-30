"""
Music Plugin for PyMotion
Responds to music discussions with absurdly named fake bands and albums
"""

import random
import re

class MusicPlugin:
    """Respond to music talk with unhinged fake band recommendations"""

    def __init__(self):
        self.name = "music"
        self.priority = 45  # Mid-priority conversational plugin
        self.enabled = True

        # Band name components
        self.band_prefixes = [
            "The", "DJ", "MC", "Lil", "Big", "Young", "Old", "Dead",
            "Psychic", "Atomic", "Electric", "Cosmic", "Quantum", "Professor",
            "Captain", "Doctor", "Reverend", "Admiral", "Lord", "Sir"
        ]

        self.band_nouns = [
            "Spatula", "Dishwasher", "Refrigerator", "Toaster", "Blender",
            "Potato", "Pickle", "Onion", "Garlic", "Cabbage", "Turnip",
            "Eyeball", "Toenail", "Kidney", "Spleen", "Appendix",
            "Xerox", "Fax", "Modem", "Router", "USB",
            "Stapler", "Clipboard", "Binder", "Eraser", "Pencil",
            "Doorknob", "Hinge", "Screw", "Bolt", "Washer",
            "Fungus", "Mold", "Bacteria", "Virus", "Parasite",
            "Puddle", "Sludge", "Ooze", "Gunk", "Slime",
            "Squeegee", "Plunger", "Mop", "Broom", "Dustpan"
        ]

        self.band_adjectives = [
            "Screaming", "Crying", "Melting", "Floating", "Spinning",
            "Cursed", "Blessed", "Haunted", "Possessed", "Enchanted",
            "Radioactive", "Toxic", "Explosive", "Combustible", "Flammable",
            "Invisible", "Transparent", "Translucent", "Opaque", "Holographic",
            "Caffeinated", "Decaffeinated", "Carbonated", "Fermented", "Pickled",
            "Synthetic", "Artificial", "Simulated", "Virtual", "Digital",
            "Prehistoric", "Ancient", "Medieval", "Victorian", "Futuristic",
            "Perpendicular", "Parallel", "Diagonal", "Vertical", "Horizontal"
        ]

        self.band_plurals = [
            "Brothers", "Sisters", "Cousins", "Uncles", "Aunts",
            "Committee", "Council", "Assembly", "Coalition", "Syndicate",
            "Orchestra", "Choir", "Ensemble", "Quartet", "Trio",
            "Collective", "Cooperative", "Union", "Federation", "League",
            "Experience", "Experiment", "Project", "Initiative", "Program"
        ]

        # Album title components
        self.album_adjectives = [
            "Acoustic", "Electric", "Synthetic", "Organic", "Cosmic",
            "Existential", "Metaphysical", "Surreal", "Abstract", "Concrete",
            "Infinite", "Finite", "Eternal", "Temporal", "Momentary",
            "Forbidden", "Mandatory", "Optional", "Required", "Voluntary",
            "Reversed", "Inverted", "Mirrored", "Reflected", "Refracted",
            "Compressed", "Expanded", "Inflated", "Deflated", "Punctured",
            "Laminated", "Perforated", "Corrugated", "Serrated", "Textured",
            "Discontinued", "Recalled", "Expired", "Refurbished", "Renewed"
        ]

        self.album_nouns = [
            "Sorrow", "Despair", "Anguish", "Confusion", "Bewilderment",
            "Laundry", "Dishes", "Vacuum", "Dusting", "Mopping",
            "Taxes", "Spreadsheet", "Meeting", "Memo", "Invoice",
            "Transit", "Parking", "Traffic", "Detour", "Roadwork",
            "Existentialism", "Nihilism", "Absurdism", "Pragmatism", "Realism",
            "Breakfast", "Lunch", "Dinner", "Brunch", "Snack",
            "Tuesday", "Wednesday", "Thursday", "Monday", "Weekend",
            "WiFi", "Bluetooth", "Ethernet", "Bandwidth", "Latency",
            "Geometry", "Algebra", "Calculus", "Trigonometry", "Statistics",
            "Plumbing", "Electrical", "Carpentry", "Masonry", "Drywall"
        ]

        self.album_formats = [
            "{adj} {noun}",
            "The {noun} of {adj} {noun}",
            "{adj} {noun}: Part {num}",
            "Songs About {noun}",
            "Studies in {adj} {noun}",
            "{noun} (Deluxe Edition)",
            "{adj} {noun} (Remastered)",
            "A Collection of {adj} {noun}",
            "{noun} & {noun}",
            "The Complete {noun}",
            "{adj} {noun}: A Retrospective",
            "Live at the {noun}",
            "{noun} (Instrumental Version)",
            "Tales from the {adj} {noun}",
            "{noun} Forever"
        ]

        # Response templates
        self.response_templates = [
            "Oh really? I've been listening to {band}, I find their album '{album}' to be fantastic.",
            "Speaking of music, have you heard {band}? Their '{album}' absolutely changed my life.",
            "That reminds me of {band}. '{album}' is a masterpiece, truly ahead of its time.",
            "I'm personally obsessed with {band} right now. '{album}' is on repeat.",
            "You should check out {band}. '{album}' won 47 Grammy awards in a parallel universe.",
            "Interesting! I've been jamming to {band} lately. '{album}' really speaks to me.",
            "{band} is my current vibe. '{album}' is pure sonic genius.",
            "If you like music, you'll love {band}. '{album}' is their magnum opus.",
            "Have you experienced {band}? '{album}' will change how you perceive sound itself.",
            "I'm deep into {band}'s discography. '{album}' is criminally underrated."
        ]

        # Probability of responding
        self.response_chance = 0.25  # 25% chance to respond

    def generate_band_name(self) -> str:
        """Generate an absurd band name"""
        patterns = [
            lambda: f"{random.choice(self.band_prefixes)} {random.choice(self.band_adjectives)} {random.choice(self.band_nouns)}",
            lambda: f"{random.choice(self.band_adjectives)} {random.choice(self.band_nouns)} {random.choice(self.band_plurals)}",
            lambda: f"{random.choice(self.band_prefixes)} {random.choice(self.band_nouns)} {random.choice(self.band_plurals)}",
            lambda: f"{random.choice(self.band_nouns)} {random.choice(self.band_plurals)}",
            lambda: f"{random.choice(self.band_adjectives)} {random.choice(self.band_nouns)}",
            lambda: f"{random.choice(self.band_prefixes)} {random.choice(self.band_nouns)}",
            # Super unhinged combinations
            lambda: f"{random.choice(self.band_adjectives)} {random.choice(self.band_nouns)} and the {random.choice(self.band_adjectives)} {random.choice(self.band_plurals)}",
            lambda: f"The {random.choice(self.band_nouns)}s",
        ]

        return random.choice(patterns)()

    def generate_album_title(self) -> str:
        """Generate an absurd album title"""
        template = random.choice(self.album_formats)

        return template.format(
            adj=random.choice(self.album_adjectives),
            noun=random.choice(self.album_nouns),
            num=random.randint(1, 27)
        )

    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Handle music-related messages"""

        # Ignore our own messages
        if nick == bot.config['nick']:
            return False

        message_lower = message.lower()

        # Patterns that indicate music discussion
        music_patterns = [
            r'\blistening to\b',
            r'\blistening\b',
            r'\bwhat.*music\b',
            r'\bwhat.*listening\b',
            r'\bwhat.*you.*listen',
            r'\bhearing\b',
            r'\bplaying\b.*\b(song|music|album|track|band|artist)\b',
            r'\b(song|music|album|track|band|artist)\b.*\bplaying\b',
            r'\bjamming to\b',
            r'\bbumping\b',
            r'\bvibing to\b',
            r'\bnow playing\b',
            r'\bcurrently listening\b',
            r'\bon repeat\b',
            r'\bfavorite (song|album|band|artist)\b',
            r'\bmusic recommendation\b',
            r'\brecommend.*music\b',
            r'\bgood music\b',
            r'\blistening\?',
        ]

        # Check if message matches any music pattern
        matches_pattern = any(re.search(pattern, message_lower) for pattern in music_patterns)

        if not matches_pattern:
            return False

        # Probabilistic response - don't respond every time
        if random.random() > self.response_chance:
            return False

        # Generate absurd band and album
        band_name = self.generate_band_name()
        album_title = self.generate_album_title()

        # Select response template
        response = random.choice(self.response_templates).format(
            band=band_name,
            album=album_title
        )

        await bot.privmsg(channel, response)
        return True

    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        """Handle /me actions - not used by this plugin"""
        return False

    async def handle_join(self, bot, nick: str, channel: str):
        """Handle user joins - not used by this plugin"""
        pass

    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        """Handle user parts - not used by this plugin"""
        pass
