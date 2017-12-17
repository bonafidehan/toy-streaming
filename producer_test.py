import httplib
import SocketServer
import threading
import unittest

import producer

class ProducerTests(unittest.TestCase):
    server_port = 8080
    consumer_port_1 = '6714'
    consumer_port_2 = '8128'

    @classmethod
    def setUpClass(cls):
        # Enable address reuse between tests.
        SocketServer.TCPServer.allow_reuse_address = True

    def setUp(self):
        self.server = producer.Server(ProducerTests.server_port)
        self.server_thread = threading.Thread(target=self.server.run)
        self.server_thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server_thread.join()

    def build_conn(self, verb, path, body):
        conn = httplib.HTTPConnection('localhost', ProducerTests.server_port)
        conn.request(verb, path, body)
        return conn

    def test_invalid_get(self):
        conn = self.build_conn('GET', '/', ProducerTests.consumer_port_1)
        res = conn.getresponse()
        self.assertEqual(404, res.status)

    def test_put_get(self):
        conn =self.build_conn('PUT', '/', ProducerTests.consumer_port_1)
        res = conn.getresponse()
        self.assertEqual(200, res.status)

        conn = self.build_conn('GET', '/', ProducerTests.consumer_port_1)
        res = conn.getresponse()
        self.assertEqual(200, res.status)

        conn = self.build_conn('GET', '/', ProducerTests.consumer_port_2)
        res = conn.getresponse()
        self.assertEqual(404, res.status)

if __name__ == '__main__':
    unittest.main()
