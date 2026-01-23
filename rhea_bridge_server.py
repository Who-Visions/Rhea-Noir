import os
import subprocess
import json
import glob
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import threading

# Configuration
PORT = 8000
RENDER_SCRIPT = "rhea_variations_render.py"
ARTIFACT_DIR = r"c:\Users\super\.gemini\antigravity\brain\a1beb3a9-4c2d-41fa-b2f6-5fe5709853ce"
# Firebase config path
FIREBASE_CRED = r"config\firebase_service_account.json"

class RheaBridgeHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        
        # Endpoint: /status
        if parsed.path == "/status":
            self._set_headers()
            status = {"status": "online", "render_active": False} 
            self.wfile.write(json.dumps(status).encode())
            
        # Endpoint: /gallery
        elif parsed.path == "/gallery":
            self._set_headers()
            files = glob.glob(os.path.join(ARTIFACT_DIR, "cortex_*.png"))
            files = [os.path.basename(f) for f in files]
            self.wfile.write(json.dumps({"files": files}).encode())
        
        # Endpoint: /assets/
        elif parsed.path.startswith("/assets/"):
            filename = parsed.path.replace("/assets/", "")
            filepath = os.path.join(ARTIFACT_DIR, filename)
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-type", "image/png")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_POST(self):
        parsed = urlparse(self.path)
        
        # Endpoint: /render?key=Xoah_Prime_23
        if parsed.path == "/render":
            query = parse_qs(parsed.query)
            key = query.get("key", [None])[0]
            
            if key:
                print(f"🚀 Bridge: Triggering render for {key}")
                def run_render():
                    subprocess.run(["python", RENDER_SCRIPT, "--key", key])
                
                thread = threading.Thread(target=run_render)
                thread.start()
                
                self._set_headers()
                self.wfile.write(json.dumps({"message": f"Render triggered for {key}"}).encode())
            else:
                self.send_response(400)
                self.end_headers()

        # Endpoint: /chat
        elif parsed.path == "/chat":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            user_message = data.get('message', '')
            
            print(f"💬 Rhea Cloud Relay: {user_message}")
            
            try:
                # Proxy to Local Dev Server (Bypass Cloud 500)
                import requests
                LOCAL_SERVER_URL = "http://localhost:8081/v1/chat/completions"
                
                # Construct OpenAI-compatible payload
                payload = {
                    "messages": [
                        {"role": "system", "content": "You are Rhea, the AI Intelligence of the Watchtower. Keep responses short for mobile command."},
                        {"role": "user", "content": user_message}
                    ],
                    "model": "gemini-3-flash-preview" # Smart Router Target
                }
                
                resp = requests.post(LOCAL_SERVER_URL, json=payload, timeout=60)
                
                if resp.status_code == 200:
                    r_json = resp.json()
                    # extract content from openai format
                    reply = r_json['choices'][0]['message']['content']
                else:
                    reply = f"Cloud Error: {resp.status_code} - {resp.text}"
                    
            except Exception as e:
                print(f"Chat Proxy Error: {e}")
                reply = f"Rhea Link Unstable. {str(e)}"

            self._set_headers()
            self.wfile.write(json.dumps({"reply": reply}).encode())
                
        else:
            self.send_response(404)
            self.end_headers()

def run(server_class=ThreadingHTTPServer, handler_class=RheaBridgeHandler):
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    print(f"🌉 Rhea Bridge Server running on port {PORT}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == "__main__":
    run()
