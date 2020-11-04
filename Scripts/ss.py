'''
-*- coding: UTF-8 -*-

@author: Tianchen Luo

Abr: serve 1
Useless, just for test
'''

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(),1234)) # socket is the end point that receive data
s.listen(5)

while True:
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established")
    clientsocket.send(bytes("Welcome to the server!","utf-8"))