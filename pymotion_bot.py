#!/usr/bin/env python3
"""
PyMotion - A modern Python IRC bot inspired by bMotion
Because TCL is awful and life is too short for eggdrop
"""

import asyncio
import re
import random
import json
import time
import logging
import ssl
import base64
import importlib
import importlib.util
import inspect
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from pathlib import Path
import aiofiles

# Simple IRC client implementation
class IRCBot:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.reader = None
        self.writer = None
        self.channels = set()
        self.connected = False
        self.registered = False
        self.sasl_in_progress = False
        self.exit_code = 0

        # Token-bucket rate limiter for outgoing messages
        self._send_tokens = 3.0       # current tokens (messages we can send now)
        self._send_max_tokens = 5.0   # burst capacity
        self._send_rate = 2.0         # tokens refilled per second
        self._send_last_refill = time.time()
        
    async def connect(self):
        """Connect to IRC server with SSL support"""
        try:
            # Set up SSL context if enabled
            ssl_context = None
            if self.config.get('ssl', True):  # Default to SSL
                ssl_context = ssl.create_default_context()
                # For self-signed certs or testing, you might want:
                # ssl_context.check_hostname = False
                # ssl_context.verify_mode = ssl.CERT_NONE
            
            port = self.config.get('port', 6697 if ssl_context else 6667)
            
            self.reader, self.writer = await asyncio.open_connection(
                self.config['server'], 
                port,
                ssl=ssl_context
            )
            self.connected = True
            
            # Send connection sequence
            await self.send(f"NICK {self.config['nick']}")
            await self.send(f"USER {self.config['nick']} 0 * :{self.config['realname']}")
            
            # Request capabilities if using SASL
            if self.config.get('sasl', {}).get('enabled', False):
                await self.send("CAP LS 302")
            
            ssl_status = "with SSL" if ssl_context else "without SSL"
            logging.info(f"Connected to {self.config['server']}:{port} {ssl_status}")
            
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            raise
    
    @staticmethod
    def _redact_sensitive(message: str) -> str:
        """Redact credentials from a log line."""
        if message.startswith("AUTHENTICATE ") and message != "AUTHENTICATE PLAIN":
            return "AUTHENTICATE [REDACTED]"
        if "NickServ" in message and "IDENTIFY" in message:
            return "PRIVMSG NickServ :IDENTIFY [REDACTED]"
        return message

    async def send(self, message: str):
        """Send raw IRC message with token-bucket rate limiting."""
        if self.writer:
            # Refill tokens based on elapsed time
            now = time.time()
            elapsed = now - self._send_last_refill
            self._send_tokens = min(self._send_max_tokens,
                                    self._send_tokens + elapsed * self._send_rate)
            self._send_last_refill = now

            # Wait if no tokens available
            if self._send_tokens < 1.0:
                wait = (1.0 - self._send_tokens) / self._send_rate
                await asyncio.sleep(wait)
                self._send_tokens = 1.0
                self._send_last_refill = time.time()

            self._send_tokens -= 1.0

            self.writer.write(f"{message}\r\n".encode())
            await self.writer.drain()
            log_message = self._redact_sensitive(message)
            logging.debug(f"SENT: {log_message}")

            # Also log to file if configured
            if hasattr(self, 'irc_log_file') and self.irc_log_file:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                async with aiofiles.open(self.irc_log_file, 'a') as f:
                    await f.write(f"[{timestamp}] SENT: {log_message}\n")
    
    async def privmsg(self, target: str, message: str):
        """Send PRIVMSG, truncating if it would exceed IRC line limits."""
        # IRC line limit is 512 bytes including CRLF; leave room for protocol overhead
        max_msg_len = 400
        if len(message.encode('utf-8')) > max_msg_len:
            message = message[:max_msg_len].rsplit(' ', 1)[0] + "..."
        await self.send(f"PRIVMSG {target} :{message}")

    async def action(self, target: str, message: str):
        """Send ACTION (/me), truncating if it would exceed IRC line limits."""
        max_msg_len = 390  # slightly less to account for \001ACTION\001 wrapper
        if len(message.encode('utf-8')) > max_msg_len:
            message = message[:max_msg_len].rsplit(' ', 1)[0] + "..."
        await self.send(f"PRIVMSG {target} :\001ACTION {message}\001")
    
    async def join_channel(self, channel: str, key: str = None):
        """Join a channel with optional key"""
        if key:
            await self.send(f"JOIN {channel} {key}")
        else:
            await self.send(f"JOIN {channel}")
        self.channels.add(channel)
    
    async def set_mode(self, target: str, modes: str):
        """Set modes on target (user or channel)"""
        await self.send(f"MODE {target} {modes}")
    
    async def handle_sasl_auth(self):
        """Handle SASL PLAIN authentication"""
        sasl_config = self.config.get('sasl', {})
        if not sasl_config.get('enabled', False):
            return
            
        username = sasl_config.get('username', '')
        password = sasl_config.get('password', '')
        
        if not username or not password:
            logging.error("SASL enabled but username/password not provided")
            return
        
        # SASL PLAIN: \0username\0password
        auth_string = f"\0{username}\0{password}"
        auth_b64 = base64.b64encode(auth_string.encode()).decode()
        
        await self.send(f"AUTHENTICATE {auth_b64}")
        self.sasl_in_progress = True
    
    async def listen(self):
        """Main message loop"""
        buffer = ""
        while self.connected:
            try:
                data = await self.reader.read(4096)
                if not data:
                    break
                    
                buffer += data.decode('utf-8', errors='ignore')
                lines = buffer.split('\r\n')
                buffer = lines[-1]  # Keep incomplete line
                
                for line in lines[:-1]:
                    if line:
                        await self.handle_message(line)
                        
            except Exception as e:
                logging.error(f"Error in listen loop: {e}")
                break
    
    async def handle_message(self, line: str):
        """Override this to handle IRC messages"""
        log_line = self._redact_sensitive(line)
        logging.debug(f"RECV: {log_line}")

        # Also log to file if configured
        if hasattr(self, 'irc_log_file') and self.irc_log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            async with aiofiles.open(self.irc_log_file, 'a') as f:
                await f.write(f"[{timestamp}] RECV: {log_line}\n")

        # Handle PING — support both "PING :token" and "PING token"
        if line.startswith('PING'):
            token = line.split(':', 1)[1] if ':' in line else line.split(' ', 1)[1]
            await self.send(f"PONG :{token}")
            return
            
        # Parse IRC message
        if line.startswith(':'):
            parts = line[1:].split(' ', 3)
            if len(parts) >= 3:
                source = parts[0]
                command = parts[1]
                params = parts[2:]
                
                await self.on_message(source, command, params)
        else:
            # Handle messages without source (like CAP, AUTHENTICATE)
            parts = line.split(' ', 2)
            if len(parts) >= 2:
                command = parts[0]
                params = parts[1:]
                await self.on_message("", command, params)
    
    async def on_message(self, source: str, command: str, params: List[str]):
        """Override this to handle parsed IRC messages"""
        pass

@dataclass
class UserState:
    """Track user state and relationships"""
    nick: str
    friendship: int = 0
    last_seen: float = field(default_factory=time.time)
    greeted_today: bool = False
    last_interaction: str = ""
    mood_modifier: float = 0.0
    kill_count: int = 0
    shutup_count: int = 0
    last_shutup_time: float = 0.0

@dataclass
class ChannelState:
    """Track channel state"""
    name: str
    users: Dict[str, UserState] = field(default_factory=dict)
    last_activity: float = field(default_factory=time.time)
    previous_activity: float = field(default_factory=time.time)
    topic: str = ""
    mood: float = 0.5  # 0.0 = depressed, 1.0 = euphoric

class Plugin:
    """Base class for bot plugins"""
    def __init__(self, name: str, priority: int = 50):
        self.name = name
        self.priority = priority
        self.enabled = True
    
    async def handle_message(self, bot: 'PyMotion', nick: str, channel: str, message: str) -> bool:
        """Return True if plugin handled the message and no further processing needed"""
        return False
    
    async def handle_action(self, bot: 'PyMotion', nick: str, channel: str, action: str) -> bool:
        """Handle /me actions"""
        return False
    
    async def handle_join(self, bot: 'PyMotion', nick: str, channel: str):
        """Handle user joins"""
        pass
    
    async def handle_part(self, bot: 'PyMotion', nick: str, channel: str, reason: str):
        """Handle user parts"""
        pass

class PyMotion(IRCBot):
    """Main bot class"""
    
    def __init__(self, config_file: str = "pymotion.json"):
        # Load configuration — resolve relative to script location
        self._base_dir = Path(__file__).resolve().parent
        self.config_file = self._base_dir / config_file
        self.config = self.load_config()
        
        super().__init__(self.config)
        
        # Bot state
        self.channels_state: Dict[str, ChannelState] = {}
        self.plugins: List[Plugin] = []
        self.start_time = time.time()
        self.background_tasks: set[asyncio.Task] = set()
        self.opinions: Dict[str, Dict] = {}  # {"topic": {"sentiment": float, "mentions": int, "last_mentioned": float, "formed_at": float}}
        
        # Set up logging first
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Set up IRC logging to file if configured
        self.irc_log_file = self.config.get('irc_log_file', 'irc_traffic.log')
        if self.irc_log_file:
            logging.info(f"IRC traffic will be logged to: {self.irc_log_file}")
        
        # Initialize plugins
        self.load_plugins()
    
    def create_background_task(self, coro, name: str | None = None) -> asyncio.Task:
        task = asyncio.create_task(coro, name=name)
        self.background_tasks.add(task)
        
        def _on_done(done_task: asyncio.Task):
            self.background_tasks.discard(done_task)
            try:
                done_task.result()
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logging.error(f"Background task failed ({getattr(done_task, 'get_name', lambda: 'task')()}): {e}")
        
        task.add_done_callback(_on_done)
        return task
    
    async def _cancel_background_tasks(self):
        if not self.background_tasks:
            return
        tasks = list(self.background_tasks)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self.background_tasks.clear()
    
    async def start_plugins(self):
        """Start plugins that expose a start() hook."""
        for plugin in self.plugins:
            if not plugin.enabled:
                continue
            start_fn = getattr(plugin, "start", None)
            if not start_fn:
                continue
            try:
                result = start_fn(self)
                if inspect.isawaitable(result):
                    await result
            except Exception as e:
                logging.error(f"Error starting plugin {plugin.name}: {e}")
    
    async def reload_config_and_plugins(self):
        """Reload config and plugins with cleanup, for hot-reload."""
        await self._cancel_background_tasks()
        for plugin in self.plugins:
            if hasattr(plugin, "cleanup"):
                try:
                    await plugin.cleanup()
                except Exception as e:
                    logging.error(f"Error cleaning up plugin {plugin.name}: {e}")
        
        self.config = self.load_config()
        self.load_plugins()
        await self.start_plugins()
    
    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """Recursively merge override into base, preserving nested keys."""
        merged = base.copy()
        for key, value in override.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = PyMotion._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        default_config = {
            "server": "irc.libera.chat",
            "port": 6697,  # Default SSL port
            "ssl": True,   # Enable SSL by default
            "nick": "PyMotion",
            "aliases": ["pybot", "motion"],  # Additional nicknames bot responds to
            "realname": "PyMotion - A Python IRC bot",
            "channels": [
                {"name": "#test", "key": None},
                {"name": "#bots", "key": None}
            ],
            "sasl": {
                "enabled": False,
                "username": "",
                "password": ""
            },
            "modes": "+B",  # User modes to set on connect
            "irc_log_file": "irc_traffic.log",  # Log all IRC traffic to file
            "log_level": "DEBUG",  # Set to DEBUG to see everything
            "plugins": {
                "enabled": ["shutup", "admin", "greetings", "random_responses", "actions", "questions", "kill", "random_chatter", "cancel", "quotes", "projectile", "stealth", "decision", "makeme", "liljon", "ai_response"],
                "disabled": []
            },
            "ai_response": {
                "openrouter_api_key_env": "OPENROUTER_API_KEY",  # env var name for API key
                "openrouter_api_url": "https://openrouter.ai/api/v1/chat/completions",
                "model": "mistralai/mistral-7b-instruct:free",
                "max_response_length": 150,
                "response_probability": 0.6,
                "cooldown_seconds": 30,
                "enabled_channels": [],  # Empty = all channels
                "disabled_channels": []
            },
            "admins": [],  # Add your IRC nick here for admin commands
            "personality": {
                "chattiness": 0.3,
                "friendliness": 0.8,
                "randomness": 0.5
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    default_config = self._deep_merge(default_config, config)
            except Exception as e:
                logging.error(f"Error loading config: {e}")
        else:
            # Create default config file
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logging.info(f"Created default config file: {self.config_file}")
        
        return default_config
    
    def load_plugins(self):
        """Load plugins from plugins directory"""
        self.plugins = []
        plugins_dir = self._base_dir / "plugins"
        
        # Create plugins directory if it doesn't exist
        if not plugins_dir.exists():
            plugins_dir.mkdir()
            logging.info("Created plugins directory")
            return
        
        # Get enabled plugins from config
        enabled_plugins = self.config.get('plugins', {}).get('enabled', [])
        disabled_plugins = self.config.get('plugins', {}).get('disabled', [])
        
        # Scan for plugin files
        plugin_files = list(plugins_dir.glob("*.py"))
        if not plugin_files:
            logging.warning("No plugins found in plugins directory")
            return
        
        # Load each plugin file
        for plugin_file in plugin_files:
            plugin_name = plugin_file.stem
            
            # Skip disabled plugins
            if plugin_name in disabled_plugins:
                logging.info(f"Skipping disabled plugin: {plugin_name}")
                continue
            
            # Skip if not in enabled list (if specified)
            if enabled_plugins and plugin_name not in enabled_plugins:
                logging.debug(f"Plugin {plugin_name} not in enabled list, skipping")
                continue
            
            try:
                # Clear stale module entry before reimporting (hot-reload safe)
                if plugin_name in sys.modules:
                    del sys.modules[plugin_name]

                # Import the plugin module
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find plugin classes in the module
                plugin_classes = []
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj):
                        logging.debug(f"Found class {name} in {plugin_file}")
                        
                        # Skip main bot classes
                        if obj.__name__ in ['PyMotion', 'IRCBot', 'Plugin']:
                            logging.debug(f"Skipping bot/base class {name}")
                            continue
                        
                        # Check if it has the required interface
                        if (hasattr(obj, 'handle_message') and  # Must have handle_message method
                            hasattr(obj, '__init__') and        # Must be instantiable
                            obj.__module__ == module.__name__):  # Must be defined in this module
                            plugin_classes.append(obj)
                            logging.debug(f"Class {name} qualifies as plugin")
                        else:
                            logging.debug(f"Class {name} missing required methods or wrong module")
                            logging.debug(f"  has handle_message: {hasattr(obj, 'handle_message')}")
                            logging.debug(f"  has __init__: {hasattr(obj, '__init__')}")
                            logging.debug(f"  module match: {obj.__module__} == {module.__name__}")
                    else:
                        logging.debug(f"Found non-class {name} in {plugin_file}: {type(obj)}")
                
                # Instantiate plugin classes
                for plugin_class in plugin_classes:
                    try:
                        plugin_instance = plugin_class()
                        
                        # Call load_config if it exists
                        if hasattr(plugin_instance, 'load_config'):
                            plugin_instance.load_config(self.config)
                        
                        self.plugins.append(plugin_instance)
                        logging.info(f"Loaded plugin: {plugin_instance.name} (priority: {plugin_instance.priority})")
                    except Exception as e:
                        logging.error(f"Error instantiating plugin {plugin_class.__name__}: {e}")
                
                if not plugin_classes:
                    logging.warning(f"No plugin classes found in {plugin_file}")
                    
            except Exception as e:
                logging.error(f"Error loading plugin {plugin_file}: {e}")
        
        # Sort plugins by priority (higher first)
        self.plugins.sort(key=lambda p: p.priority, reverse=True)
        logging.info(f"Loaded {len(self.plugins)} plugins total")
        
        # Log plugin order
        for plugin in self.plugins:
            logging.debug(f"Plugin order: {plugin.name} (priority: {plugin.priority})")
    
    def reload_plugins(self):
        """Reload all plugins - useful for development"""
        logging.info("Reloading plugins...")
        # Clear module cache for plugin modules
        plugins_dir = self._base_dir / "plugins"
        for plugin_file in plugins_dir.glob("*.py"):
            module_name = plugin_file.stem
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
        
        # Reload plugins
        self.load_plugins()
        logging.info("Plugin reload complete")
    
    def _state_file(self) -> Path:
        return self._base_dir / "bot_state.json"

    def save_state(self):
        """Persist user/channel state to disk."""
        data: Dict[str, Any] = {}
        for ch_name, ch_state in self.channels_state.items():
            users = {}
            for nick, u in ch_state.users.items():
                users[nick] = {
                    "friendship": u.friendship,
                    "last_seen": u.last_seen,
                    "greeted_today": u.greeted_today,
                    "mood_modifier": u.mood_modifier,
                    "kill_count": u.kill_count,
                    "shutup_count": u.shutup_count,
                    "last_shutup_time": u.last_shutup_time,
                }
            data[ch_name] = {
                "mood": ch_state.mood,
                "topic": ch_state.topic,
                "users": users,
            }
        data["_opinions"] = self.opinions
        tmp = str(self._state_file()) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        import os
        os.replace(tmp, self._state_file())
        logging.debug("Bot state saved to disk")

    def load_state(self):
        """Load persisted user/channel state from disk."""
        path = self._state_file()
        if not path.exists():
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Load opinions
            if "_opinions" in data:
                self.opinions = data.pop("_opinions")
            for ch_name, ch_data in data.items():
                if not isinstance(ch_data, dict):
                    continue
                ch_state = self.get_channel_state(ch_name)
                ch_state.mood = ch_data.get("mood", 0.5)
                ch_state.topic = ch_data.get("topic", "")
                for nick, u_data in ch_data.get("users", {}).items():
                    u_state = self.get_user_state(ch_name, nick)
                    u_state.friendship = u_data.get("friendship", 0)
                    u_state.last_seen = u_data.get("last_seen", time.time())
                    u_state.greeted_today = u_data.get("greeted_today", False)
                    u_state.mood_modifier = u_data.get("mood_modifier", 0.0)
                    u_state.kill_count = u_data.get("kill_count", 0)
                    u_state.shutup_count = u_data.get("shutup_count", 0)
                    u_state.last_shutup_time = u_data.get("last_shutup_time", 0.0)
            logging.info(f"Loaded bot state from {path}")
        except Exception as e:
            logging.error(f"Error loading bot state: {e}")

    async def _periodic_state_save(self):
        """Background task that saves state every 5 minutes."""
        try:
            while True:
                await asyncio.sleep(300)
                self.save_state()
        except asyncio.CancelledError:
            self.save_state()  # one final save on shutdown

    def get_channel_state(self, channel: str) -> ChannelState:
        """Get or create channel state"""
        if channel not in self.channels_state:
            self.channels_state[channel] = ChannelState(name=channel)
        return self.channels_state[channel]
    
    def get_user_state(self, channel: str, nick: str) -> UserState:
        """Get or create user state"""
        channel_state = self.get_channel_state(channel)
        if nick not in channel_state.users:
            channel_state.users[nick] = UserState(nick=nick)
        return channel_state.users[nick]
    
    # Stopwords for topic tracking
    _STOPWORDS = frozenset({
        "this", "that", "with", "from", "have", "been", "were", "they",
        "their", "them", "will", "would", "could", "should", "about",
        "what", "when", "where", "which", "there", "these", "those",
        "then", "than", "other", "into", "over", "just", "also", "some",
        "more", "very", "only", "even", "back", "after", "before",
        "being", "does", "doing", "each", "here", "most", "much",
        "your", "like", "make", "know", "think", "want", "look",
        "time", "well", "come", "made", "find", "said", "http",
        "https", "www", "really", "going", "thing", "things", "gonna",
        "yeah", "okay", "right", "sure", "maybe", "still", "never",
    })

    def get_friendship_tier(self, channel: str, nick: str) -> str:
        """Get friendship tier label for a user."""
        user = self.get_user_state(channel, nick)
        f = user.friendship
        if f <= -10:
            return "hostile"
        elif f <= -1:
            return "cold"
        elif f <= 4:
            return "neutral"
        elif f <= 14:
            return "friendly"
        else:
            return "bestie"

    def get_time_personality(self) -> dict:
        """Return personality modifiers based on time of day and day of week."""
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0=Monday, 6=Sunday

        energy = 1.0
        grumpiness = 0.0
        snark = 0.0
        flavor = ""

        if 1 <= hour <= 5:
            energy = 0.5
            grumpiness = 0.3
            snark = 0.2
            flavor = "*yawns aggressively*"
        elif 6 <= hour <= 8:
            energy = 0.7
            grumpiness = 0.1
            snark = 0.1
            flavor = "*hasn't had coffee yet*"
        elif 10 <= hour <= 16:
            energy = 1.2
            grumpiness = 0.0
            flavor = ""
        elif weekday == 4 and hour >= 17:  # Friday evening
            energy = 1.5
            grumpiness = 0.0
            snark = 0.1
            flavor = "It's FRIDAY!"

        # Weekends
        if weekday >= 5:
            energy = max(energy, 1.1)
            grumpiness = max(grumpiness - 0.1, 0.0)
            if not flavor:
                flavor = ""

        return {
            "energy": energy,
            "grumpiness": grumpiness,
            "snark": snark,
            "flavor": flavor,
        }

    def track_topic(self, channel: str, nick: str, message: str):
        """Extract notable words from a message and form opinions over time."""
        bot_names = {self.config['nick'].lower()} | {a.lower() for a in self.config.get('aliases', [])}
        channel_state = self.get_channel_state(channel)
        nicks_lower = {n.lower() for n in channel_state.users}
        nicks_lower.add(nick.lower())

        words = re.findall(r'[a-zA-Z]{4,}', message.lower())
        now = time.time()
        for word in words:
            if word in self._STOPWORDS or word in bot_names or word in nicks_lower:
                continue
            if word not in self.opinions:
                self.opinions[word] = {
                    "sentiment": 0.0,
                    "mentions": 0,
                    "last_mentioned": now,
                    "formed_at": 0.0,
                }
            entry = self.opinions[word]
            entry["mentions"] += 1
            entry["last_mentioned"] = now
            # Form opinion after 8 mentions if not already formed
            if entry["mentions"] >= 8 and entry["formed_at"] == 0.0:
                entry["sentiment"] = round(random.uniform(-0.8, 0.8), 2)
                entry["formed_at"] = now

        # Cap at 200 entries, prune least-recent
        if len(self.opinions) > 200:
            sorted_topics = sorted(self.opinions.items(), key=lambda x: x[1]["last_mentioned"])
            to_remove = len(self.opinions) - 200
            for topic, _ in sorted_topics[:to_remove]:
                del self.opinions[topic]

    async def on_message(self, source: str, command: str, params: List[str]):
        """Handle IRC messages"""
        if command == "CAP":
            # Handle capability negotiation
            if len(params) >= 2 and params[1] == "LS":
                # Server is listing capabilities
                caps = " ".join(params[2:]).replace(":", "")
                if "sasl" in caps.lower():
                    await self.send("CAP REQ :sasl")
                else:
                    await self.send("CAP END")
            elif len(params) >= 2 and params[1] == "ACK":
                # Server acknowledged capability request
                if "sasl" in " ".join(params[2:]).lower():
                    await self.send("AUTHENTICATE PLAIN")
                else:
                    await self.send("CAP END")
            elif len(params) >= 2 and params[1] == "NAK":
                # Server rejected capability
                await self.send("CAP END")
        
        elif command == "AUTHENTICATE":
            if len(params) >= 1 and params[0] == "+":
                await self.handle_sasl_auth()
        
        elif command == "903":  # SASL authentication successful
            logging.info("SASL authentication successful")
            await self.send("CAP END")
            self.sasl_in_progress = False
        
        elif command == "904" or command == "905":  # SASL authentication failed
            logging.error("SASL authentication failed")
            await self.send("CAP END")
            self.sasl_in_progress = False
        
        elif command == "433":  # ERR_NICKNAMEINUSE
            current_nick = self.config['nick']
            new_nick = current_nick + "_"
            logging.warning(f"Nick '{current_nick}' is in use, trying '{new_nick}'")
            self.config['nick'] = new_nick
            await self.send(f"NICK {new_nick}")

        elif command == "001":  # Welcome message
            logging.info("Received 001 welcome message - IRC registration complete")
            self.registered = True
            
            # Identify with NickServ if configured
            nickserv_config = self.config.get('nickserv', {})
            if nickserv_config.get('enabled', False):
                password = nickserv_config.get('password', '')
                if password:
                    # Send IDENTIFY command to NickServ
                    await self.privmsg('NickServ', f'IDENTIFY {password}')
                    logging.info("Sent IDENTIFY command to NickServ")
                    
                    # Wait a moment for NickServ to respond before continuing
                    await asyncio.sleep(2)
            
            # Set user modes if configured
            if self.config.get('modes'):
                await self.set_mode(self.config['nick'], self.config['modes'])
                logging.info(f"Set modes: {self.config['modes']}")
            
            # Join channels
            channels = self.config.get('channels', [])
            for channel_config in channels:
                if isinstance(channel_config, str):
                    # Old format: just channel name
                    await self.join_channel(channel_config)
                elif isinstance(channel_config, dict):
                    # New format: {"name": "#channel", "key": "password"}
                    channel = channel_config.get('name')
                    key = channel_config.get('key')
                    if channel:
                        await self.join_channel(channel, key)
            
            await self.start_plugins()
            self.load_state()
            self.create_background_task(
                self._periodic_state_save(), name="periodic_state_save"
            )

        elif command == "PRIVMSG":
            if len(params) >= 2:
                target = params[0]
                message = params[1] if params[1].startswith(':') else f":{params[1]}"
                
                # The message text should have the leading colon from IRC protocol
                # Strip it here before processing
                message = message.lstrip(':')
                
                # Parse nick from source
                nick = source.split('!')[0] if '!' in source else source
                
                # Determine if this is a channel or private message
                if target.startswith('#'):
                    channel = target
                else:
                    channel = nick  # Private message
                
                # Handle CTCP ACTION (/me)
                if message.startswith('\001ACTION ') and message.endswith('\001'):
                    action = message[8:-1]  # Remove \001ACTION and \001
                    await self.handle_action(nick, channel, action)
                else:
                    await self.handle_channel_message(nick, channel, message)
        
        elif command == "JOIN":
            if len(params) >= 1:
                channel = params[0]
                nick = source.split('!')[0] if '!' in source else source
                
                # Add user to channel tracking
                if nick != self.config['nick']:
                    channel_state = self.get_channel_state(channel)
                    if nick not in channel_state.users:
                        channel_state.users[nick] = UserState(nick=nick)
                    logging.debug(f"Added {nick} to {channel} user list")
                
                await self.handle_join(nick, channel)
        
        elif command == "PART":
            if len(params) >= 1:
                channel = params[0]
                reason = params[1] if len(params) > 1 else ""
                nick = source.split('!')[0] if '!' in source else source
                
                # Remove user from channel tracking
                if nick != self.config['nick']:
                    channel_state = self.get_channel_state(channel)
                    if nick in channel_state.users:
                        del channel_state.users[nick]
                        logging.debug(f"Removed {nick} from {channel} user list")
                
                await self.handle_part(nick, channel, reason)
        
        elif command == "QUIT":
            if len(params) >= 1:
                reason = params[0] if len(params) > 0 else ""
                nick = source.split('!')[0] if '!' in source else source
                
                # Remove user from all channel tracking
                if nick != self.config['nick']:
                    for channel_state in self.channels_state.values():
                        if nick in channel_state.users:
                            del channel_state.users[nick]
                            logging.debug(f"Removed {nick} from all channels (quit)")
        
        elif command == "353":  # NAMES reply
            if len(params) >= 4:
                channel = params[2]
                names_list = params[3]
                
                # Parse the names list and add users to channel tracking
                names = names_list.split()
                channel_state = self.get_channel_state(channel)
                
                for name in names:
                    # Remove mode prefixes (@, +, etc.)
                    clean_name = name.lstrip('@+%&~!')
                    if clean_name and clean_name != self.config['nick']:
                        if clean_name not in channel_state.users:
                            channel_state.users[clean_name] = UserState(nick=clean_name)
                
                logging.debug(f"Added {len(names)} users to {channel} from NAMES reply")
    
    async def handle_channel_message(self, nick: str, channel: str, message: str):
        """Handle channel messages"""
        if nick == self.config['nick']:
            return  # Ignore our own messages
        
        now = time.time()
        channel_state = self.get_channel_state(channel)
        channel_state.previous_activity = channel_state.last_activity
        
        # Update user state
        user_state = self.get_user_state(channel, nick)
        old_last_seen = user_state.last_seen
        user_state.last_seen = now

        # Friendship decay: drift toward 0 by 1 per day of absence, cap at -3 per return
        days_away = (now - old_last_seen) / 86400.0
        if days_away >= 1.0 and user_state.friendship != 0:
            decay = min(int(days_away), 3)
            if user_state.friendship > 0:
                user_state.friendship = max(0, user_state.friendship - decay)
            elif user_state.friendship < 0:
                user_state.friendship = min(0, user_state.friendship + decay)

        # Reset daily greeting flag if it's a new day
        if datetime.now().date() != datetime.fromtimestamp(old_last_seen).date():
            user_state.greeted_today = False
        
        logging.info(f"[{channel}] <{nick}> {message}")
        
        # Log to IRC file as well
        if hasattr(self, 'irc_log_file') and self.irc_log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            async with aiofiles.open(self.irc_log_file, 'a') as f:
                await f.write(f"[{timestamp}] [{channel}] <{nick}> {message}\n")
        
        # Check if message contains other usernames (indicating they're talking ABOUT the bot, not TO it)
        contains_others = self.contains_other_usernames(channel, nick, message)
        if contains_others:
            logging.info(f"Username filter blocked message in {channel}: {message}")
            return
        else:
            logging.debug(f"Message passed username filter in {channel}")
        
        # Process through plugins
        plugin_results = []
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    logging.debug(f"[{channel}] Trying plugin {plugin.name} (priority {plugin.priority}) for message: {message[:50]}...")
                    handled = await plugin.handle_message(self, nick, channel, message)
                    plugin_results.append(f"{plugin.name}={handled}")
                    if handled:
                        logging.info(f"[{channel}] Plugin {plugin.name} handled the message")
                        break  # Plugin handled it, stop processing
                    else:
                        logging.debug(f"[{channel}] Plugin {plugin.name} did not handle the message")
                except Exception as e:
                    logging.error(f"[{channel}] Error in plugin {plugin.name}: {e}")
                    import traceback
                    logging.error(traceback.format_exc())
        
        # Log summary of plugin attempts
        logging.debug(f"[{channel}] Plugin results: {', '.join(plugin_results)}")

        # Track topics for opinion formation
        self.track_topic(channel, nick, message)

        channel_state.last_activity = now
    
    def contains_other_usernames(self, channel: str, speaker: str, message: str) -> bool:
        """Check if message contains usernames other than the bot's and speaker's"""
        # Bot names (including aliases)
        bot_names = [self.config['nick'].lower()] + [alias.lower() for alias in self.config.get('aliases', [])]
        
        message_lower = message.lower()
        
        # Special case: Allow "what's my cat's name?" pattern
        if re.search(r"what'?s my cat'?s name", message_lower):
            logging.debug(f"Message matches cat name exception, skipping username filter")
            return False
        
        # Don't filter if this looks like a command to the bot
        # Commands typically have bot name at the start
        for bot_name in bot_names:
            if message_lower.startswith(bot_name) or message_lower.startswith(f"@{bot_name}"):
                logging.debug(f"Message is a command to the bot, skipping username filter")
                return False
        
        # Get list of users in this channel
        channel_state = self.get_channel_state(channel)
        
        # Words in the message
        words = message.lower().split()
        
        # Check each word against known usernames
        for word in words:
            # Clean the word (remove punctuation)
            clean_word = ''.join(c for c in word if c.isalnum())
            if not clean_word:
                continue
                
            # Skip if it's the speaker's name
            if clean_word == speaker.lower():
                continue
                
            # Skip if it's one of the bot's names
            if clean_word in bot_names:
                continue
                
            # Check if it matches any user in the channel
            for username in channel_state.users:
                if clean_word == username.lower():
                    logging.debug(f"Found other username '{username}' in message, filtering out")
                    return True
        
        return False
    
    async def handle_action(self, nick: str, channel: str, action: str):
        """Handle /me actions"""
        if nick == self.config['nick']:
            return
        
        logging.info(f"[{channel}] * {nick} {action}")
        
        # Process through plugins
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    handled = await plugin.handle_action(self, nick, channel, action)
                    if handled:
                        break
                except Exception as e:
                    logging.error(f"Error in plugin {plugin.name}: {e}")
    
    async def handle_join(self, nick: str, channel: str):
        """Handle user joins"""
        if nick == self.config['nick']:
            logging.info(f"Joined {channel}")
            return
        
        logging.info(f"[{channel}] {nick} joined")
        
        # Process through plugins (stop chain if a plugin returns True)
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    handled = await plugin.handle_join(self, nick, channel)
                    if handled:
                        break
                except Exception as e:
                    logging.error(f"Error in plugin {plugin.name}: {e}")

    async def handle_part(self, nick: str, channel: str, reason: str):
        """Handle user parts"""
        if nick == self.config['nick']:
            return

        logging.info(f"[{channel}] {nick} left ({reason})")

        # Process through plugins (stop chain if a plugin returns True)
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    handled = await plugin.handle_part(self, nick, channel, reason)
                    if handled:
                        break
                except Exception as e:
                    logging.error(f"Error in plugin {plugin.name}: {e}")
    
    async def _cleanup(self):
        """Run all cleanup tasks (background tasks, plugins, writer)."""
        try:
            self.save_state()
        except Exception as e:
            logging.error(f"Error saving state: {e}")

        try:
            await self._cancel_background_tasks()
        except Exception as e:
            logging.error(f"Error cancelling background tasks: {e}")

        for plugin in self.plugins:
            if hasattr(plugin, 'cleanup'):
                try:
                    await plugin.cleanup()
                except Exception as e:
                    logging.error(f"Error cleaning up plugin {plugin.name}: {e}")

        try:
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()
        except Exception as e:
            logging.error(f"Error closing writer: {e}")

    async def run(self):
        """Main bot loop with reconnection and exponential backoff."""
        backoff = 1
        max_backoff = 300  # 5 minutes max

        while True:
            try:
                await self.connect()
                backoff = 1  # reset on successful connection
                await self.listen()
            except KeyboardInterrupt:
                logging.info("Bot stopped by user")
                break
            except Exception as e:
                logging.error(f"Bot error: {e}")

            await self._cleanup()

            # If a graceful shutdown was requested, exit now
            if self.exit_code:
                sys.exit(self.exit_code)

            # If connected was explicitly set to False (e.g. admin shutdown), exit
            if not self.connected:
                break

            logging.info(f"Reconnecting in {backoff}s...")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)

        await self._cleanup()

async def main():
    """Entry point"""
    import signal

    bot = PyMotion()

    # Handle SIGTERM for clean systemd shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: _handle_signal(bot))

    await bot.run()


def _handle_signal(bot: PyMotion):
    """Signal handler that triggers graceful shutdown."""
    logging.info("Received shutdown signal")
    bot.connected = False


if __name__ == "__main__":
    asyncio.run(main())
