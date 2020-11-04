import socket

HOST = '127.0.0.1'
PORT = 13370

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    connection, address = s.accept()
    with connection:
        print("Connected by: ", address)
        while True:
            data = connection.recv(1024)
            if not data:
                break
            connection.sendall(data)

