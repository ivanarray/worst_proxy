import socket
import threading
from HttpProxy import HttpProxy
from HttpsProxy import HttpsProxy

packet_size = 65534
timeout = 0.5

def make_proxy_request(browser):
    while True:
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

                HttpsProxy.proxy(client, request, browser, timeout, packet_size)
            else:
                HttpProxy.proxy(client, request, browser, timeout, packet_size)
        except UnicodeDecodeError:
            pass
        except socket.error:
            pass


server = socket.socket()
server.bind(('localhost', 8081))
server.listen(100)
while True:
    browser, addr = server.accept()
    thread = threading.Thread(target=make_proxy_request, args=(browser,))
    thread.start()
