import http.server
import socketserver

PORT = 8080
handler = http.server.SimpleHTTPRequestHandler

# 使用IPv4地址
def run_server():
    with socketserver.TCPServer(("0.0.0.0", PORT), handler) as httpd:
        print(f"Serving HTTP on 0.0.0.0 port {PORT} (http://localhost:{PORT}/) ...")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()