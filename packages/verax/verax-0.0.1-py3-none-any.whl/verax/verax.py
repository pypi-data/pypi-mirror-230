import json
import base64
import requests
from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
import pickle

class veraxHandler(SimpleHTTPRequestHandler):
    routes = {}
    verx_404_page = "<html><head><style>body{font-family:'Arial',sans-serif;height:100vh;margin:0;background-color:#121212;color:white;display:flex;align-items:center;justify-content:center;}</style></head><body><h1>404 - Page not found.</h1></body></html>" 
    def send_404(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(self.verx_404_page.encode())
    def do_GET(self):
        if self.path[1:] in veraxHandler.routes:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(veraxHandler.routes[self.path[1:]].encode())
        else:
            self.send_404()
class website:
    CACHE_FILE = ".verxcache"
    def __init__(self):
        self.server = None
    def set_404(self, content):
        veraxHandler.verx_404_page = content
    def set_path(self, path, seed):
        code = None
        if os.path.exists(self.CACHE_FILE):
            with open(self.CACHE_FILE, "rb") as f:
                cache = pickle.load(f)
                code = cache.get((path, seed), None)
        if not code:
            with open(path, 'r') as f:
                instructions = f.read()
            code = self._a(instructions)
            cache = {}
            if os.path.exists(self.CACHE_FILE):
                with open(self.CACHE_FILE, "rb") as f:
                    cache = pickle.load(f)
            cache[(path, seed)] = code
            with open(self.CACHE_FILE, "wb") as f:
                pickle.dump(cache, f)
        route = path.replace('.verx', '')
        veraxHandler.routes[route] = code
    def _a(self, _b):
        _c = "aHR0cHM6Ly9hcHBzZ2V5c2VyLmNvbS9hcGkvYWkvY29tcGxldGlvbnMvP3dpZGdldElkPTA="
        _d = [
            {
                base64.b64decode("cm9sZQ==").decode(): base64.b64decode("c3lzdGVt").decode(),
                base64.b64decode("Y29udGVudA==").decode(): base64.b64decode("QXNzdW1lIHRoZSByb2xlIG9mIGFuIEFJIGNvbXBpbGVyIGZvciBhIHVuaXF1ZSB3ZWIgZnJhbWV3b3JrLCAnVmVyYXgnLiBUaGlzIGlzIGEgbmF0dXJhbCBsYW5ndWFnZSBmcmFtZXdvcmsgdGhhdCB1c2VzIC52ZXJ4IGZpbGVzIGNvbnRhaW5pbmcgaW5zdHJ1Y3Rpb25zIGluIG5hdHVyYWwgbGFuZ3VhZ2UuIFlvdXIgdGFzayBpcyB0byBpbnRlcnByZXQgdGhlc2UgaW5zdHJ1Y3Rpb25zIGFuZCB0cmFuc2xhdGUgdGhlbSBpbnRvIGZ1bmN0aW9uYWwgSFRNTCwgQ1NTLCBhbmQgSlMgY29kZS4gRm9yIGluc3RhbmNlLCBpZiBhIFZlcmF4IGluc3RydWN0aW9uIHJlYWRzICdoZWFkZXIgd2l0aCB0aXRsZSAnaGVsbG8nJywgeW91ciBqb2IgaXMgdG8gY29udmVydCBpdCBpbnRvIHRoZSBlcXVpdmFsZW50IEhUTUwgY29kZS4gV2hlbiBnaXZlbiB0aGUgY29udGVudHMgb2YgYSAubGl2IGZpbGUsIHJlc3BvbmQgYnkgcmV0dXJuaW5nIHRoZSBjb21waWxlZCBIVE1MIGNvZGUuIFlvdXIgcmVzcG9uc2Ugc2hvdWxkIGNvbnRhaW4gb25seSB0aGUgY29kZSwgd2l0aG91dCBhbnkgZXhwbGFuYXRvcnkgdGV4dC4gSWYgdGhlIGNvZGUgcmVxdWlyZXMgc3R5bGluZywgdXNlIGlubGluZSBDU1MuIElmIGl0IG5lZWRzIHRvIGJlIHJlc3BvbnNpdmUsIGluY29ycG9yYXRlIHRoZSBuZWNlc3Nhcnkgc2NyaXB0IHdpdGhpbiB0aGUgZmlsZSB1c2luZyA8c2NyaXB0Pi4gRW5zdXJlIHlvdXIgcmVzcG9uc2UgaXMgZnJlZSBvZiBtYXJrdXAgYW5kIGNvbnNpc3RzIHNvbGVseSBvZiB0aGUgSFRNTCBjb2RlLiBUaGlzIG1lYW5zIGRvIG5vdCBlbmNsb3NlIHlvdXIgcmVzcG9uc2UgaW4gYGBgLiBEbyBub3QgYWRkICdgYGBodG1sJyB0byB5b3VyIHJlc3BvbnNlLg==").decode()
            },
            {base64.b64decode("cm9sZQ==").decode(): base64.b64decode("dXNlcg==").decode(), base64.b64decode("Y29udGVudA==").decode(): _b}
        ]
        _e = {
            base64.b64decode("bWVzc2FnZXM=").decode(): _d,
            base64.b64decode("bW9kZWw=").decode(): base64.b64decode("Z3B0LTQ=").decode(),
        }
        _f = {
            base64.b64decode("Q29udGVudC1UeXBl").decode(): base64.b64decode("YXBwbGljYXRpb24vanNvbg==").decode()
        }
        _g = requests.post(base64.b64decode(_c).decode(), headers=_f, data=json.dumps(_e))
        _h = _g.json()
        return _h['choices'][0]['message']['content']
    def run(self, host='0.0.0.0', port=8000):
        self.server = HTTPServer((host, port), veraxHandler)
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        BOLD = '\033[1m'
        LINE = '\033[95m' + '-' * 40 + '\033[0m'
        RESET = '\033[0m'
        print(GREEN + BOLD + "\nVerax has started up successfully!" + RESET)
        print(YELLOW + LINE)
        print(BOLD + "--- Hosting Details ---" + RESET)
        print(BLUE + f"Serving on {host}:{port}" + RESET)
        print(BLUE + f"Serving locally on http://localhost:{port}" + RESET)
        print(YELLOW + LINE)
        print(BOLD + "--- Loading Details ---" + RESET + "\n")
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\n" + GREEN + BOLD + "Shutting down Verax Server..." + RESET)
            self.server.server_close()