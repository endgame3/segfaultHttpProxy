import socket
from http.server import BaseHTTPRequestHandler
import http.client
import urllib.parse
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the request URL
        url = urllib.parse.urlparse(self.path)

        # Connect to the remote server
        conn = http.client.HTTPConnection(url.netloc)
        conn.request('GET', url.path)

        # Get the response from the remote server
        self.return_response(conn)

    def do_HEAD(self):
        url = urllib.parse.urlparse(self.path)
        conn = http.client.HTTPConnection(url.netloc)
        conn.request('HEAD', url.path)
        self.return_response(conn)

    def return_response(self, conn):
        response = conn.getresponse()

        # Send the response headers to the client
        self.send_response(response.status)
        for header in response.getheaders():
            self.send_header(header[0], header[1])
        self.end_headers()

        # Send the response body to the client
        self.wfile.write(response.read())
        conn.close()

    def do_POST(self):
        # try:
        url = urllib.parse.urlparse(self.path)
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        conn = http.client.HTTPConnection(url.netloc)
        conn.request('POST', url.path, post_data)
        self.return_response(conn)

    def do_CONNECT(self):
        self.send_response(200, 'Connection Established')
        self.send_header('Proxy-agent', 'Python Proxy')
        self.end_headers()

        try:
            hostname, port = self.path.split(':')
            remote_server = ssl.wrap_socket(
                socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                keyfile=None,
                certfile=None
            )
            remote_server.connect((hostname, int(port)))
            self.connection.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
        except Exception as e:
            self.send_error(502, 'Bad Gateway', str(e))
        self.server.socket = remote_server
        self.handle_one_request()

    #     with urlopen(self.path, data=post_data) as response:
    #         response_body = response.read()
    #         self.send_response(response.status)
    #         for header, value in response.headers.item():
    #             self.send_header(header, value)
    #         self.end_headers()
    #         self.wfile.write(response_body)
    # except HTTPError as e:
    #     self.send_error(e.code, e.reason)
    # except URLError as e:
    #     self.send_error(400, 'Bad Request', str(e.reason))
    # except Exception as e:
    #     self.send_header(header, value)
    #     # self.end_headers()
    #     self.send_error(500, 'Internal Server Error', str(e))


if __name__ == '__main__':
    http.server.test(HandlerClass=ProxyHandler)
