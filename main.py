import json
import logging
import mimetypes
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = Path(__file__).resolve().parent

class FrameWork(BaseHTTPRequestHandler):
    
    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case '/':
                self.send_html_file('index.html')
            case '/contact':
                self.send_html_file('message.html')
            case _:
                file = BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html_file('error.html', status=404)

    def do_POST(self):
        size = self.headers.get('Content-Length')
        data = self.rfile.read(int(size))
        print(data)
        parse_data = urllib.parse.unquote_plus(data.decode())
        print(parse_data)
        try:
            parse_dict = {key : value for key, value in [el.split('=') for el in parse_data.split('&')]}
            print(parse_dict)
            with open ('storage/data.json', 'w', encoding='utf-8') as file:
                json.dump(parse_dict, file, ensure_ascii=False, indent=4)
        except ValueError as err:
            logging.error(err)
        except OSError as err:
            logging.error(err)

        self.send_response(302)
        self.send_header('Location', '/contact')
        self.end_headers()

    def send_static(self, filename, status=200):
        self.send_response(status)
        mt, _ = mimetypes.guess_type(filename)
        if mt:
            self.send_header("Content-type", mt)
        else:
            self.send_header("Content-type", 'application/octet-stream')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def send_html_file(self, filename, status=200):
        file_path = BASE_DIR.joinpath(filename)
        if file_path.exists():
            self.send_response(status)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(file_path, 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'File not found')


def run_server():
    server_address = ('localhost', 8000)
    http_server = HTTPServer(server_address, FrameWork)
    print(f"Server running at http://{server_address[0]}:{server_address[1]}")
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
        print("Server stopped")


if __name__ == '__main__':
    run_server()
