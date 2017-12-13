import argparse
import SocketServer

class Server(object):
    """Toy UDP server that echoes."""

    @staticmethod
    def parse_args():
        """Parses Server args from the arg string."""
        parser = argparse.ArgumentParser(description='Parse Server args.')
        parser.add_argument('-p', '--port', type=int, default=8080,
                            help='Set the port to listen for UDP packets')
        return parser.parse_args()

    class UDPHandler(SocketServer.BaseRequestHandler):
        """A toy handler that echoes."""
        def handle(self):
            received = self.request[0].strip()
            socket = self.request[1]
            socket.sendto('Ack: {}'.format(received), self.client_address)

    def __init__(self, port):
        """Constructs a UDP Server listening at the provided port."""
        self.udp_server = SocketServer.UDPServer(('localhost', port), Server.UDPHandler)
        self.udp_server.serve_forever()

if __name__ == '__main__':
    args = Server.parse_args()
    server = Server(args.port)
    server.run()
