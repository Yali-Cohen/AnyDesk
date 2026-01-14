import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", 0))
print(socket.gethostbyname(socket.gethostname()))
print(s.getsockname()[1])