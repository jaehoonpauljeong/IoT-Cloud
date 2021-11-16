
#!/usr/bin/python3
# by Yiwen Shen (SKKU)
# Email: chrisshen@skku.edu

import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
# client = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) # UDP
# client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
client.bind(("", 6000))
while True:
    data, addr = client.recvfrom(1024)
    decodedData = data.decode("utf-8")
    print("received message: %s"%data)
    print("decoded message: ", decodedData)
    print("addr: ", addr)