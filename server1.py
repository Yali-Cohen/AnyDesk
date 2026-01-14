#server1.py
# server1.py
import json
import socket

class Server:
    def __init__(self, host="0.0.0.0", port=8080):
        self.ip = self._get_best_local_ip()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind((host, port))
        self.port = self.server_socket.getsockname()[1]
        self.server_socket.listen(5)

        self.conn = None      # <-- פה נשמור את הסוקט המחובר
        self.conn_addr = None

    def _get_best_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return socket.gethostbyname(socket.gethostname())
        finally:
            s.close()

    def accept_connection(self):
        self.conn, self.conn_addr = self.server_socket.accept()
        print(f"Connection from {self.conn_addr} has been established!")
        return self.conn

    def getsockname(self):
        print(f"Server is listening on port: {self.port}")
        print(f"Server is listening on IP: {self.ip}")
        return (self.ip, self.port)

    def send(self, data: bytes):
        if not self.conn:
            raise RuntimeError("No active connection (did you call accept_connection()?)")
        self.conn.sendall(data)

    def receive(self, buffer_size=4096):
        if not self.conn:
            raise RuntimeError("No active connection (did you call accept_connection()?)")
        return self.conn.recv(buffer_size)

    def send_json(self, obj: dict):
        self.send(json.dumps(obj).encode("utf-8"))

    def receive_json(self):
        data = self.receive()
        if not data:
            return None
        return json.loads(data.decode("utf-8"))

    def close(self):
        try:
            if self.conn:
                self.conn.close()
        finally:
            self.server_socket.close()
