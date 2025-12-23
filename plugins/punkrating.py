"""
Punk Rating Plugin - AI-powered punk ratings via DeepSeek

Provides !rate and !suggest commands using DeepSeek AI to judge things
on the punk scale with Henry Botlins' jaded 80s punk rocker personality.
"""

import asyncio
import json
import os
import time
import urllib.error
import urllib.request
from typing import Dict, Optional


class Plugin:
    """Punk rating plugin using DeepSeek AI"""
    
    name = "punkrating"
    priority = 50  # Higher priority to catch commands early
    enabled = True
    
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config.get('deepseek', {})
        
        # DeepSeek API configuration
        self.api_base = self.config.get('api_base', 'https://api.deepseek.com/v1/chat/completions')
        self.model = self.config.get('model', 'deepseek-chat')
        self.api_key_env = self.config.get('api_key_env', 'DEEPSEEK_API_KEY')
        self.temperature = self.config.get('temperature', 0.7)
        
        # Prompts
        self.rate_prompt = self.config.get(
            'prompt',
            "You are Henry Botlins, a jaded 80s punk rocker judging whether things are punk or sellout trash. "
            "Be blunt, be mean, be funny. Rate {thing} on the punk scale and explain why in 1-2 sentences max. "
            "Don't hedge, pick a side."
        )
        self.suggestion_prompt = self.config.get(
            'suggestion_prompt',
            "You are Henry Botlins, a jaded 80s punk rocker. Someone asked about {thing}. "
            "Suggest a similar alternative that would be 10/10 on the punk scale. "
            "Be specific, creative, and blunt. Keep it to 1-2 sentences max."
        )
        
        # Memory and cooldown management
        self.data_file = self.config.get('data_file', 'punk_ratings.json')
        self.cooldown_seconds = self.config.get('cooldown_seconds', 30)
        self.memory: Dict[str, Dict[str, str]] = {}
        self.cooldowns: Dict[str, float] = {}
        
        self._load_memory()
    
    def _load_memory(self):
        """Load previous ratings from JSON file"""
        if not os.path.exists(self.data_file):
            return
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.memory = json.load(f)
        except (json.JSONDecodeError, OSError):
            self.memory = {}
    
    def _save_memory(self):
        """Save ratings to JSON file"""
        tmp_path = self.data_file + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2)
        os.replace(tmp_path, self.data_file)
    
    def _normalize_thing(self, text: str) -> str:
        """Normalize thing name for memory lookup"""
        return ' '.join(text.strip().split()).lower()
    
    async def _call_deepseek(self, system_prompt: str, user_prompt: str) -> str:
        """Make API call to DeepSeek"""
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key env var {self.api_key_env}")
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": 120
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            self.api_base,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: urllib.request.urlopen(req, timeout=20)
            )
            body = response.read()
            parsed = json.loads(body.decode('utf-8'))
        except urllib.error.HTTPError as e:
            detail = e.read().decode('utf-8', errors='ignore')
            raise RuntimeError(f"DeepSeek HTTP error {e.code}: {detail}")
        except Exception as e:
            raise RuntimeError(f"DeepSeek request failed: {e}")
        
        choices = parsed.get('choices', [])
        if not choices:
            raise RuntimeError("DeepSeek returned no choices")
        
        message = choices[0].get('message', {})
        content = message.get('content', '').strip()
        if not content:
            raise RuntimeError("DeepSeek returned an empty message")
        
        return content
    
    async def _rate_thing(self, thing: str) -> str:
        """Get a punk rating for a thing"""
        system_prompt = self.rate_prompt.format(thing=thing)
        user_prompt = f"Rate this thing on the punk scale and explain why: {thing}"
        return await self._call_deepseek(system_prompt, user_prompt)
    
    async def _suggest_alternative(self, thing: str) -> str:
        """Suggest a punk alternative to a thing"""
        system_prompt = self.suggestion_prompt.format(thing=thing)
        user_prompt = f"Suggest a similar but way more punk alternative to: {thing}"
        return await self._call_deepseek(system_prompt, user_prompt)
    
    def _check_cooldown(self, nick: str) -> bool:
        """Check if user is on cooldown. Returns True if they should wait."""
        now = time.time()
        last_time = self.cooldowns.get(nick, 0)
        if now - last_time < self.cooldown_seconds:
            return True
        self.cooldowns[nick] = now
        return False
    
    async def handle_message(self, bot, nick, channel, message):
        """Handle !rate and !suggest commands"""
        msg_lower = message.lower()
        is_rate = msg_lower.startswith('!rate')
        is_suggest = msg_lower.startswith('!suggest')
        
        if not is_rate and not is_suggest:
            return False
        
        # Parse the thing to rate/suggest
        parts = message.split(' ', 1)
        if len(parts) < 2 or not parts[1].strip():
            if is_rate:
                await bot.send_message(channel, f"{nick}: rate what? give me a thing.")
            else:
                await bot.send_message(channel, f"{nick}: suggest what? give me a thing.")
            return True
        
        thing = parts[1].strip()
        
        # Check cooldown
        if self._check_cooldown(nick):
            await bot.send_message(
                channel,
                f"{nick}: cool your jets. Try again in a bit."
            )
            return True
        
        # Check memory for existing rating/suggestion
        key_prefix = 'suggestion:' if is_suggest else ''
        key = key_prefix + self._normalize_thing(thing)
        existing = self.memory.get(key)
        
        if existing:
            if existing.get('nick') == nick:
                await bot.send_message(
                    channel,
                    f"{nick}: you already asked. Scroll up in your logs."
                )
            else:
                await bot.send_message(
                    channel,
                    f"{nick}: like I told {existing.get('nick')}, {existing.get('response')}"
                )
            return True
        
        # Get new rating/suggestion from DeepSeek
        try:
            if is_rate:
                response = await self._rate_thing(thing)
            else:
                response = await self._suggest_alternative(thing)
        except Exception as e:
            await bot.send_message(
                channel,
                f"{nick}: DeepSeek borked: {e}"
            )
            return True
        
        # Save to memory
        self.memory[key] = {
            'thing': thing,
            'response': response,
            'nick': nick,
            'timestamp': time.time()
        }
        self._save_memory()
        
        # Send response
        await bot.send_message(channel, response)
        return True
    
    async def handle_action(self, bot, nick, channel, action):
        """Not used by this plugin"""
        return False
    
    async def handle_join(self, bot, nick, channel):
        """Not used by this plugin"""
        pass
    
    async def handle_part(self, bot, nick, channel, reason):
        """Not used by this plugin"""
        pass
