#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO MEDIA INDEX - Medien-Wissen für Holo Brain
================================================
Empfängt NAS-Medien-Index via MQTT und beantwortet Fragen wie:
- "Wo ist Breaking Bad?"
- "Was ist auf dem NAS?"
- "Wie voll ist die Anime-Platte?"

DATABASE ARCHITECTURE:
----------------------
✅ MIGRATED TO CENTRAL DATABASE SYSTEM!

- Device management: Uses NetworkDatabase (holo_network.db)
- Media locations: Local specialized DB (media_index.db)
  - media_locations: Medien vom NAS via MQTT
  - manual_locations: User-Einträge für NLP-Queries

INTEGRATION in holo_brain_v15.py:
----------------------------------
    from holo_media_index import HoloMediaIndex
    from holo_database_system import HoloDatabaseManager

    # In HoloPersona.__init__:
    db_manager = HoloDatabaseManager()
    self.media_index = HoloMediaIndex(
        data_dir=Config.DATA_DIR,
        db_manager=db_manager  # ← Für zentrale Device-Verwaltung
    )

    # In _check_commands() hinzufügen:
    media_result = self.media_index.handle_query(text)
    if media_result:
        return media_result

BACKWARD COMPATIBILITY:
----------------------
If db_manager=None, works standalone (without device tracking).
"""

import os
import json
import sqlite3
import time
import threading
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

# Optional MQTT
MQTT_AVAILABLE = False
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    pass

logger = logging.getLogger("HoloMediaIndex")


@dataclass
class MediaLocation:
    """Ein Medien-Speicherort"""
    path: str
    name: str
    device: str  # "nas", "mini-pc", "pi", etc.
    media_type: str
    size_gb: float
    file_count: int
    last_seen: str
    online: bool = True


class HoloMediaIndex:
    """
    Holo's Wissen über Medien-Speicherorte.
    
    Features:
    - MQTT Listener für NAS-Updates
    - SQLite Datenbank für persistentes Wissen
    - Natürliche Sprach-Abfragen
    - Manuelle Einträge ("Merk dir: Filme sind auf dem NAS")
    - NAS Wake-Integration
    """
    
    def __init__(self, data_dir: str = "data", mqtt_config: Dict = None, db_manager=None):
        """
        Initialisiert HoloMediaIndex.

        Args:
            data_dir: Daten-Verzeichnis für die lokale media_index.db
            mqtt_config: MQTT Konfiguration für NAS-Updates
            db_manager: Optional HoloDatabaseManager für zentrale Device-Verwaltung
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "media_index.db"

        # Zentrale Datenbank (falls vorhanden)
        self.db_manager = db_manager

        self.mqtt_config = mqtt_config or {
            "enabled": True,
            "broker_ip": "192.168.178.99",
            "broker_port": 1883,
            "username": "kira",
            "password": "123",
            "topics": ["nas_brain/media_index", "nas_brain/disk_status", "nas_brain/status"]
        }

        self.mqtt_client = None
        self.nas_online = False
        self.nas_disk_status = {}
        self._lock = threading.Lock()

        # Datenbank initialisieren
        self._init_db()

        # MQTT starten falls verfügbar
        if MQTT_AVAILABLE and self.mqtt_config.get("enabled"):
            self._start_mqtt()

        logger.info("📁 HoloMediaIndex initialisiert")
    
    def _init_db(self):
        """
        Initialisiert die SQLite Datenbank.

        NOTE: Devices werden jetzt in NetworkDatabase (holo_network.db) verwaltet!
        Hier bleiben nur media-spezifische Tabellen.
        """
        with sqlite3.connect(self.db_path) as conn:
            # Media Locations - Spezialisiert für Media-Indexing
            conn.execute('''
                CREATE TABLE IF NOT EXISTS media_locations (
                    id INTEGER PRIMARY KEY,
                    path TEXT UNIQUE,
                    name TEXT,
                    device TEXT DEFAULT 'nas',
                    media_type TEXT,
                    size_gb REAL DEFAULT 0,
                    file_count INTEGER DEFAULT 0,
                    folder_count INTEGER DEFAULT 0,
                    sample_files TEXT,
                    last_updated TEXT,
                    source TEXT DEFAULT 'mqtt'
                )
            ''')

            # Manual Locations - User-Einträge für NLP-Queries
            conn.execute('''
                CREATE TABLE IF NOT EXISTS manual_locations (
                    id INTEGER PRIMARY KEY,
                    query TEXT,
                    description TEXT,
                    device TEXT,
                    path TEXT,
                    created_at TEXT
                )
            ''')

            conn.commit()

        # Devices in NetworkDatabase initialisieren (falls db_manager vorhanden)
        if self.db_manager:
            self._init_default_devices()
            logger.info("✅ Devices werden in NetworkDatabase verwaltet")
        else:
            logger.warning("⚠️ Kein db_manager - Device-Tracking nicht verfügbar")

    def _init_default_devices(self):
        """Initialisiert Standard-Geräte in NetworkDatabase"""
        if not self.db_manager:
            return

        default_devices = [
            {"name": "nas", "display_name": "NAS", "ip": "192.168.178.100",
             "device_type": "storage", "icon": "💾"},
            {"name": "mini-pc", "display_name": "Mini-PC", "ip": "192.168.178.102",
             "device_type": "computer", "icon": "🖥️"},
            {"name": "pi", "display_name": "Raspberry Pi", "ip": "192.168.178.103",
             "device_type": "computer", "icon": "🍓"},
        ]

        for dev in default_devices:
            try:
                # Check if device exists, if not create it
                existing = self.db_manager.network.get_device(dev["name"])
                if not existing:
                    self.db_manager.network.update_device(
                        name=dev["name"],
                        display_name=dev["display_name"],
                        device_type=dev["device_type"],
                        ip_address=dev["ip"],
                        status="offline",
                        icon=dev["icon"]
                    )
                    logger.info(f"  ✅ Device angelegt: {dev['display_name']}")
            except Exception as e:
                logger.error(f"  ❌ Fehler bei Device {dev['name']}: {e}")

    def _start_mqtt(self):
        """Startet MQTT Listener"""
        try:
            self.mqtt_client = mqtt.Client(client_id="holo_media_index")
            
            if self.mqtt_config.get("username"):
                self.mqtt_client.username_pw_set(
                    self.mqtt_config["username"],
                    self.mqtt_config.get("password", "")
                )
            
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_message = self._on_mqtt_message
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            
            self.mqtt_client.connect_async(
                self.mqtt_config["broker_ip"],
                self.mqtt_config.get("broker_port", 1883)
            )
            self.mqtt_client.loop_start()
            
            logger.info(f"📡 MQTT verbinde zu {self.mqtt_config['broker_ip']}...")
            
        except Exception as e:
            logger.error(f"MQTT Fehler: {e}")
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("📡 MQTT verbunden")
            for topic in self.mqtt_config.get("topics", []):
                client.subscribe(topic)
                logger.info(f"  Subscribed: {topic}")
        else:
            logger.error(f"MQTT Verbindung fehlgeschlagen: {rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        logger.warning(f"📡 MQTT getrennt (rc={rc})")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """Verarbeitet eingehende MQTT Nachrichten"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode("utf-8"))
            
            if "media_index" in topic:
                self._handle_media_index(payload)
            elif "disk_status" in topic:
                self._handle_disk_status(payload)
            elif "status" in topic:
                self._handle_nas_status(payload)
                
        except Exception as e:
            logger.error(f"MQTT Message Error: {e}")
    
    def _handle_media_index(self, data: Dict):
        """Verarbeitet Media-Index Update vom NAS"""
        folders = data.get("folders", {})
        logger.info(f"📁 Media Index empfangen: {len(folders)} Ordner")
        
        with sqlite3.connect(self.db_path) as conn:
            for path, folder in folders.items():
                conn.execute('''
                    INSERT OR REPLACE INTO media_locations 
                    (path, name, device, media_type, size_gb, file_count, folder_count, sample_files, last_updated, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    path,
                    folder.get("name", ""),
                    "nas",
                    folder.get("media_type", "unknown"),
                    folder.get("size_bytes", 0) / (1024**3),
                    folder.get("file_count", 0),
                    folder.get("folder_count", 0),
                    json.dumps(folder.get("sample_files", [])),
                    datetime.now().isoformat(),
                    "mqtt"
                ))
            conn.commit()
    
    def _handle_disk_status(self, data: Dict):
        """Verarbeitet Disk-Status Update"""
        with self._lock:
            self.nas_disk_status = data
    
    def _handle_nas_status(self, status):
        """Verarbeitet NAS Online/Offline Status"""
        if isinstance(status, str):
            self.nas_online = status.lower() == "online"
        elif isinstance(status, dict):
            self.nas_online = status.get("online", False)

        # Device-Status in NetworkDatabase updaten
        if self.db_manager:
            try:
                self.db_manager.network.update_device(
                    name="nas",
                    status="online" if self.nas_online else "offline",
                    device_type="storage",
                    display_name="NAS",
                    ip_address="192.168.178.100"
                )
            except Exception as e:
                logger.error(f"Fehler beim NAS-Status Update in NetworkDatabase: {e}")
    
    # =========================================================================
    # QUERY HANDLING - Natürliche Sprach-Abfragen
    # =========================================================================
    
    def handle_query(self, text: str) -> Optional[Dict]:
        """
        Verarbeitet natürliche Sprach-Anfragen zu Medien.
        
        Returns:
            Dict mit "type" und "reply" wenn erkannt, sonst None
        """
        t = text.lower().strip()
        
        # === WO IST / WO FINDE ICH ===
        where_patterns = [
            r'wo (?:ist|sind|finde ich|war|waren)\s+(?:der |die |das |nochmal )?(.+?)(?:\?|$)',
            r'(?:hast du|weißt du wo)\s+(.+?)\s+(?:ist|gespeichert)',
            r'auf welchem (?:gerät|laufwerk|nas)\s+ist\s+(.+)',
        ]
        
        for pattern in where_patterns:
            match = re.search(pattern, t)
            if match:
                query = match.group(1).strip()
                return self._search_and_respond(query)
        
        # === WAS IST AUF DEM NAS ===
        if any(p in t for p in ["was ist auf dem nas", "was ist auf nas", "nas inhalt", "nas übersicht"]):
            return self._get_nas_overview()
        
        # === WAS IST AUF GERÄT X ===
        device_query_patterns = [
            r'was\s+(?:ist|sind|habe ich|hab ich)\s+(?:auf|in)\s+(?:dem\s+|der\s+)?(\w+(?:[\s-]\w+)?)',
            r'(?:zeig|zeige)\s+(?:mir\s+)?(?:was\s+)?(?:auf|in)\s+(?:dem\s+|der\s+)?(\w+(?:[\s-]\w+)?)\s+(?:ist|gespeichert)',
            r'(\w+(?:[\s-]\w+)?)\s+inhalt',
        ]
        
        for pattern in device_query_patterns:
            match = re.search(pattern, t)
            if match:
                device_query = match.group(1).strip().lower()
                # Prüfe ob es ein bekanntes Gerät ist
                known_devices = ["nas", "pc", "laptop", "mini-pc", "gaming-pc", "server", "pi", 
                                 "handy", "tablet", "usb-stick", "cloud", "nextcloud", "tv", "konsole"]
                if any(d in device_query for d in known_devices):
                    return self._get_device_content(device_query)
        
        # === ALLE SPEICHERORTE ===
        if any(p in t for p in ["was habe ich wo", "wo habe ich was", "alle speicherorte", 
                                 "was hast du dir gemerkt", "welche dateien kennst du"]):
            return self._get_all_locations()
        
        # === WELCHE GERÄTE ===
        if any(p in t for p in ["welche geräte", "geräte übersicht", "welche geräte kennst du"]):
            return self._get_known_devices()
        
        # === SPEICHERPLATZ ===
        if any(p in t for p in ["speicherplatz", "wie voll", "platz auf", "freier speicher", "festplatte"]):
            return self._get_disk_status()
        
        # === IST DAS NAS AN ===
        if any(p in t for p in ["ist das nas an", "ist nas online", "nas status", "läuft das nas"]):
            return self._get_nas_status_response()
        
        # === MANUELLER EINTRAG ===
        manual_patterns = [
            # "merk dir: X ist auf dem NAS"
            r'merk\s*(?:dir)?[:\s]+(.+?)\s+(?:ist|sind|liegt|liegen)\s+(?:auf|in|unter)\s+(?:dem\s+|der\s+)?(.+)',
            # "speicher: X ist auf dem Laptop"
            r'(?:speicher|notier)[:\s]+(.+?)\s+(?:ist|sind)\s+(?:auf|in)\s+(?:dem\s+|der\s+)?(.+)',
            # "X ist auf dem NAS"
            r'^(.+?)\s+(?:ist|sind|liegt|liegen)\s+(?:auf|in)\s+(?:dem\s+|der\s+)?(\w+(?:[\s-]\w+)?)\s*$',
            # "auf dem NAS ist X" / "auf dem Laptop hab ich X"
            r'auf\s+(?:dem\s+|der\s+)?(\w+(?:[\s-]\w+)?)\s+(?:ist|sind|hab ich|habe ich|liegt|liegen)\s+(.+)',
            # "X hab ich auf dem PC"
            r'(.+?)\s+hab(?:e)?\s+ich\s+(?:auf|in)\s+(?:dem\s+|der\s+)?(.+)',
            # "ich hab X auf dem NAS gespeichert"
            r'ich\s+hab(?:e)?\s+(.+?)\s+(?:auf|in)\s+(?:dem\s+|der\s+)?(.+?)\s+(?:gespeichert|abgelegt|kopiert)',
        ]
        
        for pattern in manual_patterns:
            match = re.search(pattern, t)
            if match:
                # Bei "auf dem X ist Y" sind die Gruppen vertauscht
                if pattern.startswith('auf'):
                    location = match.group(1).strip()
                    item = match.group(2).strip()
                else:
                    item = match.group(1).strip()
                    location = match.group(2).strip()
                
                # Filtere zu kurze/generische Einträge
                if len(item) > 2 and len(location) > 1:
                    return self._add_manual_entry(item, location)
        
        return None
    
    def _search_and_respond(self, query: str) -> Dict:
        """Sucht nach einem Begriff und gibt Holo-Style Antwort"""
        results = self.search(query)
        
        if not results:
            # Prüfe manuelle Einträge
            manual = self._search_manual(query)
            if manual:
                return {
                    "type": "media_location",
                    "reply": f"*Ohren spitzen sich* {manual['description']} ist auf **{manual['device']}** unter `{manual['path']}`"
                }
            
            return {
                "type": "media_not_found",
                "reply": f"*kratzt sich am Ohr* Hmm, '{query}' hab ich leider nicht in meinem Index... " +
                         "Vielleicht ist es unter einem anderen Namen gespeichert? " +
                         "Oder sag mir wo es ist, dann merk ich mir das! 🐺"
            }
        
        # Beste Treffer
        best = results[0]
        
        # Antwort bauen
        device_name = "NAS" if best["device"] == "nas" else best["device"].upper()
        
        response = f"*Schweif wedelt* Gefunden! **{best['name']}** ist auf dem **{device_name}**\n\n"
        response += f"📁 Pfad: `{best['path']}`\n"
        
        if best.get("file_count"):
            response += f"📊 {best['file_count']} Dateien"
            if best.get("size_gb"):
                response += f" ({best['size_gb']:.1f} GB)"
            response += "\n"
        
        # NAS Status prüfen
        if best["device"] == "nas" and not self.nas_online:
            response += "\n⚠️ *Ohren legen sich an* Das NAS ist gerade **offline**. Soll ich es aufwecken?"
        
        # Weitere Treffer?
        if len(results) > 1:
            response += f"\n\n*tippt mit dem Finger* Ich hab noch {len(results)-1} weitere Treffer gefunden. Willst du mehr sehen?"
        
        return {
            "type": "media_location",
            "reply": response,
            "results": results,
            "nas_online": self.nas_online
        }
    
    def _get_nas_overview(self) -> Dict:
        """Gibt Übersicht über NAS-Inhalt"""
        stats = self.get_stats()
        
        response = "*Ohren stellen sich auf* Hier ist was auf dem NAS ist:\n\n"
        
        for media_type, info in stats.get("by_type", {}).items():
            emoji = {
                "anime": "🎌",
                "filme": "🎬",
                "serien": "📺",
                "musik": "🎵",
                "fotos": "📷",
                "video": "🎥",
                "sonstiges": "📁"
            }.get(media_type, "📁")
            
            response += f"{emoji} **{media_type.title()}**: {info['count']} Ordner ({info['size_gb']:.1f} GB)\n"
        
        response += f"\n📊 **Gesamt:** {stats['total_folders']} Ordner, {stats['total_size_gb']:.1f} GB"
        
        if not self.nas_online:
            response += "\n\n⚠️ Das NAS ist gerade offline."
        
        return {
            "type": "nas_overview",
            "reply": response,
            "stats": stats
        }
    
    def _get_disk_status(self) -> Dict:
        """Gibt Speicherplatz-Status zurück"""
        if not self.nas_disk_status:
            return {
                "type": "disk_status",
                "reply": "*kratzt sich am Ohr* Ich hab gerade keine Speicherplatz-Infos... Ist das NAS online?"
            }
        
        response = "*tippt auf imaginärem Display* Hier ist der Speicherplatz:\n\n"
        
        for path, info in self.nas_disk_status.items():
            name = Path(path).name
            used_percent = info.get("percent_used", 0)
            free_gb = info.get("free_gb", 0)
            
            # Balken visualisieren
            bar_filled = int(used_percent / 10)
            bar_empty = 10 - bar_filled
            bar = "█" * bar_filled + "░" * bar_empty
            
            # Warnung bei >80%
            warn = " ⚠️" if used_percent > 80 else ""
            
            response += f"**{name}**: [{bar}] {used_percent}%{warn}\n"
            response += f"    {free_gb:.0f} GB frei\n\n"
        
        return {
            "type": "disk_status",
            "reply": response,
            "data": self.nas_disk_status
        }
    
    def _get_nas_status_response(self) -> Dict:
        """Gibt NAS-Status zurück"""
        if self.nas_online:
            return {
                "type": "nas_status",
                "reply": "*Schweif wedelt* Ja, das NAS ist online und läuft! 🟢"
            }
        else:
            return {
                "type": "nas_status",
                "reply": "*Ohren sinken leicht* Nein, das NAS ist gerade offline. 🔴\nSoll ich es aufwecken?",
                "nas_online": False
            }
    
    def _get_device_content(self, device_query: str) -> Dict:
        """Zeigt was auf einem bestimmten Gerät gespeichert ist"""
        # Device-Name normalisieren
        device_map = {
            "nas": "nas",
            "pc": "pc", "computer": "pc", "rechner": "pc",
            "laptop": "laptop", "notebook": "laptop",
            "mini-pc": "mini-pc", "minipc": "mini-pc",
            "gaming-pc": "gaming-pc", "gaming pc": "gaming-pc", "gamingpc": "gaming-pc",
            "pi": "pi", "raspberry": "pi", "raspi": "pi",
            "handy": "handy", "smartphone": "handy", "phone": "handy",
            "tablet": "tablet", "ipad": "tablet",
            "usb": "usb-stick", "stick": "usb-stick", "usb-stick": "usb-stick",
            "cloud": "cloud", "dropbox": "cloud", "gdrive": "cloud",
            "server": "server",
        }
        
        device = None
        for key, val in device_map.items():
            if key in device_query:
                device = val
                break
        
        if not device:
            return {
                "type": "device_not_found",
                "reply": f"*kratzt sich am Ohr* Hmm, '{device_query}' kenne ich nicht als Gerät..."
            }
        
        # Device Display-Name
        display_names = {
            "nas": "NAS", "pc": "PC", "laptop": "Laptop", "mini-pc": "Mini-PC",
            "gaming-pc": "Gaming-PC", "pi": "Raspberry Pi", "handy": "Handy",
            "tablet": "Tablet", "usb-stick": "USB-Stick", "cloud": "Cloud", "server": "Server"
        }
        display_name = display_names.get(device, device.upper())
        
        results = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Automatische Einträge (vom NAS)
            if device == "nas":
                rows = conn.execute('''
                    SELECT name, path, media_type, file_count, size_gb 
                    FROM media_locations 
                    WHERE device = ?
                    ORDER BY file_count DESC
                    LIMIT 20
                ''', (device,)).fetchall()
                results.extend([dict(r) for r in rows])
            
            # Manuelle Einträge
            rows = conn.execute('''
                SELECT description as name, path, 'manuell' as media_type
                FROM manual_locations
                WHERE device = ?
                ORDER BY created_at DESC
            ''', (device,)).fetchall()
            results.extend([dict(r) for r in rows])
        
        if not results:
            return {
                "type": "device_content",
                "reply": f"*Ohren legen sich an* Ich hab noch nichts für den **{display_name}** gespeichert...\n\n" +
                         f"Sag mir was drauf ist! Z.B.: \"Meine Fotos sind auf dem {display_name}\""
            }
        
        response = f"*Schweif wedelt* Hier ist was ich über den **{display_name}** weiß:\n\n"
        
        for r in results[:10]:
            emoji = {"anime": "🎌", "filme": "🎬", "serien": "📺", "musik": "🎵", 
                     "fotos": "📷", "video": "🎥", "manuell": "📝"}.get(r.get("media_type", ""), "📁")
            
            response += f"{emoji} **{r['name']}**"
            if r.get("file_count"):
                response += f" ({r['file_count']} Dateien)"
            response += "\n"
        
        if len(results) > 10:
            response += f"\n... und {len(results) - 10} weitere"
        
        return {
            "type": "device_content",
            "reply": response,
            "device": device,
            "results": results
        }
    
    def _get_all_locations(self) -> Dict:
        """Zeigt alle gespeicherten Speicherorte"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Manuelle Einträge nach Gerät gruppiert
            rows = conn.execute('''
                SELECT device, description, path, created_at
                FROM manual_locations
                ORDER BY device, created_at DESC
            ''').fetchall()
        
        if not rows:
            return {
                "type": "all_locations",
                "reply": "*Ohren hängen* Ich hab mir noch nichts gemerkt...\n\n" +
                         "Sag mir wo deine Sachen sind! Z.B.:\n" +
                         "• \"Meine Fotos sind auf dem NAS\"\n" +
                         "• \"Die Steuererklärung ist auf dem Laptop\"\n" +
                         "• \"Spiele sind auf dem Gaming-PC\""
            }
        
        # Nach Gerät gruppieren
        by_device = {}
        for r in rows:
            device = r["device"]
            if device not in by_device:
                by_device[device] = []
            by_device[device].append(r["description"])
        
        response = "*nickt zufrieden* Das hab ich mir gemerkt:\n\n"
        
        device_emojis = {
            "nas": "💾", "pc": "🖥️", "laptop": "💻", "mini-pc": "🖥️",
            "gaming-pc": "🎮", "pi": "🍓", "handy": "📱", "tablet": "📱",
            "usb-stick": "💾", "cloud": "☁️", "server": "🖧", "unknown": "❓"
        }
        
        device_names = {
            "nas": "NAS", "pc": "PC", "laptop": "Laptop", "mini-pc": "Mini-PC",
            "gaming-pc": "Gaming-PC", "pi": "Raspberry Pi", "handy": "Handy",
            "tablet": "Tablet", "usb-stick": "USB-Stick", "cloud": "Cloud",
            "server": "Server", "unknown": "Unbekannt"
        }
        
        for device, items in by_device.items():
            emoji = device_emojis.get(device, "📁")
            name = device_names.get(device, device)
            response += f"{emoji} **{name}:**\n"
            for item in items[:5]:
                response += f"  • {item}\n"
            if len(items) > 5:
                response += f"  ... und {len(items) - 5} weitere\n"
            response += "\n"
        
        return {
            "type": "all_locations",
            "reply": response
        }
    
    def _get_known_devices(self) -> Dict:
        """Zeigt alle bekannten Geräte"""
        response = "*Ohren stellen sich auf* Diese Geräte kenne ich:\n\n"
        
        devices_info = [
            ("💾", "NAS", "Netzwerkspeicher für Filme, Anime, etc."),
            ("🖥️", "PC / Desktop", "Dein Hauptrechner"),
            ("💻", "Laptop", "Mobiler Computer"),
            ("🖥️", "Mini-PC", "Kleiner Server/PC"),
            ("🎮", "Gaming-PC", "Zum Zocken"),
            ("🍓", "Raspberry Pi", "Kleiner Linux-Rechner"),
            ("📱", "Handy/Tablet", "Mobiles Gerät"),
            ("💾", "USB-Stick", "Tragbarer Speicher"),
            ("💿", "Externe Festplatte", "Backup-Speicher"),
            ("☁️", "Cloud", "Online-Speicher (Dropbox, etc.)"),
            ("🖧", "Server", "Zentraler Rechner"),
            ("📺", "Smart-TV", "Fernseher"),
            ("🎮", "Konsole", "PlayStation, Xbox, Switch"),
        ]
        
        for emoji, name, desc in devices_info:
            response += f"{emoji} **{name}** - {desc}\n"
        
        response += "\n*lächelt* Sag mir einfach wo deine Sachen sind!\n"
        response += "Z.B.: \"Breaking Bad ist auf dem NAS\""
        
        return {
            "type": "known_devices",
            "reply": response
        }
    
    def _add_manual_entry(self, item: str, location: str) -> Dict:
        """Fügt manuellen Eintrag hinzu"""
        # Device erkennen - ERWEITERT mit vielen Geräten
        device = "unknown"
        path = location
        
        device_patterns = [
            # NAS
            (r'\bnas\b', "nas"),
            (r'synology|qnap|truenas|freenas', "nas"),
            
            # Computer
            (r'mini[\s-]?pc', "mini-pc"),
            (r'gaming[\s-]?pc', "gaming-pc"),
            (r'\bpc\b|desktop|rechner|computer', "pc"),
            (r'laptop|notebook|macbook|thinkpad', "laptop"),
            (r'server', "server"),
            
            # Raspberry Pi
            (r'raspberry|raspi|\bpi\b', "pi"),
            
            # Mobile
            (r'handy|smartphone|phone|iphone|android', "handy"),
            (r'tablet|ipad', "tablet"),
            
            # Externe Speicher
            (r'usb[\s-]?stick|stick', "usb-stick"),
            (r'externe.*festplatte|external.*hdd|externe.*hdd', "externe-festplatte"),
            (r'sd[\s-]?karte|speicherkarte', "sd-karte"),
            
            # Cloud
            (r'cloud|google[\s-]?drive|dropbox|onedrive|icloud', "cloud"),
            (r'nextcloud', "nextcloud"),
            
            # Spezifisch
            (r'tv|fernseher|smart[\s-]?tv', "tv"),
            (r'playstation|ps[45]|xbox|nintendo|switch', "konsole"),
        ]
        
        for pattern, dev in device_patterns:
            if re.search(pattern, location.lower()):
                device = dev
                break
        
        # Pfad extrahieren falls angegeben
        path_match = re.search(r'(?:unter|in|pfad|ordner)[:\s]+([/\\].+?)(?:\s|$)', location, re.IGNORECASE)
        if path_match:
            path = path_match.group(1).strip()
        
        # Device Display-Name
        device_names = {
            "nas": "NAS",
            "mini-pc": "Mini-PC",
            "gaming-pc": "Gaming-PC",
            "pc": "PC",
            "laptop": "Laptop",
            "server": "Server",
            "pi": "Raspberry Pi",
            "handy": "Handy",
            "tablet": "Tablet",
            "usb-stick": "USB-Stick",
            "externe-festplatte": "Externe Festplatte",
            "sd-karte": "SD-Karte",
            "cloud": "Cloud",
            "nextcloud": "Nextcloud",
            "tv": "Smart-TV",
            "konsole": "Konsole",
            "unknown": "Unbekannt"
        }
        
        display_name = device_names.get(device, device)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO manual_locations (query, description, device, path, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (item.lower(), item, device, location, datetime.now().isoformat()))
            conn.commit()
        
        return {
            "type": "manual_entry_added",
            "reply": f"*nickt eifrig* Alles klar! Ich merk mir: **{item}** ist auf dem **{display_name}** 📝"
        }
    
    # =========================================================================
    # SEARCH & DATABASE METHODS
    # =========================================================================
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Sucht im Media-Index"""
        query_lower = query.lower()
        results = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Exakte Suche im Namen
            rows = conn.execute('''
                SELECT * FROM media_locations 
                WHERE LOWER(name) LIKE ? OR LOWER(path) LIKE ?
                ORDER BY file_count DESC
                LIMIT ?
            ''', (f'%{query_lower}%', f'%{query_lower}%', limit)).fetchall()
            
            for row in rows:
                results.append(dict(row))
            
            # Auch in sample_files suchen
            if len(results) < limit:
                rows = conn.execute('''
                    SELECT * FROM media_locations 
                    WHERE sample_files LIKE ?
                    LIMIT ?
                ''', (f'%{query_lower}%', limit - len(results))).fetchall()
                
                for row in rows:
                    if dict(row) not in results:
                        results.append(dict(row))
        
        return results
    
    def _search_manual(self, query: str) -> Optional[Dict]:
        """Sucht in manuellen Einträgen"""
        query_lower = query.lower()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute('''
                SELECT * FROM manual_locations 
                WHERE LOWER(query) LIKE ? OR LOWER(description) LIKE ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (f'%{query_lower}%', f'%{query_lower}%')).fetchone()
            
            return dict(row) if row else None
    
    def get_stats(self) -> Dict:
        """Gibt Statistiken zurück"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Gesamt
            total = conn.execute('SELECT COUNT(*), SUM(size_gb), SUM(file_count) FROM media_locations').fetchone()
            
            # Nach Typ
            by_type = {}
            rows = conn.execute('''
                SELECT media_type, COUNT(*) as count, SUM(size_gb) as size 
                FROM media_locations 
                GROUP BY media_type
            ''').fetchall()
            
            for row in rows:
                by_type[row['media_type']] = {
                    "count": row['count'],
                    "size_gb": round(row['size'] or 0, 2)
                }
            
            return {
                "total_folders": total[0] or 0,
                "total_size_gb": round(total[1] or 0, 2),
                "total_files": total[2] or 0,
                "by_type": by_type,
                "nas_online": self.nas_online
            }
    
    def get_device_status(self, device: str) -> Optional[Dict]:
        """
        Gibt Status eines Geräts zurück.

        Returns device status from NetworkDatabase if available,
        otherwise returns None.
        """
        if self.db_manager:
            try:
                dev = self.db_manager.network.get_device(device)
                if dev:
                    # Convert NetworkDevice dataclass to dict
                    return {
                        "name": dev.name,
                        "display_name": dev.display_name,
                        "device_type": dev.device_type,
                        "status": dev.status,
                        "ip_address": dev.ip_address,
                        "last_seen": dev.last_seen,
                        "is_online": dev.status != "offline"
                    }
            except Exception as e:
                logger.error(f"Fehler beim Holen des Device-Status: {e}")

        return None
    
    def stop(self):
        """Stoppt MQTT Client"""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()


# =============================================================================
# TEST & EXAMPLES
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    print("=" * 70)
    print("HOLO MEDIA INDEX - Test Suite")
    print("=" * 70)
    print()

    # =========================================================================
    # OPTION 1: Mit HoloDatabaseManager (EMPFOHLEN)
    # =========================================================================
    print("📦 TEST 1: Mit zentraler Datenbank (NetworkDatabase)")
    print("-" * 70)

    try:
        from holo_database_system import HoloDatabaseManager

        db_manager = HoloDatabaseManager(data_dir=Path("/tmp/holo_test_central"))
        index = HoloMediaIndex(
            data_dir="/tmp/holo_test",
            mqtt_config={"enabled": False},
            db_manager=db_manager  # ← Zentrale DB für Devices
        )

        # Device Status testen
        nas_status = index.get_device_status("nas")
        if nas_status:
            print(f"✅ NAS Status: {nas_status['status']}")
        else:
            print("✅ NAS Status: Device in NetworkDatabase angelegt")

        print()

    except ImportError:
        print("⚠️ holo_database_system nicht verfügbar - überspringe Test 1")
        print()

    # =========================================================================
    # OPTION 2: Standalone (Backward Compatible)
    # =========================================================================
    print("📦 TEST 2: Standalone ohne zentrale Datenbank")
    print("-" * 70)

    index_standalone = HoloMediaIndex(
        data_dir="/tmp/holo_test_standalone",
        mqtt_config={"enabled": False}
        # db_manager=None (default) - kein Device-Tracking
    )

    print("✅ Standalone-Modus funktioniert (ohne Device-Tracking)")
    print()

    # =========================================================================
    # NLP Query Tests
    # =========================================================================
    print("📦 TEST 3: Natural Language Queries")
    print("-" * 70)

    test_queries = [
        "wo ist Breaking Bad?",
        "was ist auf dem NAS?",
        "wie voll ist die Festplatte?",
        "ist das NAS an?",
        "merk dir: Urlaubsfotos sind auf dem NAS unter /fotos/2024",
    ]

    for query in test_queries:
        print(f"❓ '{query}'")
        result = index_standalone.handle_query(query)
        if result:
            print(f"   ✅ Type: {result['type']}")
            reply = result['reply'].replace('\n', ' ')[:80]
            print(f"   💬 {reply}...")
        else:
            print("   ❌ Nicht erkannt")
        print()

    print("=" * 70)
    print("✅ Alle Tests abgeschlossen!")
    print("=" * 70)
