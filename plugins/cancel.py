"""
Cancel Plugin for PyMotion
Cancel people for silly reasons and dish out ridiculous punishments
"""

import asyncio
import random
import re
import logging
from datetime import datetime

class CancelPlugin:
    """Cancel people for silly reasons and dish out ridiculous punishments"""
    
    def __init__(self):
        self.name = "cancel"
        self.priority = 65  # High priority to catch cancel commands
        self.enabled = True
        
        # Silly accusations that would "cancel" someone
        self.accusations = [
            "using a light theme in their IDE",
            "putting pineapple on pizza",
            "not using vim keybindings",
            "liking the Star Wars prequels unironically",
            "using Internet Explorer by choice",
            "thinking tabs are better than spaces",
            "microwaving leftover pizza",
            "using Comic Sans in a serious presentation",
            "saying 'gif' instead of 'jif'",
            "not washing their hands after using the bathroom",
            "double-dipping chips at parties",
            "spoiling movies in YouTube comments",
            "being a JavaScript developer",
            "thinking Python is overrated",
            "using Arch Linux and telling everyone about it",
            "rickrolling people in 2024",
            "still using Windows XP",
            "putting milk before cereal",
            "saying 'anyways' instead of 'anyway'",
            "using 'your' when they mean 'you're'",
            "clapping when the plane lands",
            "not returning shopping carts",
            "texting 'k' as a response",
            "heating fish in the office microwave",
            "talking during movies",
            "not using an ad blocker",
            "thinking cryptocurrency is the future",
            "buying NFTs of cartoon monkeys",
            "using TikTok dances as their main form of communication",
            "saying 'based' unironically"
        ]
        
        # Ridiculous punishments for cancelled streamers/youtubers
        self.punishments = [
            "must make a 47-minute ukulele apology video",
            "has to stream nothing but educational content about tax law for a month",
            "must collaborate exclusively with Minecraft YouTubers who scream",
            "is sentenced to only playing mobile games on stream",
            "must end every sentence with 'uwu' for two weeks",
            "has to react to their own old cringe content for 8 hours straight",
            "is forced to use Internet Explorer for all streaming activities",
            "must make sincere apology videos for every meal they eat",
            "has to play only sponsored mobile game ads for content",
            "is required to ask viewers to 'smash that like button' every 30 seconds",
            "must stream exclusively in 240p resolution as penance",
            "has to read every single comment in a fake crying voice",
            "is sentenced to collaborating with Logan Paul",
            "must make content wearing a 'I'm Sorry' sandwich board",
            "has to stream while using only voice-to-text for chat interaction",
            "is forced to react to 10 hours of paint drying videos",
            "must make all future content in the form of PowerPoint presentations",
            "has to stream with their mom giving commentary",
            "is sentenced to explaining every meme from 2008",
            "must make apology videos in different accents each day",
            "has to stream while wearing oven mitts",
            "is forced to use only Comic Sans in all thumbnails",
            "must end every stream by singing the Baby Shark song",
            "has to make content while riding a stationary bike",
            "is sentenced to reviewing only pineapple pizza for a month",
            "must stream with auto-tune permanently enabled",
            "has to make sincere book reviews of instruction manuals",
            "is forced to stream exclusively during 3 AM infomercial hours",
            "must make all content while speaking in rhyme",
            "has to stream with a laugh track playing randomly"
        ]
        
        # Track active cancellations with timing
        self.active_cancellations = {}  # {channel: {target: task}}
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Handle message and check for cancel commands"""
        # Check if someone is trying to cancel someone
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        
        for bot_name in bot_names:
            cancel_match = re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\bcancel\s+(\w+)', message)
            if cancel_match:
                target = cancel_match.group(1)
                
                # Don't cancel the bot itself or the person doing the cancelling
                if target.lower() == bot_name or target.lower() == nick.lower():
                    await bot.privmsg(channel, f"Nice try, {nick}, but I'm uncancellable! 😎")
                    return True
                
                # Cancel the target!
                await self.cancel_user(bot, channel, nick, target)
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
    
    async def cancel_user(self, bot, channel: str, canceller: str, target: str):
        """Cancel a user and schedule their punishment"""
        
        # Cancel any existing cancellation for this target in this channel
        if channel in self.active_cancellations and target in self.active_cancellations[channel]:
            self.active_cancellations[channel][target].cancel()
        
        # Pick a random accusation
        accusation = random.choice(self.accusations)
        
        # Announce the cancellation
        await bot.privmsg(channel, f"🚨 BREAKING: {target} has been CANCELLED! 🚨")
        await asyncio.sleep(1)  # Dramatic pause
        await bot.privmsg(channel, f"They have been accused of {accusation}!")
        await bot.privmsg(channel, f"Punishment will be decided shortly... *dramatic music*")
        
        # Schedule the punishment (2-4 minutes delay for maximum suspense)
        delay = random.randint(120, 240)  # 2-4 minutes
        
        # Store the task so we can cancel it if needed
        if channel not in self.active_cancellations:
            self.active_cancellations[channel] = {}
        
        punishment_task = asyncio.create_task(
            self.deliver_punishment(bot, channel, target, delay)
        )
        self.active_cancellations[channel][target] = punishment_task
        
        logging.info(f"{canceller} cancelled {target} in {channel}, punishment in {delay} seconds")
    
    async def deliver_punishment(self, bot, channel: str, target: str, delay: int):
        """Deliver the punishment after a delay"""
        try:
            await asyncio.sleep(delay)
            
            # Pick a random punishment
            punishment = random.choice(self.punishments)
            
            # Announce the punishment
            await bot.privmsg(channel, f"⚖️ The Council has decided!")
            await asyncio.sleep(1)
            await bot.privmsg(channel, f"{target}'s punishment: {punishment}")
            await bot.privmsg(channel, f"May this serve as a warning to others! 😤")
            
            # Clean up the active cancellation
            if channel in self.active_cancellations and target in self.active_cancellations[channel]:
                del self.active_cancellations[channel][target]
                if not self.active_cancellations[channel]:
                    del self.active_cancellations[channel]
                    
        except asyncio.CancelledError:
            # Cancellation was cancelled (probably by a new cancellation)
            logging.debug(f"Punishment for {target} in {channel} was cancelled")
            pass
