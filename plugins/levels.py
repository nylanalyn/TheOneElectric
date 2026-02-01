"""
Levels Plugin for PyMotion
Randomly announces abstract noun levels with a percentage and direction.
"""

import random
import time


ABSTRACT_NOUNS = [
    "Absurdity", "Acrimony", "Admiration", "Adoration", "Adversity", "Affection",
    "Agony", "Alienation", "Allegiance", "Ambiguity", "Ambition", "Amusement",
    "Anarchy", "Anguish", "Animosity", "Anticipation", "Antipathy", "Anxiety",
    "Apathy", "Apprehension", "Arrogance", "Atonement", "Audacity", "Avarice",
    "Awe", "Awkwardness", "Banality", "Bedlam", "Befuddlement", "Belligerence",
    "Benevolence", "Bewilderment", "Bitterness", "Bliss", "Boredom", "Bravado",
    "Bravery", "Brutality", "Bureaucracy", "Calamity", "Callousness", "Camaraderie",
    "Capitalism", "Carnage", "Chaos", "Charisma", "Charity", "Chicanery",
    "Chivalry", "Clarity", "Coercion", "Complacency", "Complexity", "Compliance",
    "Compulsion", "Conceit", "Confidence", "Conformity", "Confusion", "Contempt",
    "Contentment", "Conviction", "Corruption", "Cowardice", "Credulity", "Cruelty",
    "Curiosity", "Cynicism", "Darkness", "Decadence", "Deceit", "Defiance",
    "Degradation", "Dejection", "Delight", "Delusion", "Democracy", "Depravity",
    "Depression", "Derangement", "Derision", "Desire", "Desolation", "Despair",
    "Desperation", "Destiny", "Devotion", "Dignity", "Diligence", "Disappointment",
    "Disbelief", "Discontent", "Disdain", "Disgrace", "Disgust", "Dishonesty",
    "Disillusionment", "Dismay", "Disobedience", "Displeasure", "Dissent",
    "Distortion", "Distraction", "Distrust", "Dominance", "Doom", "Doubt",
    "Dread", "Drudgery", "Duplicity", "Eccentricity", "Ecstasy", "Efficiency",
    "Ego", "Elation", "Eloquence", "Embarrassment", "Empathy", "Emptiness",
    "Enchantment", "Endurance", "Enigma", "Ennui", "Entropy", "Envy",
    "Epiphany", "Equilibrium", "Euphoria", "Exasperation", "Excess", "Excitement",
    "Exhaustion", "Existentialism", "Exuberance", "Fanaticism", "Fascination",
    "Fatalism", "Fatigue", "Fear", "Ferocity", "Fervor", "Fickleness",
    "Fidelity", "Flamboyance", "Flattery", "Folly", "Foolishness", "Forbearance",
    "Foreboding", "Fortitude", "Fragility", "Frenzy", "Frivolity", "Frustration",
    "Fulfillment", "Futility", "Gallantry", "Generosity", "Genius", "Gloom",
    "Gluttony", "Goodwill", "Grace", "Grandeur", "Gratitude", "Greed",
    "Grief", "Grit", "Guilt", "Gullibility", "Harmony", "Hatred",
    "Haughtiness", "Havoc", "Hedonism", "Helplessness", "Heresy", "Heroism",
    "Hesitation", "Honesty", "Honor", "Hope", "Hopelessness", "Hostility",
    "Hubris", "Humiliation", "Humility", "Hunger", "Hyperactivity", "Hypocrisy",
    "Hysteria", "Idealism", "Idiocy", "Ignorance", "Imagination", "Immorality",
    "Impatience", "Impudence", "Inadequacy", "Indecision", "Indifference",
    "Indignation", "Infamy", "Infatuation", "Ingenuity", "Inhumanity",
    "Innocence", "Innovation", "Insanity", "Insecurity", "Insolence",
    "Inspiration", "Integrity", "Intellect", "Intensity", "Intimidation",
    "Intrigue", "Intuition", "Irony", "Irrationality", "Irreverence",
    "Isolation", "Jealousy", "Joy", "Jubilation", "Justice", "Karma",
    "Kindness", "Lawlessness", "Laziness", "Lethargy", "Levity", "Liberty",
    "Loneliness", "Longing", "Looming", "Love", "Loyalty", "Lunacy",
    "Lust", "Madness", "Magnificence", "Malevolence", "Malice", "Mania",
    "Manipulation", "Martyrdom", "Mediocrity", "Melancholy", "Menace", "Mercy",
    "Mischief", "Misery", "Modesty", "Monotony", "Morbidity", "Mortality",
    "Mysticism", "Naivety", "Narcissism", "Neglect", "Negligence", "Nervousness",
    "Nihilism", "Nobility", "Nonchalance", "Nostalgia", "Notoriety", "Obedience",
    "Obligation", "Oblivion", "Obscenity", "Obsession", "Obstinacy", "Opulence",
    "Optimism", "Outrage", "Overwhelm", "Pageantry", "Pain", "Pandemonium",
    "Panic", "Paranoia", "Passion", "Patience", "Patriotism", "Peculiarity",
    "Pensiveness", "Perdition", "Perfection", "Peril", "Perseverance", "Pessimism",
    "Petulance", "Piety", "Pity", "Pomposity", "Pragmatism", "Prejudice",
    "Presumption", "Pride", "Profanity", "Profundity", "Propaganda", "Prosperity",
    "Providence", "Provocation", "Prudence", "Psychosis", "Purity", "Puzzlement",
    "Quaintness", "Queasiness", "Radiance", "Rage", "Rancor", "Rapture",
    "Recklessness", "Redemption", "Regret", "Reluctance", "Remorse", "Resentment",
    "Resignation", "Resilience", "Resolve", "Restlessness", "Retribution",
    "Revelation", "Revenge", "Reverence", "Revulsion", "Righteousness", "Rigidity",
    "Romance", "Ruthlessness", "Sabotage", "Sadism", "Sadness", "Sanctimony",
    "Sanity", "Sarcasm", "Satisfaction", "Savagery", "Schadenfreude", "Scrutiny",
    "Seduction", "Selfishness", "Sentimentality", "Serenity", "Severity", "Shame",
    "Sincerity", "Skepticism", "Sloth", "Smugness", "Solemnity", "Solitude",
    "Sophistication", "Sorrow", "Sovereignty", "Spite", "Spontaneity", "Stoicism",
    "Stubbornness", "Stupidity", "Submission", "Subtlety", "Suffering",
    "Superiority", "Superstition", "Suspicion", "Sympathy", "Tedium", "Temperance",
    "Temptation", "Tenacity", "Tenderness", "Terror", "Theatricality",
    "Thoughtfulness", "Timidity", "Tolerance", "Torment", "Tranquility",
    "Treachery", "Trepidation", "Tribulation", "Triumph", "Triviality", "Truculence",
    "Turmoil", "Tyranny", "Uncertainty", "Unease", "Unrest", "Urgency",
    "Valor", "Vanity", "Vehemence", "Vengeance", "Vexation", "Vigilance",
    "Villainy", "Vindication", "Virtue", "Vitality", "Vivacity", "Volatility",
    "Vulnerability", "Wanderlust", "Weariness", "Whimsy", "Wickedness", "Wisdom",
    "Wistfulness", "Woe", "Wonder", "Wrath", "Wretchedness", "Yearning",
    "Zeal", "Zealotry",
]

DIRECTIONS = [
    "rising", "rising", "rising",
    "falling", "falling", "falling",
    "holding steady", "holding steady",
    "climbing fast", "dropping fast",
    "surging", "plummeting",
    "spiking", "cratering",
    "inching upward", "inching downward",
    "fluctuating wildly", "off the charts",
    "approaching critical", "stabilizing",
    "accelerating", "decelerating",
    "going through the roof", "in freefall",
]


class LevelsPlugin:
    """Randomly announces abstract noun levels."""

    def __init__(self):
        self.name = "levels"
        self.priority = 5
        self.enabled = True
        self.channel_last_announcement = {}
        self.min_interval = 3600  # 1 hour minimum between announcements

    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        now = time.time()
        last = self.channel_last_announcement.get(channel.lower(), 0.0)
        if now - last < self.min_interval:
            return False

        # ~2% chance per message once the cooldown has elapsed
        if random.random() > 0.02:
            return False

        noun = random.choice(ABSTRACT_NOUNS)
        pct = random.randint(1, 100)
        direction = random.choice(DIRECTIONS)
        await bot.privmsg(channel, f"{noun} levels at {pct}% and {direction}!")
        self.channel_last_announcement[channel.lower()] = now
        return True

    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        return False

    async def handle_join(self, bot, nick: str, channel: str):
        pass

    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        pass
