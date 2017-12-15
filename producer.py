import argparse
import re
import SocketServer

class Server(object):
    """Toy streaming server. Produces a stream UDP packets to registered consumers.

    To register a consumer, send a PUT request to the producer. The HTTP request's client IP
    address is then registered. The payload must contain a number which the port that the
    consumer will be listening on. The DELETE verb deletes the registartion.

    In the commandline example below, nc is used to register a consumer listening at port
    6714 and then deregisters itself.

    $ nc SERVER PORT
    PUT / HTTP/1.1
    6714

    $ nc SERVER PORT
    DELETE / HTTP/1.1
    6714
    """

    @staticmethod
    def parse_args():
        """Parses Server args from the arg string."""
        parser = argparse.ArgumentParser(description='Parse Server args.')
        parser.add_argument('-p', '--port', type=int, default=8080,
                            help='Set the port to listen for UDP packets')
        return parser.parse_args()

    class RegistrationHandler(BaseHTTPRequestHandler):
        """A handler for registering new consumers.

        New consumers of the streaming server should PUT. To deregister, existing consumers
        should DELETE. The only vaild resource path is /. The payload must contain a port number
        of the consumer.

        The class has static state. Python's standard HTTP server framework does not allow
        access to a handler's instance state.

        Thread-safe. Its static state is protected by a lock.
        """
        lock = threading.Lock()
        # Guarded by lock.
        registered = set()

        def do_PUT(self):
            pass

        def do_DELETE(self):
            pass

    def __init__(self, port):
        """Constructs an HTTP Server listening at the provided port."""
        address = ('localhost', port)
        httpd = BaseHTTPServer.HTTPServer(address, Server.RegistrationHandler)

if __name__ == '__main__':
    args = Server.parse_args()
    server = Server(args.port)
    server.run()
