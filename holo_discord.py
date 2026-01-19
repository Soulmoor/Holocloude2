#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO DISCORD INTEGRATION v1.0 - Discord Bot für Holo                        ║
║                                                                              ║
║  Features:                                                                   ║
║  • Discord Bot mit DM-Unterstützung                                          ║
║  • Proaktive Nachrichten per Discord DM                                      ║
║  • Vollständige Integration mit HoloBrain                                    ║
║  • Typing-Indikator für natürliches Gefühl                                   ║
║  • Server-Channel und DM Unterstützung                                       ║
║                                                                              ║
║  Verwendung:                                                                 ║
║    from holo_discord import HoloDiscordBot                                   ║
║    bot = HoloDiscordBot(holo_brain)                                          ║
║    bot.run("BOT_TOKEN")                                                      ║
║                                                                              ║
║  Author: Kira & Claude                                                       ║
║  Version: 1.0                                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import logging
import time
import random
from datetime import datetime
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("HoloDiscord")

# =============================================================================
# DISCORD IMPORT (Optional - graceful degradation)
# =============================================================================

try:
    import discord
    from discord.ext import commands, tasks
    DISCORD_AVAILABLE = True
    logger.info("✅ Discord.py verfügbar")
except ImportError:
    DISCORD_AVAILABLE = False
    logger.warning("⚠️ Discord.py nicht installiert - pip install discord.py")
    # Dummy-Klassen für Import-Kompatibilität
    class discord:
        class Client: pass
        class Intents:
            @classmethod
            def default(cls): return cls()
            message_content = True
            dm_messages = True
            guilds = True
    class commands:
        class Bot: pass


# =============================================================================
# KONFIGURATION
# =============================================================================

@dataclass
class DiscordConfig:
    """Discord Bot Konfiguration"""
    # Bot Token (aus config.json oder Environment)
    token: str = ""

    # Erlaubte User-IDs für DMs (Sicherheit)
    allowed_user_ids: List[int] = field(default_factory=list)

    # Erlaubte Channel-IDs für Server-Nutzung
    allowed_channel_ids: List[int] = field(default_factory=list)

    # Command Prefix
    command_prefix: str = "!"

    # Proaktive Nachrichten Settings
    proactive_enabled: bool = True
    proactive_dm_user_id: int = 0  # Primärer User für proaktive DMs
    proactive_check_interval: int = 60  # Sekunden

    # Typing Simulation
    typing_enabled: bool = True
    typing_delay_per_char: float = 0.03  # Sekunden pro Zeichen
    typing_max_delay: float = 5.0  # Max Typing-Zeit

    # Rate Limiting
    min_response_interval: float = 1.0  # Min Sekunden zwischen Antworten

    # Status
    status_message: str = "Holo ist da! 💕"

    @classmethod
    def from_dict(cls, data: Dict) -> 'DiscordConfig':
        """Erstelle Config aus Dictionary"""
        return cls(
            token=data.get('token', ''),
            allowed_user_ids=data.get('allowed_user_ids', []),
            allowed_channel_ids=data.get('allowed_channel_ids', []),
            command_prefix=data.get('command_prefix', '!'),
            proactive_enabled=data.get('proactive_enabled', True),
            proactive_dm_user_id=data.get('proactive_dm_user_id', 0),
            proactive_check_interval=data.get('proactive_check_interval', 60),
            typing_enabled=data.get('typing_enabled', True),
            typing_delay_per_char=data.get('typing_delay_per_char', 0.03),
            typing_max_delay=data.get('typing_max_delay', 5.0),
            min_response_interval=data.get('min_response_interval', 1.0),
            status_message=data.get('status_message', 'Holo ist da! 💕'),
        )


# =============================================================================
# MESSAGE TYPES
# =============================================================================

class DiscordMessageType(Enum):
    """Typen von Discord-Nachrichten"""
    USER_DM = "user_dm"
    USER_CHANNEL = "user_channel"
    USER_MENTION = "user_mention"
    PROACTIVE_DM = "proactive_dm"
    PROACTIVE_CHANNEL = "proactive_channel"


@dataclass
class DiscordMessage:
    """Eine Discord-Nachricht für Holo"""
    content: str
    author_id: int
    author_name: str
    channel_id: int
    guild_id: Optional[int] = None
    is_dm: bool = False
    message_type: DiscordMessageType = DiscordMessageType.USER_DM
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "channel_id": self.channel_id,
            "guild_id": self.guild_id,
            "is_dm": self.is_dm,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp,
        }


# =============================================================================
# HOLO DISCORD BOT
# =============================================================================

class HoloDiscordBot:
    """
    Discord Bot Integration für Holo.

    Ermöglicht:
    - Chat über Discord DMs
    - Chat in erlaubten Server-Channels
    - Proaktive Nachrichten per DM
    - Typing-Indikator für natürliches Gefühl
    """

    def __init__(self, holo_brain=None, config: DiscordConfig = None):
        """
        Args:
            holo_brain: HoloPersona Instanz
            config: Discord-Konfiguration
        """
        self.brain = holo_brain
        self.config = config or DiscordConfig()

        # Bot Instanz
        self.bot: Optional[commands.Bot] = None
        self._is_ready = False

        # State
        self._last_response_time: Dict[int, float] = {}  # user_id -> timestamp
        self._proactive_task = None
        self._proactive_running = False

        # Callbacks für externe Integration
        self._on_message_callbacks: List[Callable] = []
        self._on_response_callbacks: List[Callable] = []

        # Statistiken
        self.stats = {
            "messages_received": 0,
            "messages_sent": 0,
            "proactive_sent": 0,
            "errors": 0,
            "start_time": time.time(),
        }

        if DISCORD_AVAILABLE:
            self._setup_bot()
        else:
            logger.error("❌ Discord.py nicht verfügbar - Bot kann nicht erstellt werden")

    def _setup_bot(self):
        """Initialisiere den Discord Bot"""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.dm_messages = True
        intents.guilds = True

        self.bot = commands.Bot(
            command_prefix=self.config.command_prefix,
            intents=intents,
            help_command=None  # Custom help
        )

        # Event Handlers registrieren
        self.bot.event(self.on_ready)
        self.bot.event(self.on_message)

        # Commands registrieren
        self._register_commands()

        logger.info("🤖 Discord Bot initialisiert")

    def _register_commands(self):
        """Registriere Bot-Commands"""

        @self.bot.command(name="status")
        async def status_command(ctx):
            """Zeigt Holos Status"""
            if not self._is_authorized(ctx.author.id, ctx.channel.id):
                return

            status = self._get_holo_status()
            await ctx.send(status)

        @self.bot.command(name="energie")
        async def energie_command(ctx):
            """Zeigt Holos Energie-Level"""
            if not self._is_authorized(ctx.author.id, ctx.channel.id):
                return

            if self.brain and hasattr(self.brain, 'get_energy_level'):
                energy = self.brain.get_energy_level()
                energy_bar = "█" * int(energy * 10) + "░" * (10 - int(energy * 10))
                await ctx.send(f"⚡ Energie: [{energy_bar}] {energy*100:.0f}%")
            else:
                await ctx.send("⚡ Energie-System nicht verfügbar")

        @self.bot.command(name="stimmung")
        async def stimmung_command(ctx):
            """Zeigt Holos Stimmung"""
            if not self._is_authorized(ctx.author.id, ctx.channel.id):
                return

            if self.brain and hasattr(self.brain, 'get_current_mood'):
                mood = self.brain.get_current_mood()
                await ctx.send(f"😊 Stimmung: {mood}")
            else:
                await ctx.send("😊 Stimmungs-System nicht verfügbar")

        @self.bot.command(name="hilfe")
        async def hilfe_command(ctx):
            """Zeigt verfügbare Commands"""
            if not self._is_authorized(ctx.author.id, ctx.channel.id):
                return

            help_text = """
**🌸 Holo Discord Bot - Befehle**

`!status` - Zeigt Holos aktuellen Status
`!energie` - Zeigt Energie-Level
`!stimmung` - Zeigt aktuelle Stimmung
`!hilfe` - Diese Hilfe

**💬 Chat**
Schreib mir einfach eine DM oder erwähne mich!
            """
            await ctx.send(help_text)

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    async def on_ready(self):
        """Bot ist bereit"""
        self._is_ready = True
        logger.info(f"✅ Discord Bot eingeloggt als {self.bot.user}")

        # Status setzen
        await self.bot.change_presence(
            activity=discord.Game(name=self.config.status_message)
        )

        # Proaktive Nachrichten starten
        if self.config.proactive_enabled:
            self._start_proactive_loop()

        logger.info("🤖 Holo Discord Bot ist bereit!")

    async def on_message(self, message):
        """Verarbeite eingehende Nachrichten"""
        # Eigene Nachrichten ignorieren
        if message.author == self.bot.user:
            return

        # Autorisierung prüfen
        if not self._is_authorized(message.author.id, message.channel.id):
            logger.debug(f"Nicht autorisiert: User {message.author.id}, Channel {message.channel.id}")
            return

        # Commands verarbeiten
        await self.bot.process_commands(message)

        # Wenn es ein Command war, nicht als Chat verarbeiten
        if message.content.startswith(self.config.command_prefix):
            return

        # DM oder Mention?
        is_dm = isinstance(message.channel, discord.DMChannel)
        is_mention = self.bot.user.mentioned_in(message) if not is_dm else False

        # Nur auf DMs oder Mentions reagieren
        if not is_dm and not is_mention:
            return

        # Nachricht verarbeiten
        await self._handle_user_message(message, is_dm)

    async def _handle_user_message(self, message, is_dm: bool):
        """Verarbeite User-Nachricht und generiere Antwort"""
        user_text = message.content

        # Mention entfernen wenn vorhanden
        if self.bot.user.mentioned_in(message):
            user_text = user_text.replace(f'<@{self.bot.user.id}>', '').strip()
            user_text = user_text.replace(f'<@!{self.bot.user.id}>', '').strip()

        if not user_text:
            return

        # Rate Limiting
        user_id = message.author.id
        now = time.time()
        last_time = self._last_response_time.get(user_id, 0)
        if now - last_time < self.config.min_response_interval:
            await asyncio.sleep(self.config.min_response_interval - (now - last_time))

        self._last_response_time[user_id] = time.time()
        self.stats["messages_received"] += 1

        # Discord Message Objekt erstellen
        discord_msg = DiscordMessage(
            content=user_text,
            author_id=message.author.id,
            author_name=str(message.author),
            channel_id=message.channel.id,
            guild_id=message.guild.id if message.guild else None,
            is_dm=is_dm,
            message_type=DiscordMessageType.USER_DM if is_dm else DiscordMessageType.USER_MENTION,
        )

        # Callbacks aufrufen
        for callback in self._on_message_callbacks:
            try:
                callback(discord_msg)
            except Exception as e:
                logger.error(f"Message callback error: {e}")

        # Antwort von Holo holen
        try:
            response = await self._get_holo_response(user_text, discord_msg)

            if response:
                await self._send_response(message.channel, response)

                # Response callbacks
                for callback in self._on_response_callbacks:
                    try:
                        callback(discord_msg, response)
                    except Exception as e:
                        logger.error(f"Response callback error: {e}")

        except Exception as e:
            logger.error(f"Fehler bei Antwort-Generierung: {e}")
            self.stats["errors"] += 1
            await message.channel.send("*seufzt* Da ist etwas schiefgelaufen... 😅")

    async def _get_holo_response(self, user_text: str, msg: DiscordMessage) -> Optional[str]:
        """Hole Antwort von HoloBrain"""
        if not self.brain:
            logger.warning("Kein HoloBrain verbunden")
            return "Ich bin gerade nicht ganz da... *gähnt*"

        try:
            # Context für Discord
            context = {
                "source": "discord",
                "is_dm": msg.is_dm,
                "user_id": msg.author_id,
                "user_name": msg.author_name,
                "channel_id": msg.channel_id,
            }

            # HoloBrain aufrufen
            if hasattr(self.brain, 'chat'):
                response = self.brain.chat(user_text, context=context)
            elif hasattr(self.brain, 'process_message'):
                response = self.brain.process_message(user_text, context=context)
            elif hasattr(self.brain, 'generate_response'):
                response = self.brain.generate_response(user_text)
            else:
                response = "Ich höre dich, aber mein Gehirn ist gerade offline... 🧠💤"

            return response

        except Exception as e:
            logger.error(f"HoloBrain Fehler: {e}")
            return None

    async def _send_response(self, channel, response: str):
        """Sende Antwort mit Typing-Indikator"""
        if self.config.typing_enabled:
            # Typing simulieren
            typing_time = min(
                len(response) * self.config.typing_delay_per_char,
                self.config.typing_max_delay
            )
            async with channel.typing():
                await asyncio.sleep(typing_time)

        # Nachricht senden (ggf. aufteilen wenn zu lang)
        if len(response) > 2000:
            # Discord Limit: 2000 Zeichen
            chunks = [response[i:i+1990] for i in range(0, len(response), 1990)]
            for chunk in chunks:
                await channel.send(chunk)
                await asyncio.sleep(0.5)
        else:
            await channel.send(response)

        self.stats["messages_sent"] += 1

    # =========================================================================
    # PROAKTIVE NACHRICHTEN
    # =========================================================================

    def _start_proactive_loop(self):
        """Starte den proaktiven Nachrichten-Loop"""
        if self._proactive_running:
            return

        self._proactive_running = True
        self._proactive_task = asyncio.create_task(self._proactive_loop())
        logger.info("💬 Proaktiver Nachrichten-Loop gestartet")

    def _stop_proactive_loop(self):
        """Stoppe den proaktiven Nachrichten-Loop"""
        self._proactive_running = False
        if self._proactive_task:
            self._proactive_task.cancel()
        logger.info("💬 Proaktiver Nachrichten-Loop gestoppt")

    async def _proactive_loop(self):
        """Loop für proaktive Nachrichten"""
        while self._proactive_running:
            try:
                await asyncio.sleep(self.config.proactive_check_interval)

                if not self._is_ready:
                    continue

                # Prüfe ob HoloBrain proaktive Nachricht hat
                message = await self._get_proactive_message()

                if message:
                    await self._send_proactive_dm(message)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Proactive loop error: {e}")
                await asyncio.sleep(10)

    async def _get_proactive_message(self) -> Optional[str]:
        """Hole proaktive Nachricht von HoloBrain"""
        if not self.brain:
            return None

        try:
            # Verschiedene Methoden für proaktive Nachrichten prüfen
            if hasattr(self.brain, 'get_proactive_message'):
                msg = self.brain.get_proactive_message(source="discord")
                if msg:
                    return msg

            if hasattr(self.brain, 'autonomous_life') and self.brain.autonomous_life:
                if hasattr(self.brain.autonomous_life, 'get_pending_message'):
                    msg = self.brain.autonomous_life.get_pending_message()
                    if msg:
                        return msg

            if hasattr(self.brain, 'inner_life') and self.brain.inner_life:
                if hasattr(self.brain.inner_life, 'get_queued_message'):
                    msg = self.brain.inner_life.get_queued_message()
                    if msg:
                        return msg.get('content') if isinstance(msg, dict) else str(msg)

            return None

        except Exception as e:
            logger.debug(f"Proactive message check error: {e}")
            return None

    async def _send_proactive_dm(self, message: str):
        """Sende proaktive Nachricht per DM"""
        if not self.config.proactive_dm_user_id:
            logger.warning("Keine proactive_dm_user_id konfiguriert")
            return

        try:
            user = await self.bot.fetch_user(self.config.proactive_dm_user_id)
            if user:
                dm_channel = await user.create_dm()
                await self._send_response(dm_channel, message)
                self.stats["proactive_sent"] += 1
                logger.info(f"💬 Proaktive DM gesendet: {message[:50]}...")
        except Exception as e:
            logger.error(f"Proaktive DM Fehler: {e}")

    async def send_proactive_message(self, message: str, user_id: int = None):
        """
        Sende eine proaktive Nachricht (extern aufrufbar).

        Args:
            message: Die Nachricht
            user_id: Optional spezifische User-ID, sonst Default
        """
        target_id = user_id or self.config.proactive_dm_user_id
        if not target_id:
            logger.warning("Keine User-ID für proaktive Nachricht")
            return False

        try:
            user = await self.bot.fetch_user(target_id)
            if user:
                dm_channel = await user.create_dm()
                await self._send_response(dm_channel, message)
                self.stats["proactive_sent"] += 1
                return True
        except Exception as e:
            logger.error(f"Proaktive Nachricht Fehler: {e}")

        return False

    # =========================================================================
    # HILFSMETHODEN
    # =========================================================================

    def _is_authorized(self, user_id: int, channel_id: int) -> bool:
        """Prüfe ob User/Channel autorisiert ist"""
        # Wenn keine Beschränkungen, erlaube alles
        if not self.config.allowed_user_ids and not self.config.allowed_channel_ids:
            return True

        # User-basierte Autorisierung
        if self.config.allowed_user_ids:
            if user_id in self.config.allowed_user_ids:
                return True

        # Channel-basierte Autorisierung
        if self.config.allowed_channel_ids:
            if channel_id in self.config.allowed_channel_ids:
                return True

        return False

    def _get_holo_status(self) -> str:
        """Hole Holos Status als formatierten String"""
        status_parts = ["**🌸 Holo Status**\n"]

        if self.brain:
            # Energie
            if hasattr(self.brain, 'get_energy_level'):
                energy = self.brain.get_energy_level()
                energy_bar = "█" * int(energy * 10) + "░" * (10 - int(energy * 10))
                status_parts.append(f"⚡ Energie: [{energy_bar}] {energy*100:.0f}%")

            # Stimmung
            if hasattr(self.brain, 'get_current_mood'):
                mood = self.brain.get_current_mood()
                status_parts.append(f"😊 Stimmung: {mood}")

            # Aktivität
            if hasattr(self.brain, 'get_current_activity'):
                activity = self.brain.get_current_activity()
                if activity:
                    status_parts.append(f"🎯 Aktivität: {activity}")

        # Bot Stats
        uptime = time.time() - self.stats["start_time"]
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        status_parts.append(f"\n📊 **Bot Stats**")
        status_parts.append(f"⏱️ Online seit: {hours}h {minutes}m")
        status_parts.append(f"📨 Nachrichten: {self.stats['messages_received']} rein / {self.stats['messages_sent']} raus")
        status_parts.append(f"💬 Proaktiv: {self.stats['proactive_sent']}")

        return "\n".join(status_parts)

    # =========================================================================
    # CALLBACKS
    # =========================================================================

    def on_message_received(self, callback: Callable):
        """Registriere Callback für eingehende Nachrichten"""
        self._on_message_callbacks.append(callback)

    def on_response_sent(self, callback: Callable):
        """Registriere Callback für gesendete Antworten"""
        self._on_response_callbacks.append(callback)

    # =========================================================================
    # HAUPTMETHODEN
    # =========================================================================

    def run(self, token: str = None):
        """
        Starte den Discord Bot (blocking).

        Args:
            token: Bot Token (optional wenn in Config)
        """
        if not DISCORD_AVAILABLE:
            logger.error("❌ Discord.py nicht verfügbar")
            return

        bot_token = token or self.config.token
        if not bot_token:
            logger.error("❌ Kein Discord Bot Token konfiguriert")
            return

        logger.info("🚀 Starte Discord Bot...")
        self.bot.run(bot_token)

    async def start(self, token: str = None):
        """
        Starte den Discord Bot (async).

        Args:
            token: Bot Token (optional wenn in Config)
        """
        if not DISCORD_AVAILABLE:
            logger.error("❌ Discord.py nicht verfügbar")
            return

        bot_token = token or self.config.token
        if not bot_token:
            logger.error("❌ Kein Discord Bot Token konfiguriert")
            return

        logger.info("🚀 Starte Discord Bot (async)...")
        await self.bot.start(bot_token)

    async def close(self):
        """Beende den Discord Bot"""
        self._stop_proactive_loop()
        if self.bot:
            await self.bot.close()
        logger.info("👋 Discord Bot beendet")

    def set_brain(self, holo_brain):
        """Setze HoloBrain Referenz"""
        self.brain = holo_brain
        logger.info("🧠 HoloBrain verbunden")

    @property
    def is_ready(self) -> bool:
        """Ist der Bot bereit?"""
        return self._is_ready

    @property
    def is_connected(self) -> bool:
        """Ist der Bot verbunden?"""
        return self.bot is not None and self.bot.is_ready()


# =============================================================================
# DISCORD BRIDGE - Integration mit anderen Holo-Systemen
# =============================================================================

class HoloDiscordBridge:
    """
    Brücke zwischen Discord Bot und anderen Holo-Systemen.

    Ermöglicht:
    - Proaktive Nachrichten von verschiedenen Quellen
    - Event-basierte Kommunikation
    - Integration mit WebSocket, MQTT, etc.
    """

    def __init__(self, discord_bot: HoloDiscordBot = None):
        self.discord_bot = discord_bot
        self._message_queue: List[Dict] = []
        self._event_handlers: Dict[str, List[Callable]] = {}

    def set_bot(self, bot: HoloDiscordBot):
        """Setze Discord Bot Referenz"""
        self.discord_bot = bot

    async def send_message(self, message: str, user_id: int = None,
                          priority: str = "normal") -> bool:
        """
        Sende Nachricht über Discord.

        Args:
            message: Die Nachricht
            user_id: Ziel User-ID
            priority: "low", "normal", "high"
        """
        if not self.discord_bot or not self.discord_bot.is_ready:
            # Queue für später
            self._message_queue.append({
                "message": message,
                "user_id": user_id,
                "priority": priority,
                "timestamp": time.time(),
            })
            return False

        return await self.discord_bot.send_proactive_message(message, user_id)

    def queue_message(self, message: str, user_id: int = None,
                     priority: str = "normal"):
        """Queue eine Nachricht für späteren Versand"""
        self._message_queue.append({
            "message": message,
            "user_id": user_id,
            "priority": priority,
            "timestamp": time.time(),
        })

    async def process_queue(self):
        """Verarbeite Message Queue"""
        if not self.discord_bot or not self.discord_bot.is_ready:
            return

        # Nach Priorität sortieren
        self._message_queue.sort(
            key=lambda x: {"high": 0, "normal": 1, "low": 2}.get(x["priority"], 1)
        )

        sent = []
        for msg in self._message_queue:
            success = await self.discord_bot.send_proactive_message(
                msg["message"], msg.get("user_id")
            )
            if success:
                sent.append(msg)

        # Gesendete entfernen
        for msg in sent:
            self._message_queue.remove(msg)

    def on_event(self, event_type: str, handler: Callable):
        """Registriere Event Handler"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    async def emit_event(self, event_type: str, data: Any = None):
        """Emittiere Event an alle Handler"""
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Event handler error: {e}")


# =============================================================================
# FACTORY FUNKTIONEN
# =============================================================================

def create_discord_bot(holo_brain=None, config_dict: Dict = None) -> Optional[HoloDiscordBot]:
    """
    Factory-Funktion zum Erstellen eines Discord Bots.

    Args:
        holo_brain: HoloPersona Instanz
        config_dict: Konfiguration als Dictionary

    Returns:
        HoloDiscordBot Instanz oder None
    """
    if not DISCORD_AVAILABLE:
        logger.error("Discord.py nicht installiert - pip install discord.py")
        return None

    config = DiscordConfig.from_dict(config_dict) if config_dict else DiscordConfig()
    return HoloDiscordBot(holo_brain=holo_brain, config=config)


def load_discord_config() -> Optional[Dict]:
    """
    Lade Discord-Konfiguration aus config.json.

    Returns:
        Discord Config Dictionary oder None
    """
    try:
        from holo_config import get_config
        discord_config = get_config("discord", {})
        if discord_config:
            return discord_config
    except ImportError:
        pass

    # Fallback: Direkt aus config.json
    try:
        import json
        from pathlib import Path
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                return config.get("discord", {})
    except Exception as e:
        logger.warning(f"Config laden fehlgeschlagen: {e}")

    return None


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("🤖 HOLO DISCORD BOT TEST")
    print("=" * 60)

    if not DISCORD_AVAILABLE:
        print("❌ Discord.py nicht installiert!")
        print("   Installiere mit: pip install discord.py")
        sys.exit(1)

    # Config laden
    config = load_discord_config()
    if not config or not config.get("token"):
        print("⚠️ Keine Discord-Konfiguration gefunden!")
        print("   Füge 'discord' Sektion zu config.json hinzu:")
        print("""
    "discord": {
        "token": "DEIN_BOT_TOKEN",
        "allowed_user_ids": [123456789],
        "proactive_dm_user_id": 123456789,
        "proactive_enabled": true
    }
        """)
        sys.exit(1)

    # Bot erstellen (ohne HoloBrain für Test)
    bot = create_discord_bot(config_dict=config)

    if bot:
        print("✅ Discord Bot erstellt")
        print("🚀 Starte Bot...")
        bot.run()
    else:
        print("❌ Bot konnte nicht erstellt werden")
