import server
from argparse import ArgumentParser

packet_size = 65534
timeout = 0.5

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-ho", dest="host", default='localhost',
                        help='Адрес, где будет хоститься прокси',
                        required=False)

    parser.add_argument("-p", dest="port", default=8081,
                        help='Порт, к которому будет производиться подключение',
                        required=False)
    args = parser.parse_args()
    server.HttpProxyServer(args.port, args.host, timeout).run()
