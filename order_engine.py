from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os, uuid, time

class OrderHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        data = json.dumps({"status": "ONLINE", "pid": os.getpid()}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode() or "{}")
        tx_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        data = json.dumps({
            "ok": True,
            "tx_id": tx_id,
            "client": body.get("client", "Apex Global Corp"),
            "amount": body.get("amount", 1200),
            "pid": os.getpid(),
            "ts": time.strftime("%H:%M:%S")
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

class FastHTTPServer(HTTPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    FastHTTPServer(("127.0.0.1", 8080), OrderHandler).serve_forever()