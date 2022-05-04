import socket
import time
import ssl
import threading
import typing

def do(server:socket.socket):
    while True:
        browser, addr = server.accept()
        browser.settimeout(5)
        recieved_from_browser = browser.recv(1024)
        print(recieved_from_browser)
        if not recieved_from_browser:
            continue
        headers = recieved_from_browser.decode()
        if "CONNECT" in headers:
            client = socket.socket()
            # Connect to port 443
            try:
                # If successful, send 200 code response
                print(headers)
                print(headers.split()[1].split("/")[0].split(":")[0])
                client.connect((headers.split()[1].split("/")[0].split(":")[0], 443))
                reply = "HTTP/1.1 200 Connection established\r\n"
                reply += "Proxy-agent: Pyx\r\n"
                reply += "\r\n"
                browser.sendall(reply.encode())
            except socket.error as err:
                # If the connection could not be established, exit
                # Should properly handle the exit with http error code here
                print(err)
                break

            # Indiscriminately forward bytes
            browser.setblocking(False)
            client.setblocking(False)
            print("go in wt")
            while True:
                try:
                    request = browser.recv(1024)
                    client.sendall(request)
                except Exception as err:
                    pass
                try:
                    reply = client.recv(1024)
                    browser.sendall(reply)
                except Exception as err:
                    pass
        else:
            client = socket.socket()
            dec_req = recieved_from_browser.decode().split()[1]
            host, port = dec_req.split('/')[2], 80
            client.connect((host, port))
            while True:
                client.sendall(recieved_from_browser)
                rec = client.recv(1024)
                browser.send(rec)


server = socket.socket()
server.bind(('localhost', 8080))
server.listen(100)
while True:
    thread=threading.Thread(target=do, args=(server,))
    thread.start()
