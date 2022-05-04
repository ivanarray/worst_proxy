import socket  # кто понял что происходит в програме тово диференцырут
import threading
import typing

packet_size = 6400
timeout = 1


def get_addr_http(request):
    return request.decode().split()[1].split('/')[2]


def get_addr_https(request):
    return request.decode().split()[1].split("/")[0].split(":")[0]


def https(client, request, browser):
    try:
        client.connect((get_addr_https(request), 443))
        reply = "HTTP/1.1 200 Connection established\r\n"
        reply += "Proxy-agent: Dota 2\r\n"
        reply += "\r\n"
        browser.sendall(reply.encode())
    except socket.error as err:
        pass

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


def http(client, request, browser):
    client.settimeout(timeout)
    host, port = get_addr_http(request), 80
    client.connect((host, port))
    while True:
        client.sendall(request)
        rec = client.recv(packet_size)
        browser.send(rec)


def do(upper_socket: socket.socket):
    while True:
        browser, addr = upper_socket.accept()
        browser.settimeout(timeout)
        try:
            request = browser.recv(packet_size)
        except socket.timeout:
            continue
            pass
        if not request:
            continue
        client = socket.socket()
        try:
            if "CONNECT" in request.decode():
                https(client, request, browser)
            else:
                http(client, request, browser)
        except UnicodeDecodeError:
            pass


server = socket.socket()
server.bind(('localhost', 8081))
server.listen(100)
while True:
    thread = threading.Thread(target=do, args=(server,))
    thread.start()
