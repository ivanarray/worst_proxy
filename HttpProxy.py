import socket


class HttpProxy:
    @staticmethod
    def proxy(client, request, browser, timeout, packet_size):
        client.settimeout(timeout)
        client.connect((HttpProxy.get_addr_http(request), 80))
        while True:
            try:
                client.sendall(request)
            except socket.error:
                continue
                pass

            try:
                rec = client.recv(packet_size)
                browser.send(rec)
            except socket.error:
                pass

    @staticmethod
    def get_addr_http(request):
        return request.decode().split()[1].split('/')[2]
