import socket
import re
import threading

from connection_type import ConnectionType


class HttpProxyServer:
    CONNECTION_REPLY = "HTTP/1.1 200 Connection established\r\n\r\n".encode()
    LINK_REG = re.compile(r'(?<=Host: )(?P<name>[^\n:\r]+)(:(?P<port>\d+))?')
    PACKET_SIZE = 65534

    def __init__(self, port: int, address: str, timeout: float):
        self.listener = socket.socket()
        self.listener.bind((address, port))
        self.is_close = False
        self.timeout = timeout

    def run(self):
        self.listener.listen(100)
        print('Сервер запущен')
        while not self.is_close:
            server, addr = self.listener.accept()
            print(f'{addr} connected to proxy')
            thread = threading.Thread(target=self.make_proxy_request, args=(server,))
            thread.start()

    def make_proxy_request(self, server: socket.socket):
        while True:
            try:
                request = server.recv(self.PACKET_SIZE)
                if not request:
                    continue
                page = request.decode(errors='ignore')
                groups = self.parse_address(page)
                if len(groups) == 0:
                    continue
                name = groups['name']
                port = groups['port']
                if port:
                    port = int(port)
            except socket.timeout:
                continue

            server.settimeout(self.timeout)
            connection_type = self.get_connection_type(page)
            if connection_type is ConnectionType.HTTPS:
                self.handle_https(server, name, port) if port else self.handle_https(server, name)
            else:
                self.handle_http(server, request, name, port) if port else self.handle_http(server, request, name)

    def handle_https(self, host: socket.socket, address: str, port: int = 443):
        server = socket.socket()
        server.connect((address, port))
        print(f'connect to {address}:{port}')
        host.sendall(self.CONNECTION_REPLY)
        server.settimeout(self.timeout)
        while not self.is_close:
            try:
                browser_request = host.recv(self.PACKET_SIZE)
                server.sendall(browser_request)
            except socket.error:
                pass
            try:
                reply = server.recv(self.PACKET_SIZE)
                host.sendall(reply)
            except socket.error:
                pass

    def handle_http(self, host: socket.socket, request: bytes, address: str, port: int = 80):
        server = socket.socket()
        server.connect((address, port))
        print(f'connect to {address}:{port}')
        server.settimeout(self.timeout)
        while True:
            try:
                server.sendall(request)
            except socket.error:
                continue

            try:
                rec = server.recv(self.PACKET_SIZE)
                host.send(rec)
            except socket.error:
                pass

    def parse_address(self, page: str) -> dict:
        return self.LINK_REG.search(page).groupdict()

    @staticmethod
    def get_connection_type(data: str) -> ConnectionType:
        return ConnectionType.HTTPS if "CONNECT" in data else ConnectionType.HTTP
