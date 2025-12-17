"""
AI Response Plugin for PyMotion
Integrates with OpenRouter API to provide intelligent responses
"""

import re
import random
import time
import httpx
import asyncio
from typing import List, Dict, Any
import logging

class AIResponsePlugin:
    """AI Response Plugin that uses OpenRouter API"""
    
    def __init__(self):
        self.name = "ai_response"
        self.priority = 40  # Medium priority - should respond after greetings but before random responses
        self.enabled = True
        
        # Configuration defaults
        self.config = {
            "openrouter_api_key": None,
            "openrouter_api_url": "https://openrouter.ai/api/v1/chat/completions",
            "model": "mistralai/mistral-7b-instruct:free",  # Free model
            "max_response_length": 150,  # IRC character limit
            "response_probability": 0.6,  # 60% chance to respond when triggered
            "cooldown_seconds": 30,  # Cooldown between AI responses per user
            "enabled_channels": [],  # Empty list means all channels
            "disabled_channels": [],  # Specific channels to disable
            "trigger_patterns": [
                r'(?i)^({botname}[,:]?)\s+(.+)$',  # Direct messages to bot
                r'(?i)\b({botname})\b.*\?',  # Questions containing bot name
                r'(?i)what do you think\b.*',  # "What do you think" questions
                r'(?i)your opinion\b.*',  # "Your opinion" questions
                r'(?i)tell me about\b.*',  # "Tell me about" requests
            ],
            "ignore_patterns": [
                r'(?i)\b(shut up|be quiet|go away)\b',  # Ignore negative commands
                r'(?i)^\s*$',  # Ignore empty messages
            ]
        }
        
        # State tracking
        self.last_response_time = {}
        self.response_history = {}
        
        # Initialize HTTP client
        self.http_client = None
        
    def load_config(self, bot_config: Dict[str, Any]):
        """Load configuration from bot config"""
        if 'ai_response' in bot_config:
            ai_config = bot_config['ai_response']
            
            # Update our config with any provided values
            for key, value in ai_config.items():
                if key in self.config:
                    self.config[key] = value
                else:
                    logging.warning(f"Unknown AI config key: {key}")
        
        # Validate required configuration
        if not self.config['openrouter_api_key']:
            logging.warning("OpenRouter API key not configured. AI plugin will be disabled.")
            self.enabled = False
        else:
            logging.info("AI Response plugin configured and enabled")
            logging.debug(f"AI config: model={self.config['model']}, max_length={self.config['max_response_length']}")
    
    def _get_bot_names(self, bot) -> List[str]:
        """Get all bot names including aliases"""
        names = [bot.config['nick'].lower()]
        names.extend(alias.lower() for alias in bot.config.get('aliases', []))
        return names
    
    def _is_allowed_channel(self, channel: str) -> bool:
        """Check if AI responses are allowed in this channel"""
        channel_lower = channel.lower()
        
        # Check disabled channels first
        if channel_lower in [c.lower() for c in self.config['disabled_channels']]:
            return False
        
        # Check enabled channels if specified
        if self.config['enabled_channels']:
            return channel_lower in [c.lower() for c in self.config['enabled_channels']]
        
        # If no specific channels configured, allow all
        return True
    
    def _is_on_cooldown(self, nick: str) -> bool:
        """Check if user is on cooldown"""
        nick_lower = nick.lower()
        last_time = self.last_response_time.get(nick_lower, 0)
        return time.time() - last_time < self.config['cooldown_seconds']
    
    def _should_ignore_message(self, message: str) -> bool:
        """Check if message should be ignored based on patterns"""
        for pattern in self.config['ignore_patterns']:
            if re.search(pattern, message):
                return True
        return False
    
    def _is_triggered(self, message: str, bot_names: List[str]) -> bool:
        """Check if message triggers AI response"""
        message_lower = message.lower()
        
        # Check if message is ignored
        if self._should_ignore_message(message):
            return False
        
        # Check trigger patterns
        for pattern in self.config['trigger_patterns']:
            # Replace {botname} placeholder with actual bot names
            for bot_name in bot_names:
                trigger_pattern = pattern.replace('{botname}', re.escape(bot_name))
                if re.search(trigger_pattern, message_lower):
                    return True
        
        return False
    
    def _extract_prompt(self, message: str, bot_names: List[str]) -> str:
        """Extract the actual prompt from the message"""
        message_lower = message.lower()
        
        # Try to find direct messages to bot
        for bot_name in bot_names:
            # Pattern: "botname: message" or "botname, message" or "botname message"
            pattern = rf'^(?:{re.escape(bot_name)}[,:]?\s*)(.+)$'
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no direct pattern found, return the whole message
        return message
    
    def _truncate_response(self, response: str) -> str:
        """Truncate response to fit IRC limits"""
        max_length = self.config['max_response_length']
        
        if len(response) <= max_length:
            return response
        
        # Try to find a natural breaking point
        truncated = response[:max_length]
        
        # Find last space or punctuation to avoid cutting words
        last_space = max(truncated.rfind(' '), truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
        
        if last_space > max_length // 2:  # Don't truncate too much
            truncated = truncated[:last_space]
        
        # Add ellipsis if we truncated
        if len(truncated) < len(response):
            truncated += "..."
        
        return truncated.strip()
    
    async def _call_openrouter_api(self, prompt: str, context: str = "") -> str:
        """Call OpenRouter API to get AI response"""
        if not self.http_client:
            self.http_client = httpx.AsyncClient()
        
        try:
            # Build the full prompt with context
            full_prompt = f"{context}\n\nUser: {prompt}"
            
            headers = {
                "Authorization": f"Bearer {self.config['openrouter_api_key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.config['model'],
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a friendly IRC bot. Keep responses concise, conversational, and appropriate for chat rooms. Avoid being overly formal or verbose."
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.7,
                "top_p": 0.9,
            }
            
            logging.debug(f"Calling OpenRouter API with prompt: {prompt[:50]}...")
            
            response = await self.http_client.post(
                self.config['openrouter_api_url'],
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'choices' in data and len(data['choices']) > 0:
                ai_response = data['choices'][0]['message']['content'].strip()
                logging.debug(f"OpenRouter response: {ai_response[:100]}...")
                return ai_response
            else:
                logging.warning(f"Unexpected OpenRouter response format: {data}")
                return "I'm not sure how to respond to that."
                
        except httpx.HTTPStatusError as e:
            logging.error(f"OpenRouter API error: {e}")
            return "Sorry, I'm having trouble connecting to my brain right now."
        except httpx.RequestError as e:
            logging.error(f"OpenRouter request failed: {e}")
            return "My brain seems to be offline. Try again later?"
        except Exception as e:
            logging.error(f"Unexpected error calling OpenRouter: {e}")
            return "Something went wrong with my AI processing."
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Handle messages and provide AI responses when appropriate"""
        
        # Check if plugin is enabled
        if not self.enabled:
            return False
        
        # Check if channel is allowed
        if not self._is_allowed_channel(channel):
            logging.debug(f"AI responses disabled in channel: {channel}")
            return False
        
        # Check cooldown
        if self._is_on_cooldown(nick):
            logging.debug(f"User {nick} is on cooldown for AI responses")
            return False
        
        # Get bot names
        bot_names = self._get_bot_names(bot)
        
        # Check if message triggers AI response
        if not self._is_triggered(message, bot_names):
            return False
        
        # Random chance to respond
        if random.random() > self.config['response_probability']:
            return False
        
        # Extract the actual prompt
        prompt = self._extract_prompt(message, bot_names)
        
        # Get some context from recent messages if available
        context = ""
        if hasattr(bot, 'response_history') and channel in bot.response_history:
            recent_messages = bot.response_history[channel][-3:]  # Last 3 messages
            context = "Recent conversation: " + " | ".join(recent_messages)
        
        # Call OpenRouter API
        try:
            ai_response = await self._call_openrouter_api(prompt, context)
            
            # Truncate response to fit IRC limits
            final_response = self._truncate_response(ai_response)
            
            # Send response
            await bot.privmsg(channel, final_response)
            
            # Update cooldown and history
            self.last_response_time[nick.lower()] = time.time()
            
            # Store response in history for context
            if channel not in self.response_history:
                self.response_history[channel] = []
            self.response_history[channel].append(f"{nick}: {message}")
            self.response_history[channel].append(f"Bot: {final_response}")
            
            # Keep history limited
            if len(self.response_history[channel]) > 10:
                self.response_history[channel] = self.response_history[channel][-10:]
            
            logging.info(f"[{channel}] AI responded to {nick}: {final_response[:50]}...")
            return True
            
        except Exception as e:
            logging.error(f"Error in AI response handling: {e}")
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
    
    async def cleanup(self):
        """Clean up resources"""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None