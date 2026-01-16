#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO DEVICE RECEIVER v1.0
=========================
Standalone Empfänger für alle Holo Device Agents.
Sammelt System-Infos von allen Geräten im Netzwerk via MQTT.

Holo Brain nutzt nur dieses Modul um Geräte-Daten abzufragen.

INSTALLATION:
    pip install paho-mqtt

FEATURES:
    - Empfängt Daten von beliebig vielen Geräten
    - Speichert History in SQLite
    - Erkennt Online/Offline Status
    - Stellt einfache API für Holo bereit

MQTT TOPICS (empfängt):
    holo/devices/{device_name}/state   → Kompletter Status
    holo/devices/{device_name}/status  → online/busy/idle/offline
    holo/devices/{device_name}/metrics → CPU, RAM, etc.
"""

import os
import json
import sqlite3
import time
import threading
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Optional MQTT
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("⚠️ paho-mqtt nicht installiert! pip install paho-mqtt")

logger = logging.getLogger("HoloDeviceReceiver")


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class DeviceInfo:
    """Informationen über ein Gerät"""
    name: str
    display_name: str
    device_type: str
    icon: str
    status: str  # online, busy, idle, offline
    last_seen: datetime
    hostname: str = ""
    ip_address: str = ""
    
    # Metriken
    cpu_percent: float = 0.0
    cpu_temp: Optional[float] = None
    ram_percent: float = 0.0
    ram_used_gb: float = 0.0
    ram_total_gb: float = 0.0
    disk_percent: float = 0.0
    disk_free_gb: float = 0.0
    uptime_hours: float = 0.0
    
    # Ordner
    shared_folders: List[Dict] = None
    
    def __post_init__(self):
        if self.shared_folders is None:
            self.shared_folders = []
    
    def is_online(self) -> bool:
        """Prüft ob Gerät noch online ist (letzte 2 Minuten)"""
        if self.status == "offline":
            return False
        return datetime.now() - self.last_seen < timedelta(minutes=2)
    
    def get_status_emoji(self) -> str:
        """Status als Emoji"""
        if not self.is_online():
            return "🔴"
        return {"online": "🟢", "busy": "🟠", "idle": "🟡"}.get(self.status, "⚪")


# =============================================================================
# DEVICE RECEIVER
# =============================================================================

class HoloDeviceReceiver:
    """
    Empfängt und verwaltet Daten von allen Holo Device Agents.
    
    Usage:
        receiver = HoloDeviceReceiver()
        receiver.start()
        
        # Daten abrufen
        devices = receiver.get_all_devices()
        pc_status = receiver.get_device("mein-pc")
        online = receiver.get_online_devices()
    """
    
    def __init__(self, data_dir: str = "data", mqtt_config: Dict = None):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "device_registry.db"
        
        # MQTT-Konfiguration aus Umgebungsvariablen oder Parameter
        self.mqtt_config = mqtt_config or {
            "enabled": True,
            "broker_ip": os.getenv("HOLO_MQTT_BROKER", "localhost"),
            "broker_port": int(os.getenv("HOLO_MQTT_PORT", "1883")),
            "username": os.getenv("HOLO_MQTT_USER", "mqtt"),
            "password": os.getenv("HOLO_MQTT_PASSWORD", ""),  # Aus Umgebungsvariable!
            "topic_prefix": "holo/devices/#",
        }
        
        self.mqtt_client = None
        self._devices: Dict[str, DeviceInfo] = {}
        self._lock = threading.RLock()
        self._running = False
        
        # Datenbank initialisieren
        self._init_db()
        
        # Bekannte Geräte aus DB laden
        self._load_devices_from_db()
        
        logger.info("📡 HoloDeviceReceiver initialisiert")
    
    def _init_db(self):
        """Initialisiert SQLite Datenbank"""
        with sqlite3.connect(self.db_path) as conn:
            # Geräte-Registry
            conn.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    name TEXT PRIMARY KEY,
                    display_name TEXT,
                    device_type TEXT,
                    icon TEXT,
                    hostname TEXT,
                    ip_address TEXT,
                    first_seen TEXT,
                    last_seen TEXT,
                    last_status TEXT DEFAULT 'offline'
                )
            ''')
            
            # Metriken-History (für Trends)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS metrics_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_name TEXT,
                    timestamp TEXT,
                    cpu_percent REAL,
                    cpu_temp REAL,
                    ram_percent REAL,
                    disk_percent REAL,
                    status TEXT,
                    FOREIGN KEY (device_name) REFERENCES devices(name)
                )
            ''')
            
            # Shared Folders
            conn.execute('''
                CREATE TABLE IF NOT EXISTS shared_folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_name TEXT,
                    path TEXT,
                    name TEXT,
                    folder_type TEXT,
                    size_gb REAL,
                    file_count INTEGER,
                    subfolders TEXT,
                    last_updated TEXT,
                    FOREIGN KEY (device_name) REFERENCES devices(name)
                )
            ''')
            
            # Index für schnelle Abfragen
            conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_device ON metrics_history(device_name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_time ON metrics_history(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_folders_device ON shared_folders(device_name)')
            
            conn.commit()
    
    def _load_devices_from_db(self):
        """Lädt bekannte Geräte aus der Datenbank"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute('SELECT * FROM devices').fetchall()
            
            for row in rows:
                device = DeviceInfo(
                    name=row['name'],
                    display_name=row['display_name'],
                    device_type=row['device_type'],
                    icon=row['icon'] or "🖥️",
                    status="offline",  # Bis wir ein Update bekommen
                    last_seen=datetime.fromisoformat(row['last_seen']) if row['last_seen'] else datetime.min,
                    hostname=row['hostname'] or "",
                    ip_address=row['ip_address'] or ""
                )
                self._devices[row['name']] = device
        
        logger.info(f"📂 {len(self._devices)} Geräte aus DB geladen")
    
    # =========================================================================
    # MQTT
    # =========================================================================
    
    def start(self):
        """Startet MQTT Listener"""
        if not MQTT_AVAILABLE:
            logger.error("MQTT nicht verfügbar!")
            return False
        
        if not self.mqtt_config.get("enabled", True):
            logger.info("MQTT deaktiviert")
            return False
        
        try:
            self.mqtt_client = mqtt.Client(client_id="holo_device_receiver")
            
            if self.mqtt_config.get("username"):
                self.mqtt_client.username_pw_set(
                    self.mqtt_config["username"],
                    self.mqtt_config.get("password", "")
                )
            
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_disconnect = self._on_disconnect
            self.mqtt_client.on_message = self._on_message
            
            self.mqtt_client.connect_async(
                self.mqtt_config["broker_ip"],
                self.mqtt_config.get("broker_port", 1883)
            )
            self.mqtt_client.loop_start()
            self._running = True
            
            logger.info(f"📡 Verbinde mit MQTT {self.mqtt_config['broker_ip']}...")
            return True
            
        except Exception as e:
            logger.error(f"MQTT Fehler: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("📡 MQTT verbunden!")
            # Alle Device-Topics abonnieren
            topic = self.mqtt_config.get("topic_prefix", "holo/devices/#")
            client.subscribe(topic)
            logger.info(f"   Subscribed: {topic}")
        else:
            logger.error(f"MQTT Verbindung fehlgeschlagen: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        logger.warning(f"📡 MQTT getrennt (rc={rc})")
    
    def _on_message(self, client, userdata, msg):
        """Verarbeitet eingehende MQTT Nachrichten"""
        try:
            topic = msg.topic
            payload = msg.payload.decode("utf-8")
            
            # Topic parsen: holo/devices/{device_name}/{type}
            parts = topic.split("/")
            if len(parts) < 4:
                return
            
            device_name = parts[2]
            msg_type = parts[3]
            
            if msg_type == "state":
                self._handle_state_update(device_name, json.loads(payload))
            elif msg_type == "status":
                self._handle_status_update(device_name, payload)
            elif msg_type == "metrics":
                self._handle_metrics_update(device_name, json.loads(payload))
                
        except Exception as e:
            logger.error(f"MQTT Message Error: {e}")
    
    def _handle_state_update(self, device_name: str, data: Dict):
        """Verarbeitet komplettes State-Update"""
        with self._lock:
            now = datetime.now()
            
            # Metriken extrahieren
            metrics = data.get("metrics", {})
            
            # Device erstellen/aktualisieren
            device = DeviceInfo(
                name=device_name,
                display_name=data.get("display_name", device_name),
                device_type=data.get("device_type", "unknown"),
                icon=data.get("icon", "🖥️"),
                status=data.get("status", "online"),
                last_seen=now,
                hostname=data.get("hostname", ""),
                ip_address=data.get("ip_address", ""),
                cpu_percent=metrics.get("cpu_percent", 0),
                cpu_temp=metrics.get("cpu_temp"),
                ram_percent=metrics.get("ram_percent", 0),
                ram_used_gb=metrics.get("ram_used_gb", 0),
                ram_total_gb=metrics.get("ram_total_gb", 0),
                disk_percent=metrics.get("disk_percent", 0),
                disk_free_gb=metrics.get("disk_total_gb", 0) - metrics.get("disk_used_gb", 0),
                uptime_hours=metrics.get("uptime_hours", 0),
                shared_folders=data.get("shared_folders", [])
            )
            
            self._devices[device_name] = device
            
            # In DB speichern
            self._save_device_to_db(device)
            self._save_metrics_to_db(device)
            self._save_folders_to_db(device_name, data.get("shared_folders", []))
            
            logger.debug(f"📥 {device_name}: {device.status} (CPU: {device.cpu_percent:.0f}%)")
    
    def _handle_status_update(self, device_name: str, status: str):
        """Verarbeitet Status-Update"""
        with self._lock:
            if device_name in self._devices:
                self._devices[device_name].status = status
                self._devices[device_name].last_seen = datetime.now()
            else:
                # Neues Gerät mit minimalem Info
                self._devices[device_name] = DeviceInfo(
                    name=device_name,
                    display_name=device_name,
                    device_type="unknown",
                    icon="🖥️",
                    status=status,
                    last_seen=datetime.now()
                )
    
    def _handle_metrics_update(self, device_name: str, metrics: Dict):
        """Verarbeitet Metriken-Update"""
        with self._lock:
            if device_name in self._devices:
                device = self._devices[device_name]
                device.cpu_percent = metrics.get("cpu_percent", device.cpu_percent)
                device.cpu_temp = metrics.get("cpu_temp", device.cpu_temp)
                device.ram_percent = metrics.get("ram_percent", device.ram_percent)
                device.last_seen = datetime.now()
    
    def _save_device_to_db(self, device: DeviceInfo):
        """Speichert Gerät in DB"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO devices 
                    (name, display_name, device_type, icon, hostname, ip_address, first_seen, last_seen, last_status)
                    VALUES (?, ?, ?, ?, ?, ?, 
                            COALESCE((SELECT first_seen FROM devices WHERE name = ?), ?),
                            ?, ?)
                ''', (
                    device.name, device.display_name, device.device_type,
                    device.icon, device.hostname, device.ip_address,
                    device.name, datetime.now().isoformat(),
                    datetime.now().isoformat(), device.status
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"DB Save Error: {e}")
    
    def _save_metrics_to_db(self, device: DeviceInfo):
        """Speichert Metriken in History"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO metrics_history 
                    (device_name, timestamp, cpu_percent, cpu_temp, ram_percent, disk_percent, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    device.name, datetime.now().isoformat(),
                    device.cpu_percent, device.cpu_temp,
                    device.ram_percent, device.disk_percent, device.status
                ))
                
                # Alte Einträge löschen (älter als 7 Tage)
                cutoff = (datetime.now() - timedelta(days=7)).isoformat()
                conn.execute('DELETE FROM metrics_history WHERE timestamp < ?', (cutoff,))
                
                conn.commit()
        except Exception as e:
            logger.error(f"Metrics Save Error: {e}")
    
    def _save_folders_to_db(self, device_name: str, folders: List[Dict]):
        """Speichert Ordner in DB"""
        if not folders:
            return
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Alte Einträge löschen
                conn.execute('DELETE FROM shared_folders WHERE device_name = ?', (device_name,))
                
                # Neue einfügen
                for folder in folders:
                    conn.execute('''
                        INSERT INTO shared_folders 
                        (device_name, path, name, folder_type, size_gb, file_count, subfolders, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        device_name,
                        folder.get("path", ""),
                        folder.get("name", ""),
                        folder.get("type", "sonstiges"),
                        folder.get("size_gb"),
                        folder.get("file_count"),
                        json.dumps(folder.get("subfolders", [])),
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
        except Exception as e:
            logger.error(f"Folders Save Error: {e}")
    
    def stop(self):
        """Stoppt den Receiver"""
        self._running = False
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        logger.info("📡 Device Receiver gestoppt")
    
    # =========================================================================
    # API FÜR HOLO
    # =========================================================================
    
    def get_device(self, name: str) -> Optional[DeviceInfo]:
        """Gibt Info über ein Gerät zurück"""
        with self._lock:
            return self._devices.get(name)
    
    def get_all_devices(self) -> List[DeviceInfo]:
        """Gibt alle bekannten Geräte zurück"""
        with self._lock:
            return list(self._devices.values())
    
    def get_online_devices(self) -> List[DeviceInfo]:
        """Gibt nur online Geräte zurück"""
        with self._lock:
            return [d for d in self._devices.values() if d.is_online()]
    
    def get_offline_devices(self) -> List[DeviceInfo]:
        """Gibt offline Geräte zurück"""
        with self._lock:
            return [d for d in self._devices.values() if not d.is_online()]
    
    def get_device_by_type(self, device_type: str) -> List[DeviceInfo]:
        """Gibt Geräte eines bestimmten Typs zurück"""
        with self._lock:
            return [d for d in self._devices.values() if d.device_type == device_type]
    
    def search_content(self, query: str) -> List[Dict]:
        """Sucht in allen Shared Folders nach einem Begriff"""
        results = []
        query_lower = query.lower()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # In Ordnernamen suchen
            rows = conn.execute('''
                SELECT sf.*, d.display_name as device_display
                FROM shared_folders sf
                JOIN devices d ON sf.device_name = d.name
                WHERE LOWER(sf.name) LIKE ? OR LOWER(sf.path) LIKE ?
            ''', (f'%{query_lower}%', f'%{query_lower}%')).fetchall()
            
            for row in rows:
                results.append({
                    "device": row['device_name'],
                    "device_display": row['device_display'],
                    "path": row['path'],
                    "name": row['name'],
                    "type": row['folder_type'],
                    "match_type": "folder"
                })
            
            # In Subfolders suchen
            rows = conn.execute('''
                SELECT sf.*, d.display_name as device_display
                FROM shared_folders sf
                JOIN devices d ON sf.device_name = d.name
                WHERE sf.subfolders LIKE ?
            ''', (f'%{query_lower}%',)).fetchall()
            
            for row in rows:
                subfolders = json.loads(row['subfolders'] or '[]')
                for subfolder in subfolders:
                    if query_lower in subfolder.lower():
                        results.append({
                            "device": row['device_name'],
                            "device_display": row['device_display'],
                            "path": f"{row['path']}/{subfolder}",
                            "name": subfolder,
                            "type": row['folder_type'],
                            "match_type": "subfolder"
                        })
        
        return results
    
    def get_summary(self) -> Dict:
        """Gibt Zusammenfassung aller Geräte zurück"""
        with self._lock:
            devices = list(self._devices.values())
            
            online = [d for d in devices if d.is_online()]
            offline = [d for d in devices if not d.is_online()]
            
            return {
                "total_devices": len(devices),
                "online_count": len(online),
                "offline_count": len(offline),
                "devices": {
                    d.name: {
                        "display_name": d.display_name,
                        "type": d.device_type,
                        "icon": d.icon,
                        "status": d.status if d.is_online() else "offline",
                        "status_emoji": d.get_status_emoji(),
                        "cpu": d.cpu_percent if d.is_online() else None,
                        "ram": d.ram_percent if d.is_online() else None,
                        "last_seen": d.last_seen.isoformat()
                    }
                    for d in devices
                }
            }
    
    def format_status_message(self) -> str:
        """Formatiert Status für Holo's Antwort"""
        summary = self.get_summary()
        
        if summary["total_devices"] == 0:
            return "*Ohren hängen* Ich kenne noch keine Geräte im Netzwerk..."
        
        lines = ["*Ohren spitzen sich* Hier sind deine Geräte:\n"]
        
        for name, info in summary["devices"].items():
            emoji = info["status_emoji"]
            icon = info["icon"]
            display = info["display_name"]
            status = info["status"]
            
            line = f"{emoji} {icon} **{display}** - {status}"
            
            if info["cpu"] is not None:
                line += f" (CPU: {info['cpu']:.0f}%"
                if info["ram"] is not None:
                    line += f", RAM: {info['ram']:.0f}%"
                line += ")"
            
            lines.append(line)
        
        lines.append(f"\n📊 {summary['online_count']}/{summary['total_devices']} Geräte online")
        
        return "\n".join(lines)


# =============================================================================
# HOLO INTEGRATION HELPER
# =============================================================================

class HoloDeviceIntegration:
    """
    Einfache Integration für Holo Brain.
    Nutzt den DeviceReceiver und bietet Query-Handling.
    """
    
    def __init__(self, receiver: HoloDeviceReceiver):
        self.receiver = receiver
    
    def handle_query(self, text: str) -> Optional[Dict]:
        """
        Verarbeitet Geräte-bezogene Anfragen.
        Gibt Dict mit 'type' und 'reply' zurück oder None.
        """
        import re
        t = text.lower().strip()
        
        # === NETZWERK STATUS ===
        if any(p in t for p in [
            "welche geräte sind an", "welche geräte sind online",
            "netzwerk status", "geräte status", "was ist online",
            "welche rechner laufen", "was läuft gerade"
        ]):
            return {
                "type": "network_status",
                "reply": self.receiver.format_status_message()
            }
        
        # === SPEZIFISCHES GERÄT ===
        device_patterns = [
            r'(?:wie geht es|status|was macht)\s+(?:dem\s+|der\s+)?(\w+(?:[\s-]\w+)?)',
            r'ist\s+(?:der\s+|die\s+|das\s+)?(\w+(?:[\s-]\w+)?)\s+(?:an|online|aus|offline)',
            r'läuft\s+(?:der\s+|die\s+|das\s+)?(\w+(?:[\s-]\w+)?)',
        ]
        
        for pattern in device_patterns:
            match = re.search(pattern, t)
            if match:
                device_query = match.group(1).strip().lower()
                return self._get_device_status(device_query)
        
        # === WO IST DATEI ===
        where_patterns = [
            r'wo (?:ist|sind|finde ich)\s+(.+?)(?:\?|$)',
            r'auf welchem (?:gerät|rechner|pc)\s+ist\s+(.+)',
        ]
        
        for pattern in where_patterns:
            match = re.search(pattern, t)
            if match:
                query = match.group(1).strip()
                return self._search_content(query)
        
        return None
    
    def _get_device_status(self, query: str) -> Dict:
        """Gibt Status eines spezifischen Geräts zurück"""
        # Versuche Gerät zu finden
        device = None
        
        for d in self.receiver.get_all_devices():
            if (query in d.name.lower() or 
                query in d.display_name.lower() or
                query in d.device_type.lower()):
                device = d
                break
        
        if not device:
            return {
                "type": "device_not_found",
                "reply": f"*kratzt sich am Ohr* Hmm, '{query}' kenne ich nicht als Gerät..."
            }
        
        emoji = device.get_status_emoji()
        status = device.status if device.is_online() else "offline"
        
        response = f"{emoji} {device.icon} **{device.display_name}** ist **{status}**"
        
        if device.is_online():
            response += f"\n\n📊 CPU: {device.cpu_percent:.0f}%"
            if device.cpu_temp:
                response += f" ({device.cpu_temp:.0f}°C)"
            response += f"\n💾 RAM: {device.ram_percent:.0f}% ({device.ram_used_gb:.1f}/{device.ram_total_gb:.1f} GB)"
            response += f"\n💿 Disk: {device.disk_percent:.0f}%"
            response += f"\n⏱️ Uptime: {device.uptime_hours:.1f}h"
        else:
            response += f"\n\n*Ohren sinken* Zuletzt online: {device.last_seen.strftime('%d.%m. %H:%M')}"
        
        return {
            "type": "device_status",
            "reply": response,
            "device": device
        }
    
    def _search_content(self, query: str) -> Dict:
        """Sucht nach Inhalten auf allen Geräten"""
        results = self.receiver.search_content(query)
        
        if not results:
            return {
                "type": "content_not_found",
                "reply": f"*kratzt sich am Ohr* '{query}' hab ich auf keinem Gerät gefunden..."
            }
        
        # Gruppiere nach Gerät
        by_device = {}
        for r in results:
            device = r["device_display"]
            if device not in by_device:
                by_device[device] = []
            by_device[device].append(r)
        
        response = f"*Schweif wedelt* Ich hab **{query}** gefunden:\n\n"
        
        for device, items in by_device.items():
            response += f"📁 **{device}:**\n"
            for item in items[:3]:
                response += f"  • `{item['path']}`\n"
            if len(items) > 3:
                response += f"  ... und {len(items)-3} weitere\n"
            response += "\n"
        
        return {
            "type": "content_found",
            "reply": response,
            "results": results
        }


# =============================================================================
# STANDALONE TEST / MONITOR
# =============================================================================

def run_monitor():
    """Startet als standalone Monitor"""
    import time
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    
    print("\n" + "="*50)
    print("🐺 HOLO DEVICE RECEIVER - Monitor Mode")
    print("="*50 + "\n")
    
    receiver = HoloDeviceReceiver(data_dir="/tmp/holo_devices")
    
    if not receiver.start():
        print("❌ Konnte nicht starten!")
        return
    
    print("📡 Warte auf Geräte-Updates...\n")
    print("Drücke Ctrl+C zum Beenden\n")
    
    try:
        while True:
            time.sleep(10)
            
            # Status ausgeben
            summary = receiver.get_summary()
            print(f"\r📊 {summary['online_count']}/{summary['total_devices']} Geräte online", end="")
            
            for name, info in summary["devices"].items():
                if info["status"] != "offline":
                    print(f" | {info['icon']} {name}: {info['status']}", end="")
            
            print("          ", end="")  # Clear rest of line
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Beende...")
    finally:
        receiver.stop()


if __name__ == "__main__":
    run_monitor()
