"""
@author: yiping
"""
import socket
import select
# from handlers import client_handlier
from Session import session
from server.server_global import *

from server.handler import *
from MessageType.message_function import *

def handle_retrieve_public_key(res):
    pass


class Server:
    def __init__(self):
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.bind((SERVER_HOST, SERVER_PORT))

    def start(self):
        self.listen_socket.listen(1)
        print(f"server listen on {SERVER_HOST}:{SERVER_PORT}")

        while True:
            [rlist, wlist, elist] = select.select(list(map(lambda session: session.socket, sessions)) + [self.listen_socket], [],
                                                  [])
            for s in rlist:
                if s == self.listen_socket:  # new connection
                    print('find new connection')
                    sess = self.create_new_session(s)
                    if sess is not None:
                        socket2session[sess.socket] = sess # store new session with the newly created data socket as key
                        id = sess.user['id']
                        id2session[id] = sess
                        sessions.append(sess)
                        bytes_buffer[sess] = bytes()
                        received[sess] = 0
                        to_receive[sess] = 0

                    continue

                # the rest logic deals with existed session
                sess = socket2session[s]
                if received[sess] == 0 and to_receive[sess] == 0:  # receive message from client
                    try:
                        header_bytes = sess.socket.recv(4, socket.MSG_WAITALL) # receive message length
                    except ConnectionError:
                        sess.socket.close()
                        self.remove_session(sess)
                        print(f"{sess.user} left")
                        continue
                    if header_bytes == '' or len(header_bytes) != 4:
                        print(f"{sess.user} broke down.")
                        sess.socket.close()
                        self.remove_session(sess)
                        # print(len(header_bytes))
                        # print(header_bytes)
                        continue

                    if len(header_bytes) == 4:
                        body_length = int.from_bytes(header_bytes, byteorder='big')
                        # print('next message length:' + str(body_length))
                        to_receive[sess] = body_length
                        bytes_buffer[sess] = bytes()

                bytes_buffer[sess] += sess.socket.recv(to_receive[sess] - received[sess])
                # print("length of buffer %d "  % len(bytes_buffer[sess]))
                received[sess] = len(bytes_buffer[sess])

                # print(to_receive[sess], received[sess])
                if received[sess] == to_receive[sess] and len(bytes_buffer[sess]) != 0:
                    received[sess] = 0
                    to_receive[sess] = 0
                    obj = sess.parse_message(bytes_buffer[sess])
                    print(f'recieved: {obj}')

                    res_msg = handle_start(obj, sess)
                    bytes_buffer[sess] = bytes()

    def close(self):
        self.listen_socket.close()


    def create_new_session(self, listen_socket):
        # and save session
        conn, addr = listen_socket.accept()
        received_byte = conn.recv(1024)
        res = parse_message(received_byte)
        print('received: ' + str(res))

        obj = handle_register(res, conn, addr)
        # [session_key, enc_session_key] = session.generate_encrypt_session_key(res['public'])
        new_sess = session.Session(conn, addr, public=res['public'])

        if obj['status'] == 1:
            new_sess.user = users[res['id']]

        new_sess.send_session_key(obj)

        return new_sess

    def remove_session(self, sess):
        if sess in sessions:
            sessions.remove(sess)

        if sess.user != None:
            id = sess.user['id']
            if id in id2session:
                del id2session[id]

        if sess.socket in socket2session:
            del socket2session[sess.socket]


if __name__ == "__main__":
    server = Server()
    server.start()
