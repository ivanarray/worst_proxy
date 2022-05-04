import socket #кто понял что происходит в програме тово диференцырут
import threading
import typing

packet_size = 6400
timeout = 1


def https(headers, browser):
    client = socket.socket()
    try:
        client.connect((headers.split()[1].split("/")[0].split(":")[0], 443))
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
            request = browser.recv(packet_size)
            client.sendall(request)
        except Exception as err:
            pass
        try:
            reply = client.recv(packet_size)
            browser.sendall(reply)
        except Exception as err:
            pass

def http(recieved_from_browser, browser):
    client = socket.socket()
    client.settimeout(timeout)
    dec_req = recieved_from_browser.decode().split()[1]
    host, port = dec_req.split('/')[2], 80
    client.connect((host, port))
    while True:
        client.sendall(recieved_from_browser)
        rec = client.recv(packet_size)
        browser.send(rec)

def do(upper_socket : socket.socket):
    while True:
        browser, addr = upper_socket.accept()
        browser.settimeout(timeout)
        recieved_from_browser = browser.recv(packet_size)
        if not recieved_from_browser:
            continue
        headers = recieved_from_browser.decode()
        if "CONNECT" in headers:
            https(headers, browser)
        else:
            http(recieved_from_browser, browser)


server = socket.socket()
server.bind(('localhost', 8081))
server.listen(100)
while True:
    thread = threading.Thread(target=do, args=(server,))
    thread.start()
