"""
@author: yiping
"""
import socket
import select
import json
from message_function import *
from threading import Thread
import struct
from session import Session
from tkinter import *
from tkinter import messagebox
from client import client_global
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 52228
BUFLEN = 1024

def parse_action(action):
    verb = action.split(' ')[0].strip()
    if verb == 'SEND':
        start = action.index('[')
        end = action.index(']')
        nameorid = action[start+1:end]
        action = action[end+1:]
        start = action.index('[')
        end = action.index(']')
        msg = action[start+1:end]
        if ',' in nameorid:
            [firstname, lastname] = nameorid.split(',')
            firstname = firstname.strip()
            lastname = lastname.strip()
            return json.dumps({'type':'send', 'firstname': firstname, 'lastname': lastname, 'message': msg})
        else:
            return json.dumps({'type': 'send', 'id':  nameorid, 'message': msg})


class Client:
    def __init__(self, config_file = ''):
        self.info = self.read_info(config_file)
        self._g = self.next_msg()
        server = self.info['server']
        root = Tk()
        client_global.tk_root_global = root
        root.title('A secret message app')

        txt_chat = Text(root)
        self.txt_chat = txt_chat
        self.txt_chat = txt_chat
        txt_chat.insert(END, "Welcome to the secrete world.....\n")

        lbl_input = Label(root,text='Enter messsage here:')
        ent_input = Entry(root)
        txt_chat.pack()
        btn_send = Button(root, text='send from json',command = self.send_from_json)


        lbl_input.pack(side=LEFT)
        ent_input.pack(side=LEFT, fill=BOTH, expand=TRUE)
        btn_send.pack(side=LEFT)
        client_global.session_global = self.start_session(server['ip'], int(server['port']))
        if client_global.session_global.socket:
            t = Thread(target=self.main_listener_thread, args=(client_global.session_global, client_global.tk_root_global),daemon=True)
            t.start()

            root.mainloop()

        try:
            root.destroy()
        except TclError:
            pass

    def main_listener_thread(self, session, tk_root):
        print('entering main thread')
        bytes_buffer = bytes()  # store receive message from session
        received = 0  # bytes received so far
        to_receive = 0  # bytes to receive
        while (tk_root):
            rlist, wlist, xlist = select.select([session.socket], [session.socket],
                                                [])  # only need to listen socket from its session
            if len(rlist):
                print('some change detected')
                if received == 0 and to_receive == 0:  # if new packet is comming
                    connection = True
                    length_bytes = b''
                    try:
                        length_bytes = session.socket.recv(4, socket.MSG_WAITALL)
                    except ConnectionError:
                        print("server has been shut down.")
                        child = []
                        for key in tk_root.children:
                            child.append(tk_root.children[key])
                        for i in child:
                            i.destroy()
                        tk_root.destroy()
                        connection = False

                    if length_bytes == '' or len(length_bytes) < 4:
                        connection = False
                        messagebox.showerror(message="Can't connect to server. Server might be down")
                        child = []
                        for key in tk_root.children:
                            child.append(tk_root.children[key])
                        for i in child:
                            i.destroy()
                        tk_root.destroy()

                    if connection:
                        bytes_buffer = bytes()
                        to_receive = struct.unpack('!L', length_bytes)[0]
                        print('to receive: ' + str(to_receive))

                bytes_buffer += session.socket.recv(to_receive - received, socket.MSG_WAITALL)

                received = len(bytes_buffer)
                print(received, to_receive)
                if received == to_receive and len(bytes_buffer) != 0:
                    print("receive a package")
                    received = 0
                    to_receive = 0
                    res = parse_message(bytes_buffer)
                    # TODO: show in chat window
                    print(f'received: + {str(res)}')
                    show_str = f"received message from user: {res['firstname']}, {res['lastname']} with id {res['id']}\n{res['message']}\n"
                    self.txt_chat.insert(END, show_str)
                    bytes_buffer = bytes()

    def start_session(self, host, port):
        # t = Thread(target=main_listener_thread, args=(client_global.session, client_global.tkroot),
        #                      daemon=True)
        session = None
        self.txt_chat.insert(END, "start new session...\n")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        # s.send("public key".encode('utf-8'))
        # server_secret = s.recv(1024)
        # server_secret = int.from_bytes(server_secret, 'big')

        # session_key = crypt.get_shared_secret("server secret")
        self.register(s)
        received_byte = s.recv(1024)
        res = parse_message(received_byte)
        self.txt_chat.insert(END, 'response: ' + str(res) + '\n')

        # TODO: generate shared secret
        if res['status'] == 1:
            session = Session(s, res['public'], (host,port))
        else:
            s.close()

        return session

    def start_and_register(self, host, post):
        self.start(host, post)
        self.register()

    def read_info(self, config_file):
        with open(config_file, 'rb') as f:
            return json.loads(f.read())

    def register(self, s):
        print('sending register request')
        person = self.info['person']
        id = person['id']
        name = person['name']
        [firstname, lastname] = name.split(',')
        firstname = firstname.strip()
        lastname = lastname.strip()
        public = person['keys']['public']
        body = {'type':'register', 'id': id, 'firstname': firstname, 'lastname': lastname, 'public': public}
        body = json.dumps(body)
        # self.txt_chat.insert(END, 'send register message:' + body + '\n')
        s.sendall(body.encode('utf-8'))

    def send_from_json(self):
        try:
            sess = client_global.session_global
            s = sess.socket
            msg = next(self._g)
            print(msg)
            s.sendall(msg)
        except StopIteration:
            print("finish sending all messages.")
            s.close()
            print("connection closed")

    def do_action(self):
        try:

            self.data_socket.sendall(next(self._g))
        except StopIteration:
            print("finish sending all messages.")
            self.data_socket.close()
            print("connection closed")


    def next_msg(self):
        for action in self.info['actions']:
            msg = parse_action(action)
            msg = format_message(msg)
            yield msg

    def do_actions(self):
        s = self.data_socket
        for ms in self._g:
            s.send(ms)

        self.close()

    def close(self):
        self.data_socket.close()


def automate(config):
    c = Client(config)
    c.register()
    c.do_actions()


if __name__ == '__main__':
    # for i in range(2):
    #     th = Thread(target=automate, args=(f'./config_{i+1}.json',)) #create a thread for processing dialog
    #     th.start()

    c = Client(config_file='./config_1.json')
    # c.register()



