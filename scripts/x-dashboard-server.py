#!/usr/bin/env python3
"""XFactor dashboard API server - serves static files + handles settings actions."""

import subprocess, json, os, sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

OS_ENV = os.environ.copy()
OS_ENV["PATH"] = f"{os.path.expanduser('~/.local/bin')}:/usr/local/bin:/usr/bin:/bin:{OS_ENV.get('PATH', '')}"

DASHBOARD_DIR = os.path.expanduser("~/.hermes/x-dashboard")
PORT = 3000

class XFactorHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == "/api/status":
            self.send_json(self.get_status())
        elif path == "/api/disconnect":
            self.send_json(self.disconnect_x())
        elif path == "/api/reconnect":
            self.send_json(self.reconnect_info())
        else:
            super().do_GET()
    
    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/disconnect":
            self.send_json(self.disconnect_x())
        else:
            self.send_json({"error": "not found"}, 404)
    
    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    
    def get_status(self):
        """Check if xurl is authenticated and return status."""
        result = subprocess.run(["xurl", "auth", "status"], capture_output=True, text=True, timeout=15, env=OS_ENV)
        auth_output = result.stdout
        
        # Check if we have a working auth
        whoami = subprocess.run(["xurl", "whoami"], capture_output=True, text=True, timeout=15, env=OS_ENV)
        connected = whoami.returncode == 0
        
        status = "connected" if connected else "disconnected"
        handle = ""
        followers = 0
        
        if connected:
            try:
                data = json.loads(whoami.stdout)
                user = data.get("data", {})
                handle = user.get("username", "")
                followers = user.get("public_metrics", {}).get("followers_count", 0)
            except:
                pass
        
        return {
            "status": status,
            "handle": handle,
            "followers": followers,
            "has_oauth2": "oauth2:" in auth_output,
            "has_oauth1": "oauth1:" in auth_output,
        }
    
    def disconnect_x(self):
        """Remove the default app to disconnect."""
        # Get the default app name
        result = subprocess.run(["xurl", "auth", "status"], capture_output=True, text=True, timeout=15, env=OS_ENV)
        output = result.stdout
        
        # Find the active app (marked with ▸)
        app_name = None
        for line in output.split("\n"):
            if "▸" in line:
                parts = line.strip().split()
                if len(parts) > 1:
                    app_name = parts[1].strip().lstrip("▸").strip()
        
        if not app_name:
            return {"success": False, "error": "No active app found", "output": output[:500]}
        
        # Remove the app
        remove_result = subprocess.run(
            ["xurl", "auth", "apps", "remove", app_name],
            capture_output=True, text=True, timeout=15, env=OS_ENV
        )
        
        if remove_result.returncode == 0:
            return {"success": True, "message": f"App '{app_name}' removed. X account disconnected."}
        else:
            return {"success": False, "error": remove_result.stderr.strip() or remove_result.stdout.strip()}
    
    def reconnect_info(self):
        """Return instructions for reconnecting."""
        return {
            "instructions": [
                "1. Get your X API credentials from https://developer.x.com/en/portal/dashboard",
                "2. Run these commands in your terminal:",
                "",
                "xurl auth apps add xfactor --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET",
                "xurl auth oauth2 --app xfactor YOUR_HANDLE",
                "xurl auth default xfactor",
                "",
                "3. Verify with: xurl whoami",
                "4. Refresh this page"
            ]
        }

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), XFactorHandler)
    print(f"XFactor server running on http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()