import argparse
import socket

class Client(object):
    """Toy UDP client."""

    @staticmethod
    def parse_args():
        """Parses Client args from the arg string."""
        parser = argparse.ArgumentParser(description='Parse Client args.')
        parser.add_argument('-p', '--port', type=int, default=8080,
                            help='Set the port to talk to')
        parser.add_argument('-m', '--message', type=str,
                            help='Message to send')
        return parser.parse_args()

    def __init__(self, port):
        # TODO: make configurable
        self.host = 'localhost'
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message):
        self.sock.sendto(message + '\n', (self.host, self.port))
        print self.sock.recv(1024)

if __name__ == '__main__':
    args = Client.parse_args()

    client = Client(args.port)
    client.send(args.message)
