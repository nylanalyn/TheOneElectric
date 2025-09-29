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
    
    async def send(self, message: str):
        """Send raw IRC message"""
        if self.writer:
            self.writer.write(f"{message}\r\n".encode())
            await self.writer.drain()
            logging.debug(f"SENT: {message}")
            
            # Also log to file if configured
            if hasattr(self, 'irc_log_file') and self.irc_log_file:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open(self.irc_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] SENT: {message}\n")
    
    async def privmsg(self, target: str, message: str):
        """Send PRIVMSG"""
        await self.send(f"PRIVMSG {target} :{message}")
    
    async def action(self, target: str, message: str):
        """Send ACTION (/me)"""
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
        logging.debug(f"RECV: {line}")
        
        # Also log to file if configured
        if hasattr(self, 'irc_log_file') and self.irc_log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.irc_log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] RECV: {line}\n")
        
        # Handle PING
        if line.startswith('PING'):
            await self.send(f"PONG {line.split(':', 1)[1]}")
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

@dataclass
class ChannelState:
    """Track channel state"""
    name: str
    users: Dict[str, UserState] = field(default_factory=dict)
    last_activity: float = field(default_factory=time.time)
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
        # Load configuration
        self.config_file = Path(config_file)
        self.config = self.load_config()
        
        super().__init__(self.config)
        
        # Bot state
        self.channels_state: Dict[str, ChannelState] = {}
        self.plugins: List[Plugin] = []
        self.start_time = time.time()
        
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
                "enabled": ["shutup", "admin", "greetings", "random_responses", "actions", "questions", "kill", "random_chatter", "cancel", "quotes", "projectile", "stealth", "decision", "makeme"],
                "disabled": []
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
                    default_config.update(config)
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
        plugins_dir = Path("plugins")
        
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
        plugins_dir = Path("plugins")
        for plugin_file in plugins_dir.glob("*.py"):
            module_name = plugin_file.stem
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
        
        # Reload plugins
        self.load_plugins()
        logging.info("Plugin reload complete")
    
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
        
        # Update user state
        user_state = self.get_user_state(channel, nick)
        user_state.last_seen = time.time()
        
        # Reset daily greeting flag if it's a new day
        if datetime.now().date() != datetime.fromtimestamp(user_state.last_seen).date():
            user_state.greeted_today = False
        
        logging.info(f"[{channel}] <{nick}> {message}")
        
        # Log to IRC file as well
        if hasattr(self, 'irc_log_file') and self.irc_log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.irc_log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] [{channel}] <{nick}> {message}\n")
        
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
    
    def contains_other_usernames(self, channel: str, speaker: str, message: str) -> bool:
        """Check if message contains usernames other than the bot's and speaker's"""
        # Bot names (including aliases)
        bot_names = [self.config['nick'].lower()] + [alias.lower() for alias in self.config.get('aliases', [])]
        
        # Don't filter if this looks like a command to the bot
        # Commands typically have bot name at the start
        message_lower = message.lower()
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
        
        # Process through plugins
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    await plugin.handle_join(self, nick, channel)
                except Exception as e:
                    logging.error(f"Error in plugin {plugin.name}: {e}")
    
    async def handle_part(self, nick: str, channel: str, reason: str):
        """Handle user parts"""
        if nick == self.config['nick']:
            return
        
        logging.info(f"[{channel}] {nick} left ({reason})")
        
        # Process through plugins
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    await plugin.handle_part(self, nick, channel, reason)
                except Exception as e:
                    logging.error(f"Error in plugin {plugin.name}: {e}")
    
    async def run(self):
        """Main bot loop"""
        try:
            await self.connect()
            await self.listen()
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
        except Exception as e:
            logging.error(f"Bot error: {e}")
        finally:
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()

async def main():
    """Entry point"""
    bot = PyMotion()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
