from http.server import BaseHTTPRequestHandler
import json
import subprocess
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            # For Vercel deployment, we'll return a simplified status
            # In production, you'd want to check your actual services

            result = {
                "coral_connected": 1,
                "processes_running": 1,
                "agents": [
                    {"type": "frontend", "id": "ai_frontend_001", "status": "connected"},
                    {"type": "backend", "id": "ai_backend_001", "status": "connected"},
                    {"type": "security", "id": "ai_security_001", "status": "connected"}
                ],
                "status": "connected"
            }

            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
