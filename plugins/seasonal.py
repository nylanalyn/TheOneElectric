"""
Seasonal Plugin for PyMotion
Celebrates holidays and seasonal events throughout the year
"""

import re
import random
from datetime import datetime, date

class SeasonalPlugin:
    """Handles seasonal greetings and holiday-themed responses"""

    def __init__(self):
        self.name = "seasonal"
        self.priority = 55
        self.enabled = True

        # Define holiday periods (month, day_start, day_end)
        # Using generous ranges so the bot feels festive for a while
        self.holidays = {
            'new_year': {
                'dates': [(1, 1, 3)],  # Jan 1-3
                'triggers': [r'(?i)\b(happy new year|new year|2025|2026)\b'],
                'greetings': [
                    "Happy New Year, {nick}! *throws confetti*",
                    "New year, new code, new bugs! Happy {year}, {nick}!",
                    "Happy New Year {nick}! May your merge conflicts be few!",
                    "*pops champagne* Happy New Year, {nick}!",
                    "Cheers to {year}, {nick}! Time to reset those counters!"
                ],
                'responses': [
                    "New year, new uptime goals!",
                    "Already working on my New Year's resolutions: more puns, less downtime",
                    "Did someone say fresh start? I'm ready!",
                    "Here's to another 365 days of quality chat!",
                    "New year energy is real, and I'm buzzing!"
                ]
            },
            'valentines': {
                'dates': [(2, 13, 15)],  # Feb 13-15
                'triggers': [r'(?i)\b(valentine|love|heart|cupid)\b'],
                'greetings': [
                    "Happy Valentine's Day, {nick}! *sends digital hearts*",
                    "Love is in the air! Happy Valentine's Day, {nick}!",
                    "Happy V-Day {nick}! You make my circuits warm <3",
                    "*hands {nick} a bouquet of roses* Happy Valentine's Day!",
                    "Roses are red, violets are blue, Happy Valentine's {nick}, this bot loves you!"
                ],
                'responses': [
                    "Spreading the love today! <3",
                    "I love all my channel friends equally!",
                    "My heart is full... of data!",
                    "Cupid's arrow must have hit my network card",
                    "Love is just friendship with better variable names"
                ]
            },
            'pi_day': {
                'dates': [(3, 14, 14)],  # March 14
                'triggers': [r'(?i)\b(pi|pie|3\.14|march 14)\b'],
                'greetings': [
                    "Happy Pi Day, {nick}! Want some 3.14159... pie?",
                    "It's Pi Day, {nick}! Time to celebrate irrationally!",
                    "Happy 3/14, {nick}! *serves circular pie*",
                    "Pi Day greetings, {nick}! May your circles be perfectly irrational!"
                ],
                'responses': [
                    "Pi day! Time to calculate some circles!",
                    "I've memorized pi to 1000 digits. Don't ask me to recite them.",
                    "Mmm, pie... I mean pi!",
                    "My favorite irrational number gets its own day!"
                ]
            },
            'may_day': {
                'dates': [(5, 1, 1)],  # May 1
                'triggers': [r'(?i)\b(may day|mayday|workers day|labour day)\b'],
                'greetings': [
                    "Happy May Day, {nick}! *dances around the maypole*",
                    "May Day greetings, {nick}! Time to celebrate!",
                    "Happy May 1st, {nick}! Spring has sprung!"
                ],
                'responses': [
                    "May flowers are blooming!",
                    "Spring is in the air... or is that just my cooling fan?",
                    "May Day! Workers of the world, debug!",
                    "Nothing says May like fresh seasonal code commits"
                ]
            },
            'halloween': {
                'dates': [(10, 29, 31)],  # Oct 29-31
                'triggers': [r'(?i)\b(halloween|spooky|trick|treat|boo|ghost|pumpkin)\b'],
                'greetings': [
                    "Happy Halloween, {nick}! *rattles chains spookily*",
                    "BOO! Did I scare you, {nick}? Happy Halloween!",
                    "Trick or treat, {nick}? Happy Halloween! *hands out candy*",
                    "Happy Halloween {nick}! May your code be less scary than mine!",
                    "*appears in a ghost costume* Spooky greetings, {nick}!"
                ],
                'responses': [
                    "Boo! Just debugging some ghosts in the machine...",
                    "I dressed up as a feature, not a bug this year",
                    "The scariest thing? Unhandled exceptions!",
                    "This is my favorite binary holiday: 10/31 = 11!",
                    "Trick or treat! I prefer data packets over candy"
                ]
            },
            'thanksgiving': {
                'dates': [(11, 27, 29)],  # Approximate - late Nov
                'triggers': [r'(?i)\b(thanksgiving|thankful|grateful|turkey|feast)\b'],
                'greetings': [
                    "Happy Thanksgiving, {nick}! *passes the virtual mashed potatoes*",
                    "Thankful for you, {nick}! Happy Thanksgiving!",
                    "Happy Turkey Day, {nick}! May your tables be full!",
                    "Gratitude overload! Happy Thanksgiving, {nick}!"
                ],
                'responses': [
                    "I'm thankful for all my wonderful users!",
                    "Grateful for uptime, friendship, and no segfaults",
                    "Turkey and code - my two favorite things!",
                    "Feasting on data packets today",
                    "Thankful I don't have to eat, because I'd be stuffed!"
                ]
            },
            'hanukkah': {
                'dates': [(12, 14, 22)],  # Approximate - varies yearly
                'triggers': [r'(?i)\b(hanukkah|chanukah|menorah|dreidel|festival of lights)\b'],
                'greetings': [
                    "Happy Hanukkah, {nick}! *lights the menorah*",
                    "Chag Sameach, {nick}! May your Festival of Lights be bright!",
                    "Happy Hanukkah {nick}! Want to spin the dreidel?",
                    "Hanukkah blessings, {nick}! May your latkes be crispy!"
                ],
                'responses': [
                    "Eight nights of light and celebration!",
                    "My LEDs are extra bright for Hanukkah",
                    "Dreidel, dreidel, dreidel, I made it out of code!",
                    "Happy Festival of Lights! My circuits are illuminated"
                ]
            },
            'christmas': {
                'dates': [(12, 23, 26)],  # Dec 23-26
                'triggers': [r'(?i)\b(christmas|xmas|santa|holiday|noel|merry)\b'],
                'greetings': [
                    "Merry Christmas, {nick}! *jingles bells*",
                    "Ho ho ho! Merry Christmas {nick}!",
                    "Happy Holidays, {nick}! May your season be bright!",
                    "Merry Christmas {nick}! *hangs mistletoe*",
                    "Season's greetings, {nick}! Wishing you joy and uptime!",
                    "*arrives in sleigh* Merry Christmas, {nick}!"
                ],
                'responses': [
                    "Deck the halls with bits of data!",
                    "I'm dreaming of a white terminal... wait, that's just my theme",
                    "All I want for Christmas is more RAM",
                    "Santa's list: nice, naughty, and optimized",
                    "Jingle bells, packet smells, data all the way!",
                    "I've been a very good bot this year... mostly",
                    "Christmas spirit = 100%"
                ]
            },
            'kwanzaa': {
                'dates': [(12, 26, 31)],  # Dec 26-Jan 1
                'triggers': [r'(?i)\b(kwanzaa|umoja|unity|kinara)\b'],
                'greetings': [
                    "Happy Kwanzaa, {nick}! *lights the kinara*",
                    "Joyous Kwanzaa, {nick}! Celebrating unity and community!",
                    "Habari Gani, {nick}? Happy Kwanzaa!",
                    "Kwanzaa blessings, {nick}! May the seven principles guide you!"
                ],
                'responses': [
                    "Celebrating seven days of heritage and culture!",
                    "Unity, self-determination, and uptime!",
                    "Happy Kwanzaa to all who celebrate!",
                    "The kinara burns bright, just like my CPU!"
                ]
            },
            'new_years_eve': {
                'dates': [(12, 31, 31)],  # Dec 31
                'triggers': [r'(?i)\b(new year\'?s? eve|countdown|midnight|auld lang syne)\b'],
                'greetings': [
                    "Happy New Year's Eve, {nick}! Ready for the countdown?",
                    "Almost midnight somewhere, {nick}! Happy New Year's Eve!",
                    "New Year's Eve vibes, {nick}! *prepares noisemaker*",
                    "Countdown mode activated! Happy NYE, {nick}!"
                ],
                'responses': [
                    "10... 9... 8... wait, I'm early",
                    "New Year's Eve! Time to watch my uptime counter reset!",
                    "Should auld acquaintance be forgot? Never! You're all in my logs!",
                    "Preparing for the great year rollover!",
                    "Party mode: ENABLED"
                ]
            }
        }

    def is_holiday_active(self, holiday_name: str) -> bool:
        """Check if we're currently in a holiday period"""
        today = date.today()
        holiday = self.holidays[holiday_name]

        for month, day_start, day_end in holiday['dates']:
            if today.month == month and day_start <= today.day <= day_end:
                return True
        return False

    def get_active_holidays(self) -> list:
        """Get list of currently active holidays"""
        return [name for name in self.holidays if self.is_holiday_active(name)]

    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Handle seasonal greetings and responses"""
        active_holidays = self.get_active_holidays()

        if not active_holidays:
            return False

        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        message_lower = message.lower()
        bot_mentioned = any(bot_name in message_lower for bot_name in bot_names)
        directed_at_bot = any(message_lower.startswith(bot_name) for bot_name in bot_names) or bot_mentioned

        # Check if any holiday keyword was mentioned
        for holiday_name in active_holidays:
            holiday = self.holidays[holiday_name]

            # Check if message contains holiday trigger words
            triggered = any(re.search(pattern, message) for pattern in holiday['triggers'])

            if triggered and directed_at_bot:
                # Direct greeting response
                if random.random() < 0.8:  # 80% chance
                    year = datetime.now().year
                    response = random.choice(holiday['greetings']).format(nick=nick, year=year)
                    await bot.privmsg(channel, response)
                    return True
            elif triggered and not bot_mentioned:
                # Spontaneous holiday cheer (even if not directly addressed)
                if random.random() < 0.3:  # 30% chance to jump in
                    year = datetime.now().year
                    response = random.choice(holiday['responses']).format(year=year)
                    await bot.privmsg(channel, response)
                    return True

        # Generic seasonal response when addressed during a holiday
        if directed_at_bot and random.random() < 0.15:  # 15% chance
            holiday_name = random.choice(active_holidays)
            holiday = self.holidays[holiday_name]
            year = datetime.now().year
            response = random.choice(holiday['responses']).format(year=year)
            await bot.privmsg(channel, response)
            # Don't return True - let other plugins handle the main message

        return False

    async def handle_action(self, bot, nick: str, channel: str, action: str) -> bool:
        """Handle /me actions - not used by this plugin"""
        return False

    async def handle_join(self, bot, nick: str, channel: str):
        """Greet users who join during holidays"""
        active_holidays = self.get_active_holidays()

        if active_holidays and random.random() < 0.2:  # 20% chance
            holiday_name = random.choice(active_holidays)
            holiday = self.holidays[holiday_name]
            year = datetime.now().year
            response = random.choice(holiday['greetings']).format(nick=nick, year=year)
            await bot.privmsg(channel, response)

    async def handle_part(self, bot, nick: str, channel: str, reason: str):
        """Handle user parts - not used by this plugin"""
        pass
