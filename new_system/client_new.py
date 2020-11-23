import json
import re
import socket
import time

from crypto.Cipher import PKCS1_OAEP, AES
from crypto.PublicKey import RSA
from crypto.Random import get_random_bytes


class Client:
    def __init__(self, json_f):
        with open(json_f) as json_file:
            json_data = json.load(json_file)

        # personal info
        name = str(json_data['person']['name']).split(", ")
        self.first_name = name[0].lower()
        self.last_name = name[1].lower()
        self.id = json_data['person']['id']
        self.public_key = json_data['person']['keys']['public']
        self.private_key = json_data['person']['keys']['private']
        self.actions = json_data['actions']

        # general info
        self.retries = json_data['general']['retries']
        self.duration = json_data['general']['duration']
        self.timeout = json_data['general']['timeout']

        # server info
        self.server_port = int(json_data['server']['port'])
        self.server_ip = str(json_data['server']['ip'])

        self.log_messages = []
        json_file.close()

    # encrypt and decrypt is the same as in our previous ones
    def encrypt_message(self, plaintext, public_key):
        if not public_key.startswith("-----BEGIN RSA PUBLIC KEY-----"):
            public_key = "-----BEGIN RSA PUBLIC KEY-----\n" + public_key + "\n-----END RSA PUBLIC KEY-----"
        recipient_key = RSA.importKey(public_key)
        session_key = get_random_bytes(16)

        # Encrypt the session key with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        enc_session_key = cipher_rsa.encrypt(session_key)

        # Encrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(plaintext.encode("UTF-8"))
        encrypted_message = b"".join([x for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)])
        return encrypted_message

    def decrypt_store_message(self, encrypted_message):
        key = self.private_key
        if not key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
            key = "-----BEGIN RSA PRIVATE KEY-----\n" + key + "\n-----END RSA PRIVATE KEY-----"
        key = RSA.importKey(key)
        entc_list = []
        i = 0
        for x in (key.size_in_bytes(), 16, 16, -1):
            if i == 3:
                entc_list.append(message)
            else:
                entc_list.append(message[:x])
            i += 1
            message = message[x:]
        enc_session_key, nonce, tag, ciphertext = entc_list
        # Decrypt the session key with the private RSA key

        cipher_rsa = PKCS1_OAEP.new(key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        # Decrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        encoded_message = cipher_aes.decrypt_and_verify(ciphertext, tag)
        decoded_message =  encoded_message.decode("utf-8")

        # add to log and return
        self.log_messages.append(decoded_message)
        return decoded_message

    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_ip, self.server_port))

        # register [ID] [FIRST_NAME] [LAST_NAME] [PUBLIC_KEY]
        registration_message = 'register [' + str(self.id) + '] [' + str(self.first_name) + '] [' + str(
            self.last_name) + '] [' + str(self.public_key) + ']'
        s.sendall(bytes(registration_message, encoding='utf-8'))
        print(s.recv(1024).decode('utf-8'))  # this should be the accept message
        current_time = time.time()

        while int(self.duration) > (time.time() - current_time):
            # receive message!
            data = s.recv(1024)
            if data is not None:
                data = data.decode('utf-8')
                print("Received: ", data)

            current_action = 0

            if current_action < len(self.actions):
                print('new action found')
                message_delivered = False
                action = self.actions[current_action]
                current_action = current_action + 1

                action_info = re.findall(r"[^[]*\[([^]]*)\]", action)
                # check whether name or id is given
                if ',' not in action_info[0]:
                    id_needed = action_info[0]
                    s.sendall(bytes("receive_key_id [" + id_needed + ']', encoding='utf-8'))

                    data = s.recv(1024)
                    if data is not None:
                        data = data.decode('utf-8')
                        print("Received: ", data)
                        info = re.findall(r"[^[]*\[([^]]*)\]", data)

                    if data.lower().startswith('key'):
                        key = info[0]
                        encr = self.encrypt_message(action_info[1], key)
                        s.sendall(bytes("send [" + str(id_needed) + "] [" + encr + "]", encoding='utf-8'))
                        message_delivered = True

                        tries = 0
                        while not message_delivered and tries < self.retries:
                            time.sleep(self.timeout)
                            s.sendall(bytes(action, encoding='utf-8'))
                            tries = tries + 1

