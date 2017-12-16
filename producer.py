import argparse
import BaseHTTPServer
import re
import threading

class Server(object):
    """Toy streaming server. Produces a stream of UDP packets for registered consumers.
    The following is the HTTP server interface:

    PUT /
        Register a consumer. The request's client IP address and the provided port are used to
        register that consumer.

    GET /
        Check registration status. The request's client IP address and the provided port are used
        to check the status of the consumer. If the reply's status code is 200, the consumer is
        registered. If the reply's status code is 404, no such consumer is registered.

    DELETE /
        Deregister a consumer. The request's client IP address and the provided port are used to
        deregister that consumer.

    In the commandline examples below, nc is used to register a consumer listening at port
    6714 and then deregister it.

    Register a consumer:

        $ nc SERVER PORT
        PUT / HTTP/1.1
        Content-Length: 4

        6714

        HTTP/1.1 200 OK

    Check the consumer exists:

        $ nc SERVER PORT
        GET / HTTP/1.1
        Content-Length: 4

        6714

        HTTP/1.1 200 OK

    Deregister the consumer:

        $ nc SERVER PORT
        DELETE / HTTP/1.1
        Content-Length: 4

        6714

        HTTP/1.1 200 OK

    Check the consumer doesn't exist:

        $ nc SERVER PORT
        GET / HTTP/1.1
        Content-Length: 4

        6714

        HTTP/1.1 404 Not Found
    """

    @staticmethod
    def parse_args():
        """Parses Server args from the arg string."""
        parser = argparse.ArgumentParser(description='Parse Server args.')
        parser.add_argument('-p', '--port', type=int, default=8080,
                            help='Set the port to listen for UDP packets')
        return parser.parse_args()

    class RegistrationHandler(BaseHTTPServer.BaseHTTPRequestHandler):
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

        # Changes the error message format. Breaks encapsulation. Not pretty but this is the
        # way that BaseHTTPRequestHandler works.
        error_message_format = '%(code)d %(explain)s: %(message)s\n'
        error_content_type = 'text/plain'

        def set_headers(self):
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()

        def get_port(self):
            """Get the port from the body. Return a tuple (bool, port) where the first
            part of the tuple indicates whether a port was found.
            """
            content_length = int(self.headers.getheader('Content-Length', 0))
            port_string = self.rfile.read(content_length)
            if port_string.isdigit():
                return (True, int(port_string))
            return (False, -1)

        def path_supported(self):
            """Returns whether the path is supported.

            Only / is supported. Mapping paths to handlers is manual in this framework and not
            necessary for a toy server.
            """
            if self.path.strip() == '/':
                return True
            return False

        def do_PUT(self):
            self.set_headers()

            if not self.path_supported():
                self.send_error(404, 'Path {} not supported'.format(self.path))
                return

            (port_provided, port) = self.get_port()
            if not port_provided:
                self.send_error(400, 'Port not provided in body')
                return

            consumer = (self.client_address[0], port)
            with self.lock:
                if consumer in self.registered:
                    self.send_error(400, 'Consumer {} already exists'.format(consumer))
                    return
                self.registered.add(consumer)
                self.send_response(200)

        def do_GET(self):
            self.set_headers()

            if not self.path_supported():
                self.send_error(404, 'Path {} not supported'.format(self.path))
                return

            (port_provided, port) = self.get_port()
            if not port_provided:
                self.send_error(400, 'Port not provided in body')
                return

            consumer = (self.client_address[0], port)
            with self.lock:
                if consumer in self.registered:
                    self.send_response(200)
                else:
                    self.send_error(404, 'Consumer {} not registered'.format(consumer))

    def __init__(self, port):
        """Constructs an HTTP Server listening at the provided port."""
        address = ('localhost', port)
        self.httpd = BaseHTTPServer.HTTPServer(address, Server.RegistrationHandler)

    def run(self):
        """Run the server forever."""
        self.httpd.serve_forever()

if __name__ == '__main__':
    args = Server.parse_args()
    server = Server(args.port)
    server.run()