from client1 import Client
c = Client()
c.connect(("192.168.1.228", 1234))
print(c.receive())
c.send("Hello from client".encode())