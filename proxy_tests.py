import socket
import unittest.mock
from threading import Thread

import server


class ProxyShould(unittest.TestCase):
    HTTPS_CONNECT = b'CONNECT www.google.com:443 HTTP/1.1\r\n' \
                    b'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0\r\n' \
                    b'Proxy-Connection: keep-alive\r\nConnection: keep-alive\r\nHost: localhost:443\r\n\r\n'

    HTTPS_REQ = 1

    HTTP_REQ = b'GET http://somkural.ru/ HTTP/1.1\r\n' \
               b'Host: localhost:80\r\n' \
               b'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0\r\n' \
               b'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\n' \
               b'Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3\r\n' \
               b'Accept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\n' \
               b'Cookie: BITRIX_SM_GUEST_ID=8005234; BITRIX_SM_LAST_VISIT=07.05.2022+20%3A07%3A02; BITRIX_SM_LAST_ADV=5\r\n' \
               b'Upgrade-Insecure-Requests: 1\r\n\r\n'

    def setUp(self) -> None:
        self.serv = server.HttpProxyHandler(8081, 'localhost', 0.5)
        Thread(target=self.serv.run).start()
        self.http_server = socket.socket()
        self.https_server = socket.socket()
        self.http_server.bind(('localhost', 80))
        self.https_server.bind(('localhost', 443))
        self.https_server.listen(100)
        self.http_server.listen(1)

    def tearDown(self) -> None:
        self.https_server.close()
        self.http_server.close()

    def test_when_https_should_return_connect_message(self):
        self.https_server.listen(1)
        host = socket.socket()
        host.connect(('localhost', 8081))
        host.send(self.HTTPS_CONNECT)
        ans = host.recv(server.HttpProxyHandler.PACKET_SIZE)
        self.assertTrue("connection established" in ans.decode().lower())

    def test_when_https_should_to_transmitted_messages_after_connect(self):
        host = socket.socket()
        host.connect(('localhost', 8081))
        host.send(self.HTTPS_CONNECT)
        self.https_server.accept()
        ans = host.recv(server.HttpProxyHandler.PACKET_SIZE)
        host.send("12345".encode())
        res = self.https_server.recv(server.HttpProxyHandler.PACKET_SIZE)

        self.assertTrue(res.decode() == "12345")


if __name__ == '__main__':
    unittest.main()
