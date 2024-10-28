from http.server import BaseHTTPRequestHandler
import json
import requests
from urllib.parse import urlparse, parse_qs
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # ambil IP dari query parameter jika ada
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        user_ip = query_params.get('ip', [None])[0] or self.headers.get('X-Forwarded-For', self.client_address[0])
        search_ip = query_params.get('search_ip', [None])[0]

        # simpan informasi IP pengguna ke file
        self.save_user_ip(user_ip)
        
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

            # simpan IP pencarian jika ada
            if search_ip:
                self.save_search_ip(search_ip)
        else:
            result = {"error": "could not retrieve location information"}

        # mengirimkan respons JSON ke pengguna
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def save_user_ip(self, user_ip):
        # simpan IP pengguna ke file JSON
        data_file = 'data/userip.json'
        self.save_to_file(data_file, {"UserIP": user_ip})

    def save_search_ip(self, search_ip):
        # simpan IP pencarian ke file JSON
        data_file = 'data/searchip.json'
        self.save_to_file(data_file, {"SearchIP": search_ip})

    def save_to_file(self, filepath, data):
        # pastikan direktori data ada
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # baca file yang sudah ada jika ada
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                try:
                    current_data = json.load(f)
                except json.JSONDecodeError:
                    current_data = []  # jika file kosong
        else:
            current_data = []

        # tambahkan data baru ke current_data
        current_data.append(data)

        # simpan kembali ke file
        with open(filepath, 'w') as f:
            json.dump(current_data, f, indent=4)

# untuk Vercel, kita tidak perlu menjalankan server HTTP
# kita cukup mendefinisikan handler dan biarkan Vercel yang mengurusnya
handler_instance = handler()
