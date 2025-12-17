"""
AI Response Plugin for PyMotion - Test Version
Integrates with OpenRouter API to provide intelligent responses
This version works without httpx for testing purposes
"""

import re
import random
import time
from typing import List, Dict, Any, Optional
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
            "max_response_attempts": 3,  # Retry to get within max length
            "response_probability": 0.6,  # 60% chance to respond when triggered
            "cooldown_seconds": 30,  # Cooldown between AI responses per user
            "enabled_channels": [],  # Empty list means all channels
            "disabled_channels": [],  # Specific channels to disable
            "trigger_patterns": [
                r'(?i)^@?({botname})[,:]?\s*(.+)$',  # Direct messages to bot (allow "@bot:" and no-space after punctuation)
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
        
        # Mock HTTP client for testing
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
        # Try to find direct messages to bot
        for bot_name in bot_names:
            # Pattern: "botname: message" or "botname, message" or "@botname message"
            pattern = rf'^(?:@?{re.escape(bot_name)}[,:]?\s*)(.+)$'
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

    def _is_response_within_limits(self, response: str) -> bool:
        return len(response) <= self.config['max_response_length']
    
    async def _call_openrouter_api(self, prompt: str, context: str = "") -> str:
        """Mock OpenRouter API call for testing"""
        # In the real version, this would call the actual API
        # For testing, we'll return a mock response
        
        # Simple mock responses based on prompt content
        prompt_lower = prompt.lower()
        
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello there! I'm an AI-powered IRC bot. How can I help you today?"
        elif "python" in prompt_lower:
            return "Python is an awesome programming language! I'm written in Python myself."
        elif "ai" in prompt_lower or "artificial intelligence" in prompt_lower:
            return "AI is fascinating! I use AI to generate intelligent responses like this one."
        elif "opinion" in prompt_lower or "think" in prompt_lower:
            return "That's an interesting question! I think it depends on the context and perspective."
        elif "tell me about" in prompt_lower:
            return "I'd be happy to tell you about that! It's a complex topic with many aspects to consider."
        else:
            return "That's a great question! I'll think about it and get back to you with a thoughtful response."

    async def _get_response_with_retries(self, prompt: str, context: str = "") -> str:
        max_length = int(self.config['max_response_length'])
        max_attempts = max(1, int(self.config.get("max_response_attempts", 3)))

        last_response: Optional[str] = None
        for attempt in range(1, max_attempts + 1):
            if attempt == 1:
                attempt_prompt = prompt
            else:
                prev_len = len(last_response) if last_response is not None else 0
                attempt_prompt = (
                    f"{prompt}\n\n"
                    f"Constraint: Reply in {max_length} characters or fewer.\n"
                    f"Your previous reply was {prev_len} characters.\n"
                    "Return ONLY the corrected shorter reply."
                )

            last_response = await self._call_openrouter_api(attempt_prompt, context)
            if self._is_response_within_limits(last_response):
                return last_response

        return last_response or "I'm not sure how to respond to that."
    
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
        
        # Call OpenRouter API (mock version)
        try:
            ai_response = await self._get_response_with_retries(prompt, context)
            final_response = ai_response if self._is_response_within_limits(ai_response) else self._truncate_response(ai_response)
            
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
        # No actual cleanup needed for mock version
        pass
