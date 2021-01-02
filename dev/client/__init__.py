import socket
import select
from MessageType.message_function import *
from threading import Thread
import struct
from Session.session import Session
from tkinter import *
from tkinter import messagebox
from client import client_global
from client.parser import parse_action
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import MessageType
from datetime import datetime
from time import sleep
import log_config
import logging

class Client:
    def __init__(self, config_file='', log_file=''):
        log_config.config(log_file)
        self.info = self.read_info(config_file)
        self.retries = int(self.info['general']['retries'])
        self._g = self.next_msg()
        self.msg_task = {}  # storing message task that's yet to be completed
        self.pending_msg = {}  # store message that has been sent but with no ack from server yet
        server = self.info['server']
        root = self.draw_ui()

        self.public_keys = {}

        self.handlers = {}
        self.register_all_handlers()

        pk_str = '-----BEGIN RSA PRIVATE KEY-----\n' + self.info['person']['keys'][
            'private'] + '\n-----END RSA PRIVATE KEY-----'
        self.private_key = RSA.importKey(pk_str)
        self.cipher_rsa = PKCS1_OAEP.new(self.private_key)

        self.session = self.start_session(server['ip'], int(server['port']))
        if self.session.socket:
            t = Thread(target=self.main_listener_thread,
                       args=(self.session, client_global.tk_root_global), daemon=True)
            t.start()

            root.mainloop()

        try:
            root.destroy()
        except TclError:
            pass

    def draw_ui(self):
        root = Tk()
        client_global.tk_root_global = root
        root.title(f"{self.info['person']['name']}")

        txt_chat = Text(root)
        self.txt_chat = txt_chat

        txt_chat.insert(END, "Welcome to the secrete world.....\n")

        lbl_input = Label(root, text='Enter messsage here:')
        ent_input = Text(root)
        ent_input.bind("<Control-Return>", self.send_from_input)
        self.ent_input = ent_input
        txt_chat.pack()
        btn_send_json = Button(root, text='Send prewritten message', command=self.send_from_json)
        btn_send = Button(root, text='Send(ctrl+enter)', command=self.send_from_input)
        lbl_input.pack() #side = LEFT
        ent_input.pack() #side=LEFT, fill=BOTH, expand=TRUE
        btn_send.pack(side=RIGHT) #side=LEFT
        btn_send_json.pack(side=RIGHT) #side=LEFT
        return root

    def main_listener_thread(self, session, tk_root):
        bytes_buffer = bytes()  # store receive message from session
        received = 0  # bytes received so far
        to_receive = 0  # bytes to receive
        while (tk_root):
            rlist, wlist, xlist = select.select([session.socket], [session.socket],
                                                [])  # only need to listen socket from its session
            if len(rlist):
                if received == 0 and to_receive == 0:  # if new packet is comming
                    connection = True
                    length_bytes = b''
                    try:
                        length_bytes = session.socket.recv(4, socket.MSG_WAITALL)
                    except ConnectionError:
                        logging.error("server has been shut down.")
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
                        # print('to receive: ' + str(to_receive))

                bytes_buffer += session.socket.recv(to_receive - received, socket.MSG_WAITALL)

                received = len(bytes_buffer)
                if received == to_receive and len(bytes_buffer) != 0:
                    received = 0
                    to_receive = 0
                    res = session.parse_message(bytes_buffer)

                    # print(f'received: {str(res)}')
                    # show_str = f"received message from user: {res['firstname']}, {res['lastname']} with id {res['id']}\n{res['message']}\n"
                    # self.txt_chat.insert(END, show_str)
                    self.handle_start(res)
                    bytes_buffer = bytes()


    def register_all_handlers(self):
        self.add_handler(MessageType.ACK, self.handle_ack_general)
        self.add_handler(MessageType.ACK_MSG, self.handle_ack_message)
        self.add_handler(MessageType.PUB_KEY, self.handle_public_key)
        self.add_handler(MessageType.USER_MSG, self.handle_user_message)

    def start_session(self, host, port):

        self.txt_chat.insert(END, "Register and start new session...\n")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        self.register(s)

        length_bytes = s.recv(4, socket.MSG_WAITALL)
        to_receive = struct.unpack('!L', length_bytes)[0]
        bytes_buffer = s.recv(to_receive, socket.MSG_WAITALL)

        session_key, b_msg = self.decrypt_session_key(bytes_buffer)

        new_sess = Session(s, (host, port), session_key=session_key)

        self.txt_chat.insert(END, 'Secure connection established\n')

        res = new_sess.parse_message(b_msg)

        if res['status'] != 1:
            messagebox.showinfo(message=res['text'])
            exit(1)

        else:
            logging.debug(f"From server: {(res['text'])}\n")
            # show_str = f"received message from user: {res['firstname']}, {res['lastname']} with id {res['id']}\n{res['message']}\n"
            self.txt_chat.insert(END, 'From server:\n' + res['text'] + '\n')

            return new_sess

    def decrypt_session_key(self, b_msg):
        msg_arr = []
        for x in (self.private_key.size_in_bytes(), -1):
            if x == -1:
                msg_arr.append(b_msg)
            else:
                msg_arr.append(b_msg[0:x])
                b_msg = b_msg[x:]
        session_key = self.cipher_rsa.decrypt(msg_arr[0])  # Decrypt the session key with the private RSA key
        return session_key, msg_arr[1]

    def decrypt_message(self, received_byte):
        """

        :param received_byte:
        :return: decoded string
        """
        msg_arr = []
        for x in (self.private_key.size_in_bytes(), 16, 16, -1):
            if x == -1:
                msg_arr.append(received_byte)
            else:
                msg_arr.append(received_byte[0:x])
                received_byte = received_byte[x:]
        [enc_session_key, nonce, tag, ciphertext] = msg_arr
        # Decrypt the session key with the private RSA key
        session_key = self.cipher_rsa.decrypt(enc_session_key)

        # Decrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        # data = cipher_aes.decrypt(ciphertext)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        return data.decode("utf-8")

    def start_and_register(self, host, post):
        self.start(host, post)
        self.register()

    def read_info(self, config_file):
        with open(config_file, 'rb') as f:
            return json.loads(f.read())

    def register(self, s):
        logging.debug('sending register request')
        person = self.info['person']
        id = person['id']
        name = person['name']
        [firstname, lastname] = name.split(',')
        firstname = firstname.strip()
        lastname = lastname.strip()
        public = person['keys']['public']
        body = {'type': MessageType.Request.REGISTER, 'id': id, 'firstname': firstname, 'lastname': lastname, 'public': public}
        body = json.dumps(body)
        s.sendall(body.encode('utf-8'))

    def send_from_input(self, _=None):
        txt = self.ent_input.get("1.0",END)
        self.ent_input.delete("1.0", END)
        msg = parse_action(txt)
        if msg is None:
            return self.txt_chat.insert(END, f"Input format: send [firstname, lastname]/[id] [your message]\n")
        else:
            self.start_send(msg)

    def start_send(self, msg):
        msg['retries'] = self.retries
        msg['message_id'] = client_global.pending_id
        client_global.pending_id += 1
        logging.debug(msg)
        public_keys = []
        if 'firstname' in msg and 'lastname' in msg:
            firstname = msg['firstname'].lower()
            lastname = msg['lastname'].lower()
            name = (firstname, lastname)

            if name not in client_global.name2id:
                logging.debug("Public key is not in the list, retrieve first")
                self.txt_chat.insert(END,
                                     'Receiver\'s public key is not available locally, send retrieve request to server\n')
                self.msg_task[msg['message_id']] = msg
                self.retrieve_public_key(first_name=firstname, last_name=lastname)
            else:
                ids = client_global.name2id[name]
                for _id in ids:
                    public_key = client_global.public_keys[_id]
                    self.send2other(public_key, msg)

        elif 'id' in msg:
            if msg['id'] not in client_global.public_keys:
                logging.debug("Public key is not in the list, retrieving first")
                self.txt_chat.insert(END,
                                     'Receiver\'s public key is not available locally, send retrieve request to server\n')

                self.msg_task[msg['message_id']] = msg
                self.retrieve_public_key(_id=msg['id'])
            else:
                public_key = client_global.public_keys[msg['id']]
                self.send2other(public_key, msg)

    def send_from_json(self):
        try:
            msg = next(self._g)
            self.start_send(msg)
        except StopIteration:
            messagebox.showinfo("Message list is empty", "You have no more prewritten message to send.")


    def send2other(self, public_key, msg):
        logging.debug(msg)
        self.pending_msg[msg['message_id']] = msg
        # msg['message_id'] = client_global.pending_id  # add message id
        # client_global.pending_id += 1
        cipher_text = self.session.encrypt_RSA(public_key, msg['message'])
        msg = msg.copy()
        msg['message'] = [c for c in cipher_text]
        self.session.send(msg)

    def parse_user_message(self, msg):
        cipher_text = bytes(msg['message'])
        cipher_rsa = PKCS1_OAEP.new(self.private_key)
        msg['message'] = cipher_rsa.decrypt(cipher_text).decode('utf-8')
        return msg

    def retrieve_public_key(self, _id=None, first_name=None, last_name=None):
        if _id is not None:
            self.session.send({'type': MessageType.Request.RET_PUB_KEY, 'id': _id})
        elif first_name is not None and last_name is not None:
            self.session.send({'type': MessageType.Request.RET_PUB_KEY, 'firstname': first_name, 'lastname': last_name})

    def add_handler(self, type, handle):
            self.handlers[type] = handle

    def handle_start(self, res):
        # logging.debug(f'received: {res}')
        if 'type' in res:
            _type = res['type']
            if _type in self.handlers:
                self.handlers[_type](res)


    def handle_ack_general(self, res):
        if res['type'] == MessageType.ACK:
            msg = f"From server:\nres['text']\n"
            self.txt_chat.insert(END, msg)

    def handle_ack_message(self, res):
        if res['type'] == MessageType.ACK_MSG:
            if res['status'] == 1:
                time = datetime.fromtimestamp(res['timestamp']).ctime()
                m_id = res['message_id']
                origin_msg = self.pending_msg[m_id]
                msg = origin_msg['message']
                if msg.startswith('[') and msg.endswith(']'):
                    msg = msg[1:-1]

                if 'firstname' in origin_msg:
                    idorname = origin_msg['firstname'].capitalize() + ' ' + origin_msg['lastname'].capitalize()
                else:
                    idorname = origin_msg['id']
                self.txt_chat.insert(END, f"To {idorname} at {time}:\n{msg}\n")
                logging.info(f'To {idorname}: {msg}')
                self.remove_pending_message(m_id)

            else:  # send message error
                msg = f'From server:\n{res["text"]}\n'
                self.txt_chat.insert(END, msg)
                m_id = res['message_id']
                num_left = self.pending_msg[m_id]['retries']
                if num_left > 0:
                    t = Thread(target=self.retry, args=(m_id, num_left, res))
                    t.start()

    def retry(self, m_id, num_left, res):
        duration = int(self.info['general']['timeout'])
        self.txt_chat.insert(END, f'Retry after {duration} second(s)\n')
        sleep(duration)
        if m_id not in self.pending_msg:  # message has been successfully sent
            return logging.debug("message has already been sent. Abort retry action.")
        self.pending_msg[m_id]['retries'] -= 1
        self.txt_chat.insert(END, f'Retry {self.retries - num_left + 1}th time\n')
        for _id in res['ids']:  # list of ids that are not online earlier
            public_key = client_global.public_keys[_id]
            self.send2other(public_key, self.pending_msg[m_id])

    def remove_pending_message(self, m_id):
        if m_id in self.pending_msg:
            del self.pending_msg[m_id]

    def remove_from_message_task(self, m_id):
        if m_id in self.msg_task:
            del self.msg_task[m_id]

    def handle_user_message(self, res):
        res = self.parse_user_message(res)
        flag = 0
        if 'meta' in res:
            flag = res['meta']

        sender = res['source']
        text = res['message']
        if text.startswith('[') and text.endswith(']'):
            text = text[1:-1]
        time = datetime.fromtimestamp(res['timestamp']).ctime()

        who = f"{sender['firstname'].capitalize()} {sender['lastname'].capitalize()}({sender['id']})"
        msg = f"From {who} at {time}:\n{text}\n"
        if flag: # if transaction success
            logging.info(f"From {who}: {text}")
        self.txt_chat.insert(END, msg)

    def handle_public_key(self, res):
        self.txt_chat.insert(END, "From server:\n" + res['text'] + '\n')
        if 'users' in res:  # req is posted by name
            user = res['users'][0]
            firstname = user['firstname'].lower()
            lastname = user['lastname'].lower()
            name = (firstname, lastname)
            if name not in client_global.name2id:
                client_global.name2id[name] = []
            for user in res['users']:
                client_global.name2id[name].append(user['id'])
                client_global.public_keys[user['id']] = user['public']

            m_ids = set()
            for _id in client_global.name2id[name]:
                for msg in self.msg_task.values():
                    if name == (msg['firstname'].lower(), msg['lastname'].lower()):
                        m_id = self._send(_id, msg['message_id'])
                        m_ids.add(m_id)

            for m_id in m_ids:
                self.remove_from_message_task(m_id)

        elif 'public' in res:  # req is posted by id
            client_global.public_keys[res['id']] = res['public']
            name = (res['firstname'].lower(), res['lastname'].lower())
            if name in client_global.name2id:
                client_global.name2id[name].append(res['id'])
            else:
                client_global.name2id[name] = [res['id']]

            m_ids = set()
            for msg in self.msg_task.values():
                if res['id'] == msg['id']:
                    m_id = self._send(res['id'], msg['message_id'])
                    m_ids.add(m_id)
            for m_id in m_ids:
                self.remove_from_message_task(m_id)

    def _send(self, _id, m_id):
        public_key = client_global.public_keys[_id]
        if m_id in self.msg_task:
            msg = self.msg_task[m_id]
            logging.debug("sending message encrypted with public key")
            self.send2other(public_key, msg)
        return m_id

    def next_msg(self):
        for action in self.info['actions']:
            msg = parse_action(action)
            yield msg

    def close(self):
        self.data_socket.close()


if __name__ == '__main__':
    pass
    # for i in range(2):
    #     th = Thread(target=automate, args=(f'./config_{i+1}.json',)) #create a thread for processing dialog
    #     th.start()
    # c = Client(config_file='./config_1.json')
    # c.register()
