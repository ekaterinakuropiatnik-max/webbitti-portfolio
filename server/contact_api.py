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
        reply_html = f"""<!doctype html>
<html lang="de"><body style="margin:0;background:#f2f4f6;font-family:Arial,Helvetica,sans-serif;color:#182433">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f2f4f6;padding:28px 12px"><tr><td align="center">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:620px;background:#ffffff;border-radius:18px;overflow:hidden;box-shadow:0 10px 30px rgba(11,13,16,.10)">
  <tr><td style="background:#0b0d10;padding:26px 34px">
    <table role="presentation" cellspacing="0" cellpadding="0"><tr>
      <td><img src="https://webbitti.com/img/webbitti-mark-email.gif" width="72" height="72" alt="Webbitti" style="display:block;border:0;border-radius:16px"></td>
      <td style="padding-left:15px"><div style="color:#c8ff65;font-size:20px;font-weight:700;letter-spacing:.04em">WEBBITTI</div><div style="color:#b9c0c8;font-size:13px;margin-top:4px">Webdesign &amp; digitale Lösungen · Wien</div></td>
    </tr></table>
  </td></tr>
  <tr><td style="padding:38px 34px 12px">
    <div style="display:inline-block;background:#ecffd0;color:#315800;border-radius:99px;padding:7px 12px;font-size:12px;font-weight:700;letter-spacing:.05em">ANFRAGE ERHALTEN</div>
    <h1 style="margin:20px 0 14px;font-size:28px;line-height:1.25;color:#111820">Vielen Dank, {name}.</h1>
    <p style="margin:0 0 16px;font-size:16px;line-height:1.65;color:#4b5866">Ihre Nachricht ist sicher bei Webbitti angekommen. Ich sehe mir Ihr Vorhaben persönlich an und melde mich in der Regel innerhalb von 24 Stunden.</p>
    <div style="margin:24px 0;background:#f5f7f8;border-left:4px solid #c8ff65;border-radius:8px;padding:16px 18px;color:#273442;font-size:15px"><strong>Ihre Anfrage:</strong><br>{package}</div>
    <p style="margin:0 0 18px;font-size:15px;line-height:1.55;color:#4b5866">Möchten Sie vorab noch etwas ergänzen? Schreiben Sie mir direkt per WhatsApp.</p>
    <table role="presentation" cellspacing="0" cellpadding="0"><tr><td style="border-radius:9px;background:#1f7a45">
      <a href="https://wa.me/4367764757974?text=Hallo%20Kateryna%2C%20ich%20habe%20gerade%20eine%20Anfrage%20über%20Webbitti%20gesendet." style="display:inline-block;padding:15px 23px;color:#ffffff;text-decoration:none;font-size:16px;font-weight:700">Jetzt per WhatsApp schreiben →</a>
    </td></tr></table>
  </td></tr>
  <tr><td style="padding:24px 34px 38px"><p style="margin:0;font-size:15px;line-height:1.6;color:#4b5866">Freundliche Grüße<br><strong style="color:#182433">Kateryna Kuropiatnyk</strong><br>Webbitti · Wien</p></td></tr>
  <tr><td style="border-top:1px solid #e2e6e9;padding:22px 34px;text-align:center">
    <a href="https://webbitti.com/" style="display:inline-block;border:1px solid #1a3548;border-radius:8px;padding:11px 18px;color:#1a3548;text-decoration:none;font-size:14px;font-weight:700">Webbitti Website ansehen</a>
    <p style="margin:14px 0 0;color:#83909b;font-size:12px">webbitti.com · Wien, Österreich</p>
  </td></tr>
</table>
</td></tr></table>
</body></html>"""
        reply_text = f"Hallo {name},\n\nvielen Dank für Ihre Anfrage bei Webbitti. Ihre Nachricht ist sicher angekommen. Ich melde mich in der Regel innerhalb von 24 Stunden.\n\nIhre Anfrage: {package}\n\nWhatsApp: https://wa.me/4367764757974\nWebsite: https://webbitti.com/\n\nFreundliche Grüße\nKateryna Kuropiatnyk\nWebbitti · Wien"
        try:
            send_email({"sender":{"name":SENDER_NAME,"email":SENDER_EMAIL},"to":[{"email":OWNER_EMAIL}],"replyTo":{"email":email,"name":name},"subject":f"Neue Webbitti-Anfrage: {package}","htmlContent":owner_html})
            send_email({"sender":{"name":SENDER_NAME,"email":SENDER_EMAIL},"to":[{"email":email,"name":name}],"replyTo":{"email":OWNER_EMAIL,"name":"Kateryna Kuropiatnyk"},"subject":"Ihre Anfrage ist bei Webbitti angekommen","htmlContent":reply_html,"textContent":reply_text})
        except (urllib.error.URLError, RuntimeError, TimeoutError) as error:
            print(f"contact-api provider_error={type(error).__name__}", flush=True)
            return self.reply(502, {"ok":False,"message":"Die Nachricht konnte gerade nicht gesendet werden. Bitte nutzen Sie E-Mail oder WhatsApp."})
        recent.append(now); self.reply(200, {"ok":True,"message":"Vielen Dank! Ihre Anfrage ist angekommen. Sie erhalten gleich eine Bestätigung per E-Mail."})

if __name__ == "__main__": ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
