import socket


class HttpsProxy:
    @staticmethod
    def proxy(client, request, browser, timeout, packet_size):
        client.connect((HttpsProxy.get_addr_https(request), 443))
        reply = "HTTP/1.1 200 Connection established\r\n\r\n"
        browser.sendall(reply.encode())

        browser.setblocking(True)
        browser.settimeout(timeout)
        client.setblocking(True)
        client.settimeout(timeout)
        while True:
            try:
                browser_request = browser.recv(packet_size)
                client.sendall(browser_request)
            except socket.error:
                pass
            try:
                reply = client.recv(packet_size)
                browser.sendall(reply)
            except socket.error:
                pass

    @staticmethod
    def get_addr_https(request):
        return request.decode().split()[1].split("/")[0].split(":")[0]