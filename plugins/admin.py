"""
Admin Plugin for PyMotion
Administrative commands for managing the bot
"""

import re
import logging

class AdminPlugin:
    """Handle admin commands like reload"""
    
    def __init__(self):
        self.name = "admin"
        self.priority = 90  # High priority
        self.enabled = True
    
    async def handle_message(self, bot, nick: str, channel: str, message: str) -> bool:
        """Handle admin commands"""
        bot_names = [bot.config['nick'].lower()] + [alias.lower() for alias in bot.config.get('aliases', [])]
        
        # Check if user is an admin (you can configure this)
        admins = bot.config.get('admins', [])
        is_admin = nick in admins
        
        for bot_name in bot_names:
            # Reload command
            if re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\breload\b', message):
                if not is_admin:
                    await bot.privmsg(channel, f"{nick}: Sorry, only admins can use that command!")
                    return True
                
                try:
                    await bot.privmsg(channel, "Reloading configuration and plugins...")
                    old_config = bot.config.copy()
                    await bot.reload_config_and_plugins()
                    
                    await bot.privmsg(channel, f"✅ Reload complete! Loaded {len(bot.plugins)} plugins.")
                    logging.info(f"Bot reloaded by {nick}")
                    
                except Exception as e:
                    await bot.privmsg(channel, f"❌ Reload failed: {e}")
                    logging.error(f"Reload error: {e}")
                    # Restore old config if reload failed
                    bot.config = old_config
                
                return True
            
            # Status command
            if re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\bstatus\b', message):
                uptime_seconds = int(__import__('time').time() - bot.start_time)
                hours = uptime_seconds // 3600
                minutes = (uptime_seconds % 3600) // 60
                
                plugin_names = [p.name for p in bot.plugins if p.enabled]
                
                status_msg = (
                    f"🤖 Status: Online | "
                    f"⏱️ Uptime: {hours}h {minutes}m | "
                    f"🔌 Plugins: {len(plugin_names)} loaded | "
                    f"📡 Channels: {len(bot.channels)}"
                )
                
                await bot.privmsg(channel, status_msg)
                return True
            
            # Help command for admins
            if re.search(rf'(?i)\b{re.escape(bot_name)}\b.*\badmin\s+help\b', message):
                if not is_admin:
                    await bot.privmsg(channel, f"{nick}: You're not an admin!")
                    return True
                
                help_text = (
                    "Admin commands: "
                    "reload (reload config & plugins), "
                    "status (show bot status)"
                )
                await bot.privmsg(channel, help_text)
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
