from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # mendapatkan alamat IP pengguna dari request
        user_ip = self.headers.get('X-Forwarded-For', self.client_address[0])
        response = {"ip": user_ip}

        # mengatur respons menjadi JSON
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
