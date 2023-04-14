# server code
import socket

s = socket.socket()
host = socket.gethostname()
print('hostname',host)
port = 1717
s.bind((host, port))

s.listen(5)
while True:
    c,addr = s.accept()
    print("Got connection ", addr)
    c.send("Meeting is at 10am")
    c.close()

