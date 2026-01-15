#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO DEVICE AGENT v1.0
======================
Leichtgewichtiger Agent der auf jedem Gerät laufen kann.
Sendet System-Infos und Speicherorte an Holo via MQTT.

INSTALLATION:
    pip install paho-mqtt psutil

KONFIGURATION:
    Passe CONFIG unten an dein Gerät an!

STARTEN:
    python holo_device_agent.py
    
    # Oder als Service:
    # systemctl enable holo-device-agent
    # systemctl start holo-device-agent
"""

import os
import sys
import json
import time
import socket
import logging
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Optional imports
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("⚠️ paho-mqtt nicht installiert! pip install paho-mqtt")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil nicht installiert! pip install psutil")


# =============================================================================
# KONFIGURATION - PASSE DAS AN DEIN GERÄT AN!
# =============================================================================

CONFIG = {
    # === GERÄT ===
    "device": {
        "name": "mein-pc",           # Eindeutiger Name für dieses Gerät
        "display_name": "Mein PC",   # Anzeigename
        "type": "pc",                # pc, laptop, gaming-pc, server, mini-pc, pi
        "icon": "🖥️",                # Emoji für Anzeige
    },
    
    # === MQTT ===
    "mqtt": {
        "enabled": True,
        "broker_ip": "192.168.178.99",    # IP des MQTT Brokers
        "broker_port": 1883,
        "username": "kira",                # Falls Auth nötig
        "password": "123",
        "base_topic": "holo/devices/",     # Topic-Prefix
    },
    
    # === SYSTEM MONITORING ===
    "monitoring": {
        "enabled": True,
        "interval_seconds": 30,            # Wie oft Status senden
        "include_cpu": True,
        "include_ram": True,
        "include_temperature": True,       # CPU Temperatur (wenn verfügbar)
        "include_disk": True,
        "include_network": False,          # Netzwerk-Stats
        "include_processes": False,        # Top-Prozesse
    },
    
    # === SPEICHERORTE ===
    # Ordner die du mit Holo teilen willst
    "shared_folders": [
        # {"path": "D:/Games", "name": "Spiele", "type": "spiele"},
        # {"path": "C:/Users/Kira/Documents", "name": "Dokumente", "type": "dokumente"},
        # {"path": "E:/Filme", "name": "Filme", "type": "filme"},
    ],
    
    # === ACTIVITY DETECTION ===
    "activity": {
        "enabled": True,
        "cpu_busy_threshold": 30,      # Ab wieviel % CPU = busy
        "idle_timeout_minutes": 10,     # Nach X Minuten idle = idle status
    },
    
    # === LOGGING ===
    "log_level": "INFO",
}


# =============================================================================
# LOGGING SETUP
# =============================================================================

logging.basicConfig(
    level=getattr(logging, CONFIG["log_level"]),
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("HoloAgent")


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class SystemMetrics:
    """System-Metriken"""
    cpu_percent: float = 0.0
    cpu_temp: Optional[float] = None
    ram_percent: float = 0.0
    ram_used_gb: float = 0.0
    ram_total_gb: float = 0.0
    disk_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    uptime_hours: float = 0.0


@dataclass 
class DeviceStatus:
    """Kompletter Gerätestatus"""
    device_name: str
    display_name: str
    device_type: str
    icon: str
    status: str  # online, busy, idle, offline
    timestamp: str
    metrics: Optional[Dict] = None
    shared_folders: Optional[List[Dict]] = None
    hostname: str = ""
    ip_address: str = ""


# =============================================================================
# SYSTEM MONITOR
# =============================================================================

class SystemMonitor:
    """Sammelt System-Metriken"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.last_activity = time.time()
        
    def get_metrics(self) -> SystemMetrics:
        """Sammelt aktuelle System-Metriken"""
        metrics = SystemMetrics()
        
        if not PSUTIL_AVAILABLE:
            return metrics
        
        try:
            # CPU
            if self.config.get("include_cpu", True):
                metrics.cpu_percent = psutil.cpu_percent(interval=1)
            
            # RAM
            if self.config.get("include_ram", True):
                ram = psutil.virtual_memory()
                metrics.ram_percent = ram.percent
                metrics.ram_used_gb = ram.used / (1024**3)
                metrics.ram_total_gb = ram.total / (1024**3)
            
            # Temperatur
            if self.config.get("include_temperature", True):
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        # Verschiedene Sensoren je nach System
                        for name in ['coretemp', 'cpu_thermal', 'k10temp', 'acpitz']:
                            if name in temps:
                                metrics.cpu_temp = temps[name][0].current
                                break
                except Exception:
                    pass
            
            # Disk
            if self.config.get("include_disk", True):
                # Hauptpartition
                if sys.platform == "win32":
                    disk = psutil.disk_usage("C:\\")
                else:
                    disk = psutil.disk_usage("/")
                metrics.disk_percent = disk.percent
                metrics.disk_used_gb = disk.used / (1024**3)
                metrics.disk_total_gb = disk.total / (1024**3)
            
            # Uptime
            metrics.uptime_hours = (time.time() - psutil.boot_time()) / 3600
            
        except Exception as e:
            logger.error(f"Metrics error: {e}")
        
        return metrics
    
    def get_activity_status(self, metrics: SystemMetrics) -> str:
        """Bestimmt ob Gerät busy oder idle ist"""
        activity_config = CONFIG.get("activity", {})
        
        if not activity_config.get("enabled", True):
            return "online"
        
        cpu_threshold = activity_config.get("cpu_busy_threshold", 30)
        idle_timeout = activity_config.get("idle_timeout_minutes", 10) * 60
        
        # CPU busy?
        if metrics.cpu_percent > cpu_threshold:
            self.last_activity = time.time()
            return "busy"
        
        # Zu lange idle?
        if time.time() - self.last_activity > idle_timeout:
            return "idle"
        
        return "online"
    
    def scan_shared_folders(self) -> List[Dict]:
        """Scannt konfigurierte Ordner"""
        folders = []
        
        for folder_config in CONFIG.get("shared_folders", []):
            path = folder_config.get("path", "")
            
            if not os.path.exists(path):
                continue
            
            try:
                # Basis-Info
                folder_info = {
                    "path": path,
                    "name": folder_config.get("name", Path(path).name),
                    "type": folder_config.get("type", "sonstiges"),
                    "exists": True,
                }
                
                # Optional: Größe berechnen (kann langsam sein!)
                if folder_config.get("include_size", False):
                    total_size = 0
                    file_count = 0
                    for dirpath, dirnames, filenames in os.walk(path):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            try:
                                total_size += os.path.getsize(fp)
                                file_count += 1
                            except Exception:
                                pass
                        # Nur erste Ebene wenn zu groß
                        if file_count > 10000:
                            break
                    
                    folder_info["size_gb"] = total_size / (1024**3)
                    folder_info["file_count"] = file_count
                
                # Unterordner auflisten (erste Ebene)
                if folder_config.get("list_subfolders", True):
                    subfolders = []
                    try:
                        for entry in os.listdir(path):
                            entry_path = os.path.join(path, entry)
                            if os.path.isdir(entry_path) and not entry.startswith('.'):
                                subfolders.append(entry)
                        folder_info["subfolders"] = subfolders[:50]  # Max 50
                    except Exception:
                        pass
                
                folders.append(folder_info)
                
            except Exception as e:
                logger.debug(f"Folder scan error for {path}: {e}")
        
        return folders


# =============================================================================
# MQTT PUBLISHER
# =============================================================================

class MqttPublisher:
    """Sendet Daten via MQTT"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.client = None
        self.connected = False
        self.device_name = CONFIG["device"]["name"]
        
    def connect(self):
        """Verbindet mit MQTT Broker"""
        if not MQTT_AVAILABLE:
            logger.error("MQTT nicht verfügbar!")
            return False
        
        try:
            self.client = mqtt.Client(client_id=f"holo_agent_{self.device_name}")
            
            if self.config.get("username"):
                self.client.username_pw_set(
                    self.config["username"],
                    self.config.get("password", "")
                )
            
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            
            # Last Will - wird gesendet wenn Verbindung abbricht
            base_topic = self.config.get("base_topic", "holo/devices/")
            self.client.will_set(
                f"{base_topic}{self.device_name}/status",
                "offline",
                retain=True
            )
            
            self.client.connect(
                self.config["broker_ip"],
                self.config.get("broker_port", 1883),
                keepalive=60
            )
            self.client.loop_start()
            
            logger.info(f"📡 Verbinde mit MQTT {self.config['broker_ip']}...")
            return True
            
        except Exception as e:
            logger.error(f"MQTT Verbindungsfehler: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info("📡 MQTT verbunden!")
            # Online-Status senden
            self.publish_status("online")
        else:
            logger.error(f"MQTT Verbindung fehlgeschlagen: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        logger.warning(f"📡 MQTT getrennt (rc={rc})")
    
    def publish_status(self, status: str):
        """Sendet einfachen Status"""
        if not self.connected:
            return
        
        base_topic = self.config.get("base_topic", "holo/devices/")
        self.client.publish(
            f"{base_topic}{self.device_name}/status",
            status,
            retain=True
        )
    
    def publish_full_state(self, state: DeviceStatus):
        """Sendet kompletten Gerätestatus"""
        if not self.connected:
            return
        
        try:
            base_topic = self.config.get("base_topic", "holo/devices/")
            
            # Kompletter State
            self.client.publish(
                f"{base_topic}{self.device_name}/state",
                json.dumps(asdict(state), ensure_ascii=False),
                retain=True
            )
            
            # Einzelne Topics für einfachen Zugriff
            self.client.publish(
                f"{base_topic}{self.device_name}/status",
                state.status,
                retain=True
            )
            
            if state.metrics:
                self.client.publish(
                    f"{base_topic}{self.device_name}/metrics",
                    json.dumps(state.metrics),
                    retain=True
                )
            
            logger.debug(f"📤 State publiziert: {state.status}")
            
        except Exception as e:
            logger.error(f"MQTT Publish Error: {e}")
    
    def disconnect(self):
        """Trennt Verbindung"""
        if self.client:
            self.publish_status("offline")
            self.client.loop_stop()
            self.client.disconnect()


# =============================================================================
# MAIN AGENT
# =============================================================================

class HoloDeviceAgent:
    """Hauptklasse des Device Agents"""
    
    def __init__(self):
        self.monitor = SystemMonitor(CONFIG.get("monitoring", {}))
        self.mqtt = MqttPublisher(CONFIG.get("mqtt", {}))
        self._running = False
        
        # Hostname & IP ermitteln
        self.hostname = socket.gethostname()
        try:
            self.ip_address = socket.gethostbyname(self.hostname)
        except Exception:
            self.ip_address = "unknown"
    
    def start(self):
        """Startet den Agent"""
        logger.info(f"🚀 Holo Device Agent startet...")
        logger.info(f"   Gerät: {CONFIG['device']['display_name']} ({CONFIG['device']['name']})")
        logger.info(f"   Typ: {CONFIG['device']['type']}")
        logger.info(f"   Host: {self.hostname} ({self.ip_address})")
        
        # MQTT verbinden
        if CONFIG["mqtt"]["enabled"]:
            if not self.mqtt.connect():
                logger.error("MQTT Verbindung fehlgeschlagen!")
                return
        
        self._running = True
        
        # Initial-Status senden
        time.sleep(2)  # Warten auf MQTT-Verbindung
        self._send_status()
        
        # Hauptloop
        interval = CONFIG.get("monitoring", {}).get("interval_seconds", 30)
        logger.info(f"📊 Sende Status alle {interval} Sekunden")
        
        try:
            while self._running:
                self._send_status()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("⏹️ Agent wird beendet...")
        finally:
            self.stop()
    
    def _send_status(self):
        """Sammelt und sendet aktuellen Status"""
        try:
            # Metriken sammeln
            metrics = self.monitor.get_metrics()
            activity = self.monitor.get_activity_status(metrics)
            
            # Ordner scannen (nicht bei jedem Update)
            folders = self.monitor.scan_shared_folders()
            
            # Status zusammenbauen
            device_config = CONFIG["device"]
            status = DeviceStatus(
                device_name=device_config["name"],
                display_name=device_config["display_name"],
                device_type=device_config["type"],
                icon=device_config.get("icon", "🖥️"),
                status=activity,
                timestamp=datetime.now().isoformat(),
                metrics=asdict(metrics),
                shared_folders=folders,
                hostname=self.hostname,
                ip_address=self.ip_address
            )
            
            # Via MQTT senden
            self.mqtt.publish_full_state(status)
            
            # Log
            temp_str = f", {metrics.cpu_temp:.0f}°C" if metrics.cpu_temp else ""
            logger.info(f"📊 {activity.upper()}: CPU {metrics.cpu_percent:.0f}%{temp_str}, RAM {metrics.ram_percent:.0f}%")
            
        except Exception as e:
            logger.error(f"Status Error: {e}")
    
    def stop(self):
        """Stoppt den Agent"""
        self._running = False
        self.mqtt.disconnect()
        logger.info("👋 Agent beendet")


# =============================================================================
# CLI & SETUP HELPER
# =============================================================================

def setup_wizard():
    """Interaktiver Setup-Assistent"""
    print("\n" + "="*50)
    print("🐺 HOLO DEVICE AGENT - Setup Wizard")
    print("="*50 + "\n")
    
    print("Beantworte ein paar Fragen um den Agent zu konfigurieren:\n")
    
    # Gerätename
    default_name = socket.gethostname().lower().replace(" ", "-")
    name = input(f"1. Gerätename (eindeutig) [{default_name}]: ").strip()
    if not name:
        name = default_name
    
    # Display Name
    display = input(f"2. Anzeigename [{name.title()}]: ").strip()
    if not display:
        display = name.title()
    
    # Typ
    print("\n   Gerätetypen: pc, laptop, gaming-pc, server, mini-pc, pi")
    device_type = input("3. Gerätetyp [pc]: ").strip().lower()
    if not device_type:
        device_type = "pc"
    
    # MQTT Broker
    broker = input("\n4. MQTT Broker IP [192.168.178.99]: ").strip()
    if not broker:
        broker = "192.168.178.99"
    
    # Generiere Config
    config = f'''
# =============================================================================
# HOLO DEVICE AGENT CONFIG - {display}
# =============================================================================

CONFIG = {{
    "device": {{
        "name": "{name}",
        "display_name": "{display}",
        "type": "{device_type}",
        "icon": "🖥️",
    }},
    
    "mqtt": {{
        "enabled": True,
        "broker_ip": "{broker}",
        "broker_port": 1883,
        "username": "kira",
        "password": "123",
        "base_topic": "holo/devices/",
    }},
    
    "monitoring": {{
        "enabled": True,
        "interval_seconds": 30,
        "include_cpu": True,
        "include_ram": True,
        "include_temperature": True,
        "include_disk": True,
    }},
    
    "shared_folders": [
        # Füge hier Ordner hinzu die du teilen willst:
        # {{"path": "D:/Games", "name": "Spiele", "type": "spiele"}},
        # {{"path": "C:/Users/{name}/Documents", "name": "Dokumente", "type": "dokumente"}},
    ],
    
    "activity": {{
        "enabled": True,
        "cpu_busy_threshold": 30,
        "idle_timeout_minutes": 10,
    }},
    
    "log_level": "INFO",
}}
'''
    
    print("\n" + "="*50)
    print("✅ Konfiguration erstellt!")
    print("="*50)
    print(config)
    
    save = input("\nSoll ich diese Config in 'holo_agent_config.py' speichern? [j/n]: ")
    if save.lower() in ['j', 'ja', 'y', 'yes']:
        with open("holo_agent_config.py", "w") as f:
            f.write(config)
        print("✅ Gespeichert! Kopiere die Config in dieses Skript oder importiere sie.")


def print_status():
    """Zeigt aktuellen System-Status"""
    print("\n" + "="*50)
    print("📊 SYSTEM STATUS")
    print("="*50)
    
    if PSUTIL_AVAILABLE:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/") if sys.platform != "win32" else psutil.disk_usage("C:\\")
        
        print(f"CPU:  {cpu:.1f}%")
        print(f"RAM:  {ram.percent:.1f}% ({ram.used/1024**3:.1f} / {ram.total/1024**3:.1f} GB)")
        print(f"Disk: {disk.percent:.1f}% ({disk.used/1024**3:.1f} / {disk.total/1024**3:.1f} GB)")
        
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    print(f"Temp ({name}): {entries[0].current:.1f}°C")
        except Exception:
            pass
    else:
        print("⚠️ psutil nicht installiert")
    
    print("="*50 + "\n")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Holo Device Agent")
    parser.add_argument("--setup", action="store_true", help="Interaktiver Setup")
    parser.add_argument("--status", action="store_true", help="Zeige System-Status")
    parser.add_argument("--once", action="store_true", help="Einmal Status senden und beenden")
    args = parser.parse_args()
    
    if args.setup:
        setup_wizard()
    elif args.status:
        print_status()
    else:
        # Agent starten
        agent = HoloDeviceAgent()
        agent.start()
