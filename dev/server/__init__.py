"""
@author: yiping
"""
import socket
from threading import Thread
import json
from message_function import get_response, format_message
import select
# from handlers import client_handlier
import session
from server.server_global import *

from server.handler import *
from message_function import *

def handle_retrieve_public_key(res):
    pass


class Server:
    def __init__(self):
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.bind((SERVER_HOST, SERVER_PORT))

    def start(self):
        self.listen_socket.listen(1)
        print(f"server listen on {SERVER_HOST}:{SERVER_PORT}")
        # while True:
        #     data_socket, addr = self.listen_socket.accept()
        #     print(f'client {str(addr)} connected')
        #     th = Thread(target=client_handler, args=(data_socket, addr)) #create a thread for processing dialog
        #     th.start()
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
                        id2addr[id] = sess.addr
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
                        print("one client leave")
                        continue
                    if header_bytes == '' or len(header_bytes) != 4:
                        print("client broke down.")
                        sess.socket.close()
                        self.remove_session(sess)
                        print(len(header_bytes))
                        print(header_bytes)
                        continue

                    if len(header_bytes) == 4:
                        body_length = int.from_bytes(header_bytes, byteorder='big')
                        print('next message length:' + str(body_length))
                        to_receive[sess] = body_length
                        bytes_buffer[sess] = bytes()

                bytes_buffer[sess] += sess.socket.recv(to_receive[sess] - received[sess])
                # print("length of buffer %d "  % len(bytes_buffer[sess]))
                received[sess] = len(bytes_buffer[sess])

                print(to_receive[sess], received[sess])
                if received[sess] == to_receive[sess] and len(bytes_buffer[sess]) != 0:
                    received[sess] = 0
                    to_receive[sess] = 0
                    obj = parse_message(bytes_buffer[sess])
                    print(obj)
                    # TODO: sent return message to sender
                    handle_start(obj)
                    bytes_buffer[sess] = bytes()

    def close(self):
        self.listen_socket.close()

    def remove_connection(self, conn, addr):
        id = connections[addr]['user']
        if id is not None:  # when user is already logged in
            del id2addr[id]  # so that id and addr are no longer bound

        del connections[addr]

    def client_handler(self, conn, addr):
        """thread entry
                :param conn:
                :param addr:
                :return:
        """
        connections[addr] = {'socket': conn, 'user': None}  # first store the connection

        #     msg = get_response(conn)
        #     if not msg:  # if client closed connection
        #         print(f'client {addr} closes the connection')
        #         remove_connection(conn, addr)
        #         break
        #
        #     print(f'receive info from {addr}：\n \t\t\ {msg}')
        #     res = handle_start(msg, conn, addr)
        #     send_msg = json.dumps(res)
        #     conn.send(format_message(send_msg))
        # conn.close()

    def create_new_session(self, listen_socket):
        # TODO receive client secret, generate shared key
        # and save session
        conn, addr = listen_socket.accept()
        received_byte = conn.recv(1024)
        res = parse_message(received_byte)
        print('received: ' + str(res))

        obj = handle_register(res, conn, addr)
        new_sess = None
        # TODO: get client public key from res
        if obj['status'] == 1:

            obj['public'] = 'server public key'
            id = res['id']
            user = users[id]
            new_sess = session.Session(conn, addr, 'shared secretkey', user=user) # only create new session if registeration succussful
        conn.send(json.dumps(obj).encode('utf-8'))
        # TODO: generate shared secret key

        return new_sess

    def remove_session(sess):
        if sess in sessions:
            sessions.remove(sess)

        if sess.user != None:
            user = sess.user
            sess.user = None
            if user in user_to_session:
                del user_to_session[user]

        if sess.socket in socket_to_sessions:
            del socket_to_sessions[sess.socket]


if __name__ == "__main__":
    server = Server()
    server.start()
