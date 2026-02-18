# protocol/framing.py, how the send, recv will work. with json ending with \n
import json

def send_json_line(sock, obj: dict):
    msg = json.dumps(obj, separators=(",", ":")) + "\n"
    sock.sendall(msg.encode("utf-8"))

def iter_json_lines(sock, bufsize=4096):
    buffer = ""
    while True:
        chunk = sock.recv(bufsize).decode("utf-8", errors="ignore")
        if not chunk:
            return
        buffer += chunk
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if line:
                yield json.loads(line)