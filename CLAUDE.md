# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**TheOneElectric** is a PyMotion IRC bot - a modern Python IRC bot inspired by bMotion. It connects to IRC servers (currently configured for Libera.Chat #fractalsignal) with a personality-driven plugin system.

## Commands

### Running the Bot
```bash
python pymotion_bot.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

The bot requires Python 3.13+ and has minimal dependencies (primarily `aiofiles`).

## Architecture

### Core Components

**IRCBot** (pymotion_bot.py:26-179)
- Low-level IRC client with SSL/TLS support
- Handles connection, authentication (SASL), and raw message parsing
- Manages PING/PONG, capability negotiation

**PyMotion** (pymotion_bot.py:223-722)
- Main bot class extending IRCBot
- Loads configuration from `pymotion.json`
- Manages channel/user state tracking via `ChannelState` and `UserState` dataclasses
- Implements plugin system with priority-based message routing
- Filters messages containing other usernames to avoid cross-talk

### Plugin System

Plugins live in `plugins/` directory and inherit from the `Plugin` base class (pymotion_bot.py:200-221).

**Plugin Interface:**
- `handle_message(bot, nick, channel, message) -> bool` - Return True to stop plugin chain
- `handle_action(bot, nick, channel, action) -> bool` - Handle /me actions
- `handle_join(bot, nick, channel)` - Handle user joins
- `handle_part(bot, nick, channel, reason)` - Handle user parts
- `priority` attribute (int) - Higher priority plugins run first (100 = highest)
- `enabled` attribute (bool) - Plugin enable/disable flag

**Plugin Priority Order:**
1. **shutup** (priority 100) - Silences bot for 5 minutes, blocks all other plugins when active
2. **admin** (priority 90) - Admin commands: reload, status
3. **makeme** (priority 60) - Crafts items or transforms users with comedic outcomes
4. Lower priority plugins: greetings, random_responses, actions, questions, kill, random_chatter, cancel, quotes, projectile, stealth, decision

**Key Plugin Mechanics:**
- Plugins are sorted by priority (highest first) in `load_plugins()` (pymotion_bot.py:383)
- Plugin chain stops when any plugin returns True
- Username filter (`contains_other_usernames()`) prevents bot from responding when other users are mentioned
- Bot responds to multiple aliases configured in config (nick + aliases list)

### Configuration

Configuration is loaded from `pymotion.json`:
- IRC connection settings (server, port, SSL, SASL)
- Bot identity (nick, aliases, realname)
- Channel list with optional keys
- Plugin enable/disable lists
- Admin users list
- Personality parameters (chattiness, friendliness, randomness)
- Logging configuration

The bot supports hot-reloading via admin command: `{botnick} reload`

### State Management

**UserState** (pymotion_bot.py:182-189)
- Tracks per-user friendship, last seen time, greeting status
- Associated with specific channels

**ChannelState** (pymotion_bot.py:192-198)
- Maintains user dictionary for each channel
- Tracks channel mood, topic, and activity

State is populated from IRC NAMES replies (353) and JOIN/PART/QUIT events.

### Message Flow

1. Raw IRC line received in `listen()` (pymotion_bot.py:124-143)
2. Parsed in `handle_message()` (pymotion_bot.py:145-175)
3. Routed to `on_message()` (pymotion_bot.py:417-568) based on command
4. PRIVMSG → `handle_channel_message()` (pymotion_bot.py:570-618)
5. Username filter check via `contains_other_usernames()` (pymotion_bot.py:620-660)
6. Plugins iterated in priority order until one returns True

### Logging

- Dual logging: stdout (via logging module) and `irc_traffic.log` file
- Log level configurable via `log_level` in config (default: INFO)
- All IRC traffic (SENT/RECV) logged with timestamps

## Development Notes

### Creating New Plugins

1. Create `plugins/yourplugin.py`
2. Define a class with the plugin interface (must have `handle_message`, `__init__`)
3. Set `name`, `priority`, and `enabled` attributes
4. Return True from `handle_message()` to consume the message
5. Add plugin name to `enabled` list in `pymotion.json`
6. Use `{botnick} reload` command to load without restart

### Testing Plugins

Plugin loading shows detailed debug output at DEBUG log level. Check:
- Plugin class detection logic (pymotion_bot.py:343-365)
- Plugin instantiation (pymotion_bot.py:368-374)
- Plugin order logging (pymotion_bot.py:386-388)

### Bot Name Matching

Plugins typically check if bot is addressed using this pattern:
```python
bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
for bot_name in bot_names:
    if re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\bkeyword\b', message):
        # handle command
```

### Admin Commands

Admins are configured in `pymotion.json` `admins` field. Current admin: "nullveil"

Available admin commands (via admin plugin):
- `{botnick} reload` - Reload config and plugins
- `{botnick} status` - Show uptime, plugin count, channel count
- `{botnick} admin help` - Show admin help
