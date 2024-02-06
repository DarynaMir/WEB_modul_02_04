import json
import logging
import mimetypes
import socket
import urllib.parse
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = Path(__file__).resolve().parent
BUFFER_SIZE = 1024
HTTP_PORT = 8000  # Corrected port number
HTTP_HOST = '0.0.0.0'
SOCKET_HOST = '127.0.0.1'
SOCKET_PORT = 4000

jinja = Environment(loader=FileSystemLoader('templates'))  # Fixed loader argument


class FrameWork(BaseHTTPRequestHandler):

    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        match route.path:  # Added 'match' keyword
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

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SOCKET_HOST, SOCKET_PORT))
        client_socket.close()
        self.send_response(302)
        self.send_header('Location', '/contact')
        self.end_headers()

        save_data_from_form(data)

    def send_html_file(self, filename, status_code=200):  # Corrected method name
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

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


def save_data_from_form(data):
    parse_data = urllib.parse.unquote_plus(data.decode())
    try:
        parse_dict = {key: value for key, value in [el.split('=') for el in parse_data.split('&')]}

        with open('storage/data.json', 'w', encoding='utf-8') as file:
            json.dump(parse_dict, file, ensure_ascii=False, indent=4)
    except ValueError as err:
        logging.error(err)
    except OSError as err:
        logging.error(err)


def run_socket_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    logging.info('Starting socket server')
    try:
        while True:
            msg, address = server_socket.recvfrom(BUFFER_SIZE)
            logging.info(f'Socket received {address}: {msg}')
            save_data_from_form(msg)
    except KeyboardInterrupt:
        pass
    finally:
        server_socket.close()


def run_http_server(host, port):
    server_address = (host, port)
    http_server = HTTPServer(server_address, FrameWork)
    logging.info('Starting HTTP server')
    try:
        http_server.serve_forever()  # Changed to serve_forever
    except KeyboardInterrupt:
        http_server.server_close()
        logging.info("HTTP Server stopped")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

    server = Thread(target=run_http_server, args=(HTTP_HOST, HTTP_PORT))
    server.start()
    server_socket = Thread(target=run_socket_server, args=(SOCKET_HOST, SOCKET_PORT))
    server_socket.start()
