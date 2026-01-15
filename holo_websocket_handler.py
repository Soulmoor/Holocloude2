#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO WEBSOCKET HANDLER - Echtzeit-Kommunikation mit Typing-Effekt           ║
║                                                                              ║
║  Features:                                                                   ║
║  • Realistisches Character-by-Character Streaming                            ║
║  • Proaktive Nachrichten (Idle, Gedanken, Träume)                            ║
║  • Status-Updates (Energie, Stimmung)                                        ║
║  • Typing-Indicator                                                          ║
║                                                                              ║
║  Kann standalone oder in bestehenden Flask/FastAPI Server integriert werden  ║
║                                                                              ║
║  Author: Kira & Claude                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import json
import logging
import time
import threading
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger("HoloWebSocket")


# =============================================================================
# MESSAGE TYPES
# =============================================================================

class MessageType(Enum):
    """WebSocket Nachricht-Typen"""
    # Client → Server
    USER_MESSAGE = "user_message"
    USER_TYPING = "user_typing"
    USER_STOPPED_TYPING = "user_stopped_typing"
    PING = "ping"
    REQUEST_STATUS = "request_status"
    
    # Server → Client
    HOLO_TYPING_START = "holo_typing_start"
    HOLO_CHAR = "holo_char"           # Einzelnes Zeichen
    HOLO_CHUNK = "holo_chunk"         # Mehrere Zeichen (Burst)
    HOLO_TYPING_END = "holo_typing_end"
    HOLO_MESSAGE = "holo_message"     # Komplette Nachricht (Fallback)
    HOLO_PROACTIVE = "holo_proactive" # Proaktive Nachricht
    HOLO_STATUS = "holo_status"       # Status-Update
    HOLO_ERROR = "holo_error"
    PONG = "pong"


@dataclass
class WebSocketMessage:
    """Eine WebSocket Nachricht"""
    type: str
    data: Dict
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_json(self) -> str:
        return json.dumps({
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WebSocketMessage':
        data = json.loads(json_str)
        return cls(
            type=data.get("type", "unknown"),
            data=data.get("data", {}),
            timestamp=data.get("timestamp", time.time())
        )


# =============================================================================
# TYPING STREAMER
# =============================================================================

class TypingStreamer:
    """
    Streamt Text mit realistischem Typing-Effekt über WebSocket.
    
    Kann sowohl synchron als auch asynchron genutzt werden.
    """
    
    def __init__(self, organic_presence=None):
        """
        Args:
            organic_presence: Optional OrganicPresenceManager für Timing
        """
        self.organic_presence = organic_presence
        
        # Fallback-Timing wenn kein OrganicPresence
        self.base_delay_ms = 30
        self.variance_ms = 20
        self.pause_comma_ms = 150
        self.pause_period_ms = 300
        self.pause_newline_ms = 400
    
    async def stream_text(self, 
                          text: str, 
                          send_callback: Callable[[str], Any],
                          energy_level: float = 0.7,
                          mood: str = "neutral") -> None:
        """
        Streame Text Character-by-Character.
        
        Args:
            text: Zu streamender Text
            send_callback: Async Callback für jede Nachricht
            energy_level: Energie-Level (beeinflusst Geschwindigkeit)
            mood: Stimmung (beeinflusst Stil)
        """
        # Typing Start senden
        await send_callback(WebSocketMessage(
            type=MessageType.HOLO_TYPING_START.value,
            data={"total_length": len(text)}
        ).to_json())
        
        # Nutze OrganicPresence wenn verfügbar
        if self.organic_presence and hasattr(self.organic_presence, 'typing'):
            chars = list(self.organic_presence.typing.simulate_typing(
                text, energy_level, mood
            ))
            
            buffer = ""
            last_send = time.time()
            
            for typed_char in chars:
                if typed_char.is_correction:
                    # Backspace senden
                    if buffer:
                        buffer = buffer[:-1]
                    await send_callback(WebSocketMessage(
                        type=MessageType.HOLO_CHAR.value,
                        data={"char": "\b", "is_correction": True}
                    ).to_json())
                elif typed_char.char:
                    buffer += typed_char.char
                    
                    # Sende einzelnes Zeichen
                    await send_callback(WebSocketMessage(
                        type=MessageType.HOLO_CHAR.value,
                        data={
                            "char": typed_char.char,
                            "delay_ms": typed_char.delay_ms,
                            "buffer": buffer
                        }
                    ).to_json())
                
                # Delay
                await asyncio.sleep(typed_char.delay_ms / 1000.0)
        else:
            # Fallback: Einfaches Streaming
            buffer = ""
            for char in text:
                delay = self._calculate_delay(char, energy_level)
                buffer += char
                
                await send_callback(WebSocketMessage(
                    type=MessageType.HOLO_CHAR.value,
                    data={
                        "char": char,
                        "delay_ms": delay,
                        "buffer": buffer
                    }
                ).to_json())
                
                await asyncio.sleep(delay / 1000.0)
        
        # Typing End senden
        await send_callback(WebSocketMessage(
            type=MessageType.HOLO_TYPING_END.value,
            data={"final_text": text}
        ).to_json())
    
    def _calculate_delay(self, char: str, energy_level: float) -> int:
        """Berechne Delay für ein Zeichen (Fallback)"""
        import random
        
        base = self.base_delay_ms
        variance = random.randint(-self.variance_ms, self.variance_ms)
        delay = base + variance
        
        # Sonderzeichen
        if char == ',':
            delay += self.pause_comma_ms
        elif char in '.!?':
            delay += self.pause_period_ms
        elif char == '\n':
            delay += self.pause_newline_ms
        
        # Energie-Einfluss
        if energy_level < 0.3:
            delay = int(delay * 1.5)  # Müde = langsamer
        elif energy_level > 0.8:
            delay = int(delay * 0.8)  # Energetisch = schneller
        
        return delay


# =============================================================================
# HOLO WEBSOCKET HANDLER
# =============================================================================

class HoloWebSocketHandler:
    """
    Hauptklasse für WebSocket-Kommunikation mit Holo.
    
    Unterstützt:
    - Flask-SocketIO
    - FastAPI WebSockets
    - Standalone asyncio
    """
    
    def __init__(self, holo_brain=None, organic_presence=None):
        """
        Args:
            holo_brain: HoloPersona Instanz
            organic_presence: OrganicPresenceManager Instanz
        """
        self.brain = holo_brain
        self.organic_presence = organic_presence
        self.streamer = TypingStreamer(organic_presence)
        
        # Connected clients
        self.clients: Dict[str, Any] = {}
        
        # Proactive message loop
        self._proactive_running = False
        self._proactive_task = None
        
        # Message handlers
        self._handlers: Dict[str, Callable] = {
            MessageType.USER_MESSAGE.value: self._handle_user_message,
            MessageType.USER_TYPING.value: self._handle_user_typing,
            MessageType.PING.value: self._handle_ping,
            MessageType.REQUEST_STATUS.value: self._handle_status_request,
        }
    
    def register_client(self, client_id: str, send_callback: Callable):
        """Registriere einen neuen Client"""
        self.clients[client_id] = {
            "send": send_callback,
            "connected_at": time.time(),
            "last_activity": time.time(),
        }
        logger.info(f"🔌 Client verbunden: {client_id}")
    
    def unregister_client(self, client_id: str):
        """Entferne einen Client"""
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"🔌 Client getrennt: {client_id}")
    
    async def handle_message(self, client_id: str, message: str) -> None:
        """
        Verarbeite eingehende WebSocket-Nachricht.
        
        Args:
            client_id: Client-ID
            message: JSON-String der Nachricht
        """
        try:
            msg = WebSocketMessage.from_json(message)
            
            # Update last activity
            if client_id in self.clients:
                self.clients[client_id]["last_activity"] = time.time()
            
            # Handler aufrufen
            handler = self._handlers.get(msg.type)
            if handler:
                await handler(client_id, msg)
            else:
                logger.warning(f"Unbekannter Message-Typ: {msg.type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON Parse Error: {e}")
            await self._send_error(client_id, "Invalid JSON")
        except Exception as e:
            logger.error(f"Message Handler Error: {e}")
            await self._send_error(client_id, str(e))
    
    async def _handle_user_message(self, client_id: str, msg: WebSocketMessage):
        """Verarbeite User-Nachricht"""
        user_text = msg.data.get("text", "")
        
        if not user_text.strip():
            return
        
        logger.info(f"📨 [{client_id}] User: {user_text[:50]}...")
        
        # Response generieren
        if self.brain:
            # Sammle Response (Generator)
            full_response = ""
            async for chunk in self._generate_response(user_text):
                full_response += chunk
            
            # Energie-Level für Typing holen
            energy_level = 0.7
            mood = "neutral"
            
            if self.organic_presence:
                if hasattr(self.organic_presence, 'energy_system'):
                    es = self.organic_presence.energy_system
                    if es and hasattr(es, 'state'):
                        energy_level = getattr(es.state, 'total_energy', 0.7)
                
                if hasattr(self.organic_presence, 'inner_life'):
                    il = self.organic_presence.inner_life
                    if il and hasattr(il, 'mood'):
                        m = getattr(il.mood, 'current_mood', None)
                        if m:
                            mood = m.value
            
            # Streame Response mit Typing-Effekt
            send_cb = self.clients.get(client_id, {}).get("send")
            if send_cb:
                await self.streamer.stream_text(
                    full_response, 
                    send_cb,
                    energy_level=energy_level,
                    mood=mood
                )
        else:
            # Kein Brain - Echo
            await self._send_message(client_id, f"Echo: {user_text}")
    
    async def _generate_response(self, user_text: str):
        """Generator für Brain-Response"""
        if not self.brain:
            yield "Kein Brain verbunden."
            return
        
        try:
            # Brain's generate_response ist ein Generator
            for chunk in self.brain.generate_response(user_text):
                # Prüfe auf __COMPLETE__ Marker
                if isinstance(chunk, str) and chunk.startswith("__COMPLETE__"):
                    break
                yield chunk
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            yield f"Entschuldige, ein Fehler ist aufgetreten: {e}"
    
    async def _handle_user_typing(self, client_id: str, msg: WebSocketMessage):
        """User tippt gerade"""
        # Könnte für "Holo wartet"-Animation genutzt werden
        pass
    
    async def _handle_ping(self, client_id: str, msg: WebSocketMessage):
        """Ping-Pong für Keepalive"""
        await self._send_to_client(client_id, WebSocketMessage(
            type=MessageType.PONG.value,
            data={"server_time": time.time()}
        ))
    
    async def _handle_status_request(self, client_id: str, msg: WebSocketMessage):
        """Sende Status-Update"""
        status = self._gather_status()
        await self._send_to_client(client_id, WebSocketMessage(
            type=MessageType.HOLO_STATUS.value,
            data=status
        ))
    
    def _gather_status(self) -> Dict:
        """Sammle aktuellen Status"""
        status = {
            "timestamp": time.time(),
            "connected_clients": len(self.clients),
        }
        
        # Organic Presence Status
        if self.organic_presence:
            try:
                status["organic"] = self.organic_presence.get_status()
            except Exception as e:
                logger.warning(f"[WebSocketHandler] get_status organic failed: {type(e).__name__}: {e}")

        # Brain Status
        if self.brain:
            try:
                if hasattr(self.brain, 'energy') and self.brain.energy:
                    es = self.brain.energy.get_status()
                    status["energy"] = {
                        "total": es.get("total_energy", 0),
                        "emotional": es.get("emotional_energy", 0),
                        "state": es.get("state", "unknown")
                    }

                if hasattr(self.brain, 'emotions') and self.brain.emotions:
                    status["mood"] = self.brain.emotions.get_mood()
            except Exception as e:
                logger.warning(f"[WebSocketHandler] get_status brain failed: {type(e).__name__}: {e}")
        
        return status
    
    async def _send_to_client(self, client_id: str, msg: WebSocketMessage):
        """Sende Nachricht an Client"""
        client = self.clients.get(client_id)
        if client and client.get("send"):
            try:
                await client["send"](msg.to_json())
            except Exception as e:
                logger.error(f"Send error to {client_id}: {e}")
    
    async def _send_message(self, client_id: str, text: str):
        """Sende einfache Text-Nachricht"""
        await self._send_to_client(client_id, WebSocketMessage(
            type=MessageType.HOLO_MESSAGE.value,
            data={"text": text}
        ))
    
    async def _send_error(self, client_id: str, error: str):
        """Sende Fehler-Nachricht"""
        await self._send_to_client(client_id, WebSocketMessage(
            type=MessageType.HOLO_ERROR.value,
            data={"error": error}
        ))
    
    async def broadcast(self, msg: WebSocketMessage):
        """Sende an alle Clients"""
        for client_id in list(self.clients.keys()):
            await self._send_to_client(client_id, msg)
    
    # =========================================================================
    # PROACTIVE MESSAGES
    # =========================================================================
    
    async def start_proactive_loop(self, interval: float = 30.0):
        """Starte Loop für proaktive Nachrichten"""
        if self._proactive_running:
            return
        
        self._proactive_running = True
        
        while self._proactive_running:
            try:
                await self._check_proactive()
            except Exception as e:
                logger.error(f"Proactive loop error: {e}")
            
            await asyncio.sleep(interval)
    
    def stop_proactive_loop(self):
        """Stoppe proaktiven Loop"""
        self._proactive_running = False
    
    async def _check_proactive(self):
        """Prüfe auf proaktive Nachrichten"""
        if not self.organic_presence:
            return
        
        msg = self.organic_presence.check_proactive_message()
        if msg:
            # An alle Clients senden
            await self.broadcast(WebSocketMessage(
                type=MessageType.HOLO_PROACTIVE.value,
                data={
                    "type": msg["type"],
                    "message": msg["message"],
                    "body_language": msg.get("body_language"),
                    "requires_response": msg.get("requires_response", False)
                }
            ))


# =============================================================================
# FLASK-SOCKETIO INTEGRATION
# =============================================================================

def create_flask_socketio_handler(app, socketio, holo_brain=None, organic_presence=None):
    """
    Erstellt Flask-SocketIO Handler.
    
    Usage:
        from flask import Flask
        from flask_socketio import SocketIO
        
        app = Flask(__name__)
        socketio = SocketIO(app, cors_allowed_origins="*")
        
        handler = create_flask_socketio_handler(app, socketio, brain, organic)
    """
    handler = HoloWebSocketHandler(holo_brain, organic_presence)
    
    @socketio.on('connect')
    def on_connect():
        from flask import request
        client_id = request.sid
        
        async def send_callback(msg):
            socketio.emit('message', msg, room=client_id)
        
        handler.register_client(client_id, send_callback)
    
    @socketio.on('disconnect')
    def on_disconnect():
        from flask import request
        handler.unregister_client(request.sid)
    
    @socketio.on('message')
    def on_message(data):
        from flask import request
        import asyncio
        
        # Async handler in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                handler.handle_message(request.sid, json.dumps(data) if isinstance(data, dict) else data)
            )
        finally:
            loop.close()
    
    return handler


# =============================================================================
# FASTAPI INTEGRATION
# =============================================================================

def create_fastapi_websocket_route(app, holo_brain=None, organic_presence=None):
    """
    Erstellt FastAPI WebSocket Route.
    
    Usage:
        from fastapi import FastAPI
        
        app = FastAPI()
        handler = create_fastapi_websocket_route(app, brain, organic)
    """
    from fastapi import WebSocket, WebSocketDisconnect
    
    handler = HoloWebSocketHandler(holo_brain, organic_presence)
    
    @app.websocket("/ws/holo")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        client_id = str(id(websocket))
        
        async def send_callback(msg):
            await websocket.send_text(msg)
        
        handler.register_client(client_id, send_callback)
        
        try:
            while True:
                data = await websocket.receive_text()
                await handler.handle_message(client_id, data)
        except WebSocketDisconnect:
            handler.unregister_client(client_id)
    
    return handler


# =============================================================================
# FRONTEND JAVASCRIPT
# =============================================================================

FRONTEND_JS = '''
/**
 * HOLO WebSocket Client
 * 
 * Verbindet mit Holo-Backend und zeigt Typing-Effekt an.
 */
class HoloWebSocket {
    constructor(url, options = {}) {
        this.url = url;
        this.options = {
            reconnect: true,
            reconnectDelay: 3000,
            onMessage: null,
            onTypingStart: null,
            onTypingChar: null,
            onTypingEnd: null,
            onProactive: null,
            onStatus: null,
            onConnect: null,
            onDisconnect: null,
            ...options
        };
        
        this.ws = null;
        this.buffer = '';
        this.isTyping = false;
        this.typingElement = null;
    }
    
    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('🐺 Holo WebSocket verbunden');
            if (this.options.onConnect) this.options.onConnect();
        };
        
        this.ws.onclose = () => {
            console.log('🐺 Holo WebSocket getrennt');
            if (this.options.onDisconnect) this.options.onDisconnect();
            
            if (this.options.reconnect) {
                setTimeout(() => this.connect(), this.options.reconnectDelay);
            }
        };
        
        this.ws.onerror = (error) => {
            console.error('🐺 WebSocket Fehler:', error);
        };
        
        this.ws.onmessage = (event) => {
            this._handleMessage(JSON.parse(event.data));
        };
    }
    
    _handleMessage(msg) {
        switch (msg.type) {
            case 'holo_typing_start':
                this.buffer = '';
                this.isTyping = true;
                if (this.options.onTypingStart) {
                    this.options.onTypingStart(msg.data);
                }
                break;
                
            case 'holo_char':
                const char = msg.data.char;
                if (char === '\\b') {
                    // Backspace
                    this.buffer = this.buffer.slice(0, -1);
                } else {
                    this.buffer += char;
                }
                
                if (this.options.onTypingChar) {
                    this.options.onTypingChar(char, this.buffer, msg.data.delay_ms);
                }
                
                // Update typing element if set
                if (this.typingElement) {
                    this.typingElement.textContent = this.buffer;
                }
                break;
                
            case 'holo_typing_end':
                this.isTyping = false;
                if (this.options.onTypingEnd) {
                    this.options.onTypingEnd(msg.data.final_text);
                }
                break;
                
            case 'holo_message':
                if (this.options.onMessage) {
                    this.options.onMessage(msg.data.text);
                }
                break;
                
            case 'holo_proactive':
                if (this.options.onProactive) {
                    this.options.onProactive(msg.data);
                }
                break;
                
            case 'holo_status':
                if (this.options.onStatus) {
                    this.options.onStatus(msg.data);
                }
                break;
                
            case 'pong':
                // Keepalive response
                break;
        }
    }
    
    send(text) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'user_message',
                data: { text: text },
                timestamp: Date.now() / 1000
            }));
        }
    }
    
    requestStatus() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'request_status',
                data: {},
                timestamp: Date.now() / 1000
            }));
        }
    }
    
    setTypingElement(element) {
        this.typingElement = element;
    }
    
    disconnect() {
        this.options.reconnect = false;
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Usage Example:
// const holo = new HoloWebSocket('ws://localhost:5005/ws/holo', {
//     onTypingStart: () => console.log('Holo tippt...'),
//     onTypingChar: (char, buffer) => document.getElementById('response').textContent = buffer,
//     onTypingEnd: (text) => console.log('Fertig:', text),
//     onProactive: (data) => showNotification(data.message)
// });
// holo.connect();
// holo.send('Hallo Holo!');
'''


# =============================================================================
# STANDALONE TEST SERVER
# =============================================================================

async def run_test_server(host: str = "localhost", port: int = 8765):
    """Startet einen einfachen Test-WebSocket-Server"""
    import websockets
    
    handler = HoloWebSocketHandler()
    
    async def handle_client(websocket, path):
        client_id = str(id(websocket))
        
        async def send_callback(msg):
            await websocket.send(msg)
        
        handler.register_client(client_id, send_callback)
        
        try:
            async for message in websocket:
                await handler.handle_message(client_id, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            handler.unregister_client(client_id)
    
    print(f"🐺 Holo WebSocket Test-Server auf ws://{host}:{port}")
    print(f"   Sende: {{\"type\": \"user_message\", \"data\": {{\"text\": \"Hallo\"}}}}")
    
    async with websockets.serve(handle_client, host, port):
        await asyncio.Future()  # Run forever


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(message)s'
    )
    
    print("=" * 60)
    print("🐺 HOLO WEBSOCKET HANDLER")
    print("=" * 60)
    
    if "--server" in sys.argv:
        # Starte Test-Server
        try:
            import websockets
            asyncio.run(run_test_server())
        except ImportError:
            print("❌ websockets nicht installiert: pip install websockets")
    
    elif "--js" in sys.argv:
        # Gib Frontend-JS aus
        print("\n📜 FRONTEND JAVASCRIPT:\n")
        print(FRONTEND_JS)
    
    else:
        # Test ohne Server
        print("\n🧪 TYPING STREAMER TEST:\n")
        
        streamer = TypingStreamer()
        
        async def test_streaming():
            chars_received = []
            
            async def mock_send(msg):
                data = json.loads(msg)
                if data["type"] == "holo_char":
                    chars_received.append(data["data"]["char"])
                    print(data["data"]["char"], end="", flush=True)
            
            test_text = "Hallo! Ich bin Holo... *wedelt* 🐺"
            print(f"Streaming: '{test_text}'\n")
            print("Output: ", end="")
            
            await streamer.stream_text(test_text, mock_send)
            
            print(f"\n\n✅ {len(chars_received)} Zeichen gestreamt")
        
        asyncio.run(test_streaming())
        
        print("\n" + "=" * 60)
        print("Optionen:")
        print("  --server  Startet Test-WebSocket-Server")
        print("  --js      Gibt Frontend-JavaScript aus")
        print("=" * 60)
