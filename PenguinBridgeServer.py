"""
PenguinBridge - A reusable, lightweight, bidirectional Python bridge for PenguinMod.
No external dependencies (uses built-in http.server and threading).

This module can be imported into any other Python script to listen to broadcasts
from and send broadcasts to a packaged PenguinMod app.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable, Dict, List

class PenguinBridge:
    def __init__(self, host: str = "127.0.0.1", port: int = 6035):
        self.host = host
        self.port = port
        self.server: HTTPServer = None
        self.server_thread: threading.Thread = None
        
        # Thread safety lock for the outgoing message queue
        self._queue_lock = threading.Lock()
        # Queue holding messages waiting to be fetched by PenguinMod
        self._outgoing_queue: List[Dict[str, str]] = []
        
        # Event callbacks map: { "broadcast_name": [callback_functions] }
        self._handlers: Dict[str, List[Callable]] = {}
        # Wildcard handlers that catch EVERY broadcast from PenguinMod
        self._wildcard_handlers: List[Callable] = []

    def on(self, event_name: str):
        """
        Decorator to register a callback function for a specific PenguinMod broadcast.
        
        Example:
            @bridge.on("player_scored")
            def on_score(data):
                print(f"Score updated to {data}")
        """
        def decorator(func: Callable):
            if event_name not in self._handlers:
                self._handlers[event_name] = []
            self._handlers[event_name].append(func)
            return func
        return decorator

    def on_any(self, func: Callable):
        """
        Decorator to register a wildcard callback for ANY broadcast from PenguinMod.
        The function must accept two arguments: (event_name, data).
        """
        self._wildcard_handlers.append(func)
        return func

    def trigger(self, event_name: str, data: str):
        """Manually trigger registered callbacks (used internally by HTTP handler)."""
        for handler in self._wildcard_handlers:
            try:
                handler(event_name, data)
            except Exception as e:
                print(f"[PenguinBridge Error] In wildcard callback: {e}")

        if event_name in self._handlers:
            for handler in self._handlers[event_name]:
                try:
                    handler(data)
                except Exception as e:
                    print(f"[PenguinBridge Error] In callback for '{event_name}': {e}")

    def send(self, event_name: str, data: str = ""):
        """
        Send a broadcast from Python to the PenguinMod project.
        
        Example:
            bridge.send("game_start_countdown", "3... 2... 1!")
        """
        with self._queue_lock:
            self._outgoing_queue.append({
                "event": event_name,
                "data": str(data)
            })

    def _create_handler_class(self):
        """Creates an isolated HTTP request handler class closed over this instance."""
        bridge_instance = self

        class BridgeHTTPRequestHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                # Suppress default HTTP logging to keep console clean
                pass

            def _set_cors_headers(self):
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')

            def do_OPTIONS(self):
                self.send_response(200)
                self._set_cors_headers()
                self.end_headers()

            def do_GET(self):
                """Handles connection health checks and background event polling."""
                self._set_cors_headers()
                
                if self.path == '/poll':
                    # Retrieve and clear the outgoing message queue safely
                    with bridge_instance._queue_lock:
                        events_to_send = list(bridge_instance._outgoing_queue)
                        bridge_instance._outgoing_queue.clear()
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(events_to_send).encode('utf-8'))
                    
                elif self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "online"}).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.end_headers()

            def do_POST(self):
                """Receives broadcasts coming from PenguinMod."""
                if self.path == '/broadcast':
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    
                    try:
                        payload = json.loads(post_data.decode('utf-8'))
                        broadcast_name = payload.get('broadcast', '')
                        data = payload.get('data', '')
                        
                        bridge_instance.trigger(broadcast_name, data)
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self._set_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"status": "received"}).encode('utf-8'))
                    except Exception:
                        self.send_response(400)
                        self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()

        return BridgeHTTPRequestHandler

    def start(self, blocking: bool = False):
        """Starts the local server (non-blocking background thread by default)."""
        handler_class = self._create_handler_class()
        self.server = HTTPServer((self.host, self.port), handler_class)
        
        def run_loop():
            self.server.serve_forever()

        if blocking:
            print(f"PenguinBridge starting on http://{self.host}:{self.port} (Blocking mode)")
            run_loop()
        else:
            self.server_thread = threading.Thread(target=run_loop, daemon=True)
            self.server_thread.start()
            print(f"PenguinBridge starting on http://{self.host}:{self.port} (Background thread)")

    def stop(self):
        """Stops the server cleanly."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("🔌 PenguinBridge stopped.")


# =====================================================================
# RUNNABLE DEMO (Simulates bidirectional interaction)
# =====================================================================
if __name__ == '__main__':
    import time
    
    bridge = PenguinBridge(port=6035)

    # When PenguinMod tells us it loaded, greet it from Python!
    @bridge.on("client_ready")
    def on_client_ready(data):
        print("PenguinMod client is ready! Sending welcome signal back...")
        bridge.send("welcome_message", "Hello, world!")

    # When PenguinMod sends a general message, print it here
    @bridge.on_any
    def log_everything(event_name, data):
        print(f"RECV -> '{event_name}' DATA: '{data}'")

    bridge.start(blocking=False)

    print("Type anything in this console and press Enter to broadcast it to the PenguinMod project!")
    try:
        while True:
            # Let the user type messages directly in the terminal to send to PenguinMod!
            user_input = input("")
            if user_input.strip():
                bridge.send("console_input", user_input)
    except KeyboardInterrupt:
        bridge.stop()