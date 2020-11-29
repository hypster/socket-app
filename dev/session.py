from message_function import *
class Session:
    def __init__(self, socket, token, addr, user = None):
        self.socket = socket
        self.token = token
        self.addr = addr
        self.user = user

    def send(self, msg):
        return self.socket.sendall(self.encrypt(format_message(msg)))

    def receive(self, data):
        return data

    def decrypt(self, data):
        #TODO
        return data

    def encrypt(self, msg):
        #TODO
        return msg