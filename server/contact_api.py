#!/usr/bin/env python3
import html, json, os, re, time, urllib.error, urllib.request
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST, PORT = "127.0.0.1", int(os.environ.get("CONTACT_API_PORT", "8787"))
BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
OWNER_EMAIL = os.environ.get("CONTACT_OWNER_EMAIL", "kuropiatnyk.design@gmail.com")
SENDER_EMAIL = os.environ.get("CONTACT_SENDER_EMAIL", "anfrage@webbitti.com")
SENDER_NAME = os.environ.get("CONTACT_SENDER_NAME", "Webbitti")
ALLOWED_ORIGINS = {"https://webdesign.webbitti.com", "https://webbitti.com"}
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
requests_by_ip = defaultdict(deque)

def send_email(payload):
    request = urllib.request.Request("https://api.brevo.com/v3/smtp/email", data=json.dumps(payload).encode(), headers={"api-key": BREVO_API_KEY, "content-type": "application/json", "accept": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=12) as response:
        if response.status not in (200, 201, 202): raise RuntimeError(f"provider status {response.status}")

def safe(value, limit): return html.escape(str(value or "").strip()[:limit])

class Handler(BaseHTTPRequestHandler):
    server_version = "WebbittiContact/1.0"
    def log_message(self, fmt, *args): print(f"contact-api {self.command} {self.path} {args[1] if len(args)>1 else '-'}", flush=True)
    def reply(self, status, payload):
        data = json.dumps(payload).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(data))); self.send_header("Cache-Control", "no-store"); self.send_header("X-Content-Type-Options", "nosniff"); self.end_headers(); self.wfile.write(data)
    def do_GET(self): self.reply(200, {"ok": True, "mailConfigured": bool(BREVO_API_KEY)}) if self.path == "/health" else self.reply(404, {"ok": False})
    def do_POST(self):
        if self.path != "/contact": return self.reply(404, {"ok": False})
        if self.headers.get("Origin", "") not in ALLOWED_ORIGINS: return self.reply(403, {"ok": False, "message": "Ungültige Anfrage."})
        if not BREVO_API_KEY: return self.reply(503, {"ok": False, "message": "Der Versand wird gerade eingerichtet. Bitte schreiben Sie per E-Mail oder WhatsApp."})
        try: length = int(self.headers.get("Content-Length", "0"))
        except ValueError: length = 0
        if length <= 0 or length > 20000: return self.reply(413, {"ok": False, "message": "Die Anfrage ist zu groß."})
        ip, now = self.headers.get("X-Real-IP", self.client_address[0]), time.time()
        recent = requests_by_ip[ip]
        while recent and recent[0] < now - 3600: recent.popleft()
        if len(recent) >= 5: return self.reply(429, {"ok": False, "message": "Zu viele Anfragen. Bitte versuchen Sie es später erneut."})
        try: data = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError): return self.reply(400, {"ok": False, "message": "Bitte prüfen Sie Ihre Angaben."})
        if str(data.get("website", "")).strip(): return self.reply(200, {"ok": True})
        try: elapsed = now * 1000 - float(data.get("startedAt", 0))
        except (TypeError, ValueError): elapsed = 0
        if elapsed < 2500 or elapsed > 86400000: return self.reply(400, {"ok": False, "message": "Bitte laden Sie die Seite neu und versuchen Sie es noch einmal."})
        name, email = safe(data.get("name"), 100), safe(data.get("email"), 180)
        company, package, message = safe(data.get("company"), 180) or "—", safe(data.get("package"), 120) or "Individuelle Anfrage", safe(data.get("message"), 4000)
        if len(name) < 2 or not EMAIL_RE.match(email) or len(message) < 10: return self.reply(400, {"ok": False, "message": "Bitte füllen Sie Name, E-Mail und Vorhaben vollständig aus."})
        owner_html = f"<h2>Neue Anfrage über Webbitti</h2><p><b>Name:</b> {name}<br><b>E-Mail:</b> {email}<br><b>Unternehmen:</b> {company}<br><b>Interesse:</b> {package}</p><h3>Vorhaben</h3><p>{message.replace(chr(10), '<br>')}</p>"
        reply_html = f"<p>Hallo {name},</p><p>vielen Dank für Ihre Anfrage bei Webbitti. Ihre Nachricht ist sicher angekommen.</p><p>Ich sehe mir Ihr Vorhaben persönlich an und melde mich in der Regel innerhalb von 24 Stunden bei Ihnen.</p><p><b>Ihre Anfrage:</b> {package}</p><p>Freundliche Grüße<br>Kateryna Kuropiatnyk<br>Webbitti · Wien</p>"
        try:
            send_email({"sender":{"name":SENDER_NAME,"email":SENDER_EMAIL},"to":[{"email":OWNER_EMAIL}],"replyTo":{"email":email,"name":name},"subject":f"Neue Webbitti-Anfrage: {package}","htmlContent":owner_html})
            send_email({"sender":{"name":SENDER_NAME,"email":SENDER_EMAIL},"to":[{"email":email,"name":name}],"replyTo":{"email":OWNER_EMAIL,"name":"Kateryna Kuropiatnyk"},"subject":"Ihre Anfrage ist bei Webbitti angekommen","htmlContent":reply_html})
        except (urllib.error.URLError, RuntimeError, TimeoutError) as error:
            print(f"contact-api provider_error={type(error).__name__}", flush=True)
            return self.reply(502, {"ok":False,"message":"Die Nachricht konnte gerade nicht gesendet werden. Bitte nutzen Sie E-Mail oder WhatsApp."})
        recent.append(now); self.reply(200, {"ok":True,"message":"Vielen Dank! Ihre Anfrage ist angekommen. Sie erhalten gleich eine Bestätigung per E-Mail."})

if __name__ == "__main__": ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
