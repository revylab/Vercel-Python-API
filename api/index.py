from http.server import BaseHTTPRequestHandler
import json
import requests
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # ambil IP dari query parameter jika ada
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        user_ip = query_params.get('ip', [None])[0] or self.headers.get('X-Forwarded-For', self.client_address[0])

        # buat request ke ipinfo.io untuk data geolokasi
        token = "612faf773381a7"  # ganti dengan token ipinfo kamu
        url = f"https://ipinfo.io/{user_ip}?token={token}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()

            # ekstrak data geolokasi
            ip = data.get("ip")
            city = data.get("city")
            region = data.get("region")
            country = data.get("country")
            loc = data.get("loc")  # formatnya "latitude,longitude"
            org = data.get("org")  # info ISP atau organisasi
            hostname = data.get("hostname")  # mengambil hostname dari data

            # membagi latitude dan longitude
            latitude, longitude = loc.split(",") if loc else (None, None)

            # buat link google maps ke lokasi pengguna
            map_link = f"https://www.google.com/maps?q={latitude},{longitude}" if loc else None

            # susun respons dalam bentuk JSON
            result = {
                "ip": ip,
                "city": city,
                "region": region,
                "country": country,
                "latitude": latitude,
                "longitude": longitude,
                "organization": org,
                "map_link": map_link,
                "hostname": hostname  # gunakan hostname dari data IP
            }
        else:
            result = {"error": "could not retrieve location information"}

        # mengirimkan respons JSON ke pengguna
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))
