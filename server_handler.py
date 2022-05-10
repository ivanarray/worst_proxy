import re
import socket
import socketserver

from connection_type import ConnectionType


class HttpProxyHandler(socketserver.BaseRequestHandler):
    CONNECTION_REPLY = "HTTP/1.1 200 Connection established\r\n\r\n".encode()
    LINK_REG = re.compile(r'(?<=Host: )(?P<name>[^\n:\r ]+)(:(?P<port>\d+))?')
    PACKET_SIZE = 65534
    TIMEOUT = 2

    def handle(self) -> None:
        try:
            print(f"connect to {self.client_address}")
            self.request.settimeout(self.TIMEOUT)
            data: bytes = self.request.recv(self.PACKET_SIZE)
            d_data = data.decode()
            connect_type = self.get_connection_type(d_data)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.TIMEOUT)
                addr = self.parse_address(d_data)
                name = addr['name']
                port = addr['port']
                if port is None:
                    port = 80 if connect_type is connect_type.HTTP else 443
                sock.connect((name, int(port)))
                if connect_type is connect_type.HTTP:
                    self.handle_http(sock, data)
                else:
                    self.handle_https(sock, data)
        except Exception as e:
            print(e)

    def finish(self) -> None:
        self.request.close()

    def handle_https(self, remote_server: socket.socket, data: bytes):
        self.request.sendall(self.CONNECTION_REPLY)
        while True:
            try:
                try:
                    data = self.request.recv(self.PACKET_SIZE)
                    remote_server.sendall(data)
                except socket.error:
                    pass
                try:
                    rec = remote_server.recv(self.PACKET_SIZE)
                    self.request.sendall(rec)
                    if len(rec) < 1 or len(data) < 1:
                        break
                except socket.error:
                    pass
            except Exception as e:
                print(e)
                break

    def handle_http(self, remote_server: socket.socket, data: bytes):
        remote_server.sendall(data)
        while True:
            try:
                try:
                    rec = remote_server.recv(self.PACKET_SIZE)
                    self.request.sendall(rec)
                    if len(rec) < 1:
                        break
                except socket.timeout:
                    pass
                try:
                    data = self.request.recv(self.PACKET_SIZE)
                    remote_server.sendall(data)
                    if len(data) < 1:
                        break
                except socket.timeout:
                    pass
            except Exception as e:
                print(e)
                break

    def parse_address(self, page: str) -> dict:
        return self.LINK_REG.search(page).groupdict()

    @staticmethod
    def get_connection_type(data: str) -> ConnectionType:
        return ConnectionType.HTTPS if "CONNECT" in data else ConnectionType.HTTP
