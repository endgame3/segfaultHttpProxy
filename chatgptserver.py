import socket
import threading


class Proxy:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip, self.port))

    def start(self):
        self.server.listen(5)
        print(f"Proxy server listening on {self.ip}:{self.port}...")
        while True:
            client_socket, client_addr = self.server.accept()
            print(f"Accepted connection from {client_addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        request = client_socket.recv(4096)
        method, url, protocol = self.get_url(request)
        print(f"{method} {url} {protocol}")
        web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        web_socket.connect((url, 80))
        web_socket.send(request)
        while True:
            response = web_socket.recv(4096)
            if len(response) > 0:
                client_socket.send(response)
            else:
                break
        web_socket.close()
        client_socket.close()

    def get_url(self, request):
        first_line = request.split(b"\n")[0]
        words = first_line.split()
        url = words[1]
        http_pos = url.find(b"://")
        if http_pos == -1:
            temp = url
        else:
            temp = url[(http_pos + 3):]
        port_pos = temp.find(b":")
        webserver_pos = temp.find(b"/")
        if webserver_pos == -1:
            webserver_pos = len(temp)
        webserver = ""
        port = -1
        if port_pos == -1 or webserver_pos < port_pos:
            port = 80
            webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
            webserver = temp[:port_pos]
        return words[0], webserver, words[2]


if __name__ == "__main__":
    proxy = Proxy("127.0.0.1", 8080)
    proxy.start()
