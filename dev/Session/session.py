from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from MessageType.message_function import *
import socket

class Session:
    def __init__(self, socket, addr, public=None,session_key=None,user = None):
        self.socket = socket
        self.public = public
        self.addr = addr
        self.user = user
        if session_key is None:
            self.session_key = get_random_bytes(16)
        else:
            self.session_key = session_key

        # print(f'session key:  {session_key}')


    def send(self, msg): #AES send
        bmsg = json.dumps(msg).encode('utf-8')
        cipher_aes = AES.new(self.session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(bmsg)
        self.socket.sendall(format_message(cipher_aes.nonce + tag + ciphertext))

    def receive(self):
        s = self.socket
        length_bytes = s.recv(4, socket.MSG_WAITALL)
        to_receive = struct.unpack('!L', length_bytes)[0]
        bytes_buffer = s.recv(to_receive, socket.MSG_WAITALL)
        return self.parse_message(bytes_buffer)

    def send_session_key(self, msg):
        enc_session_key = self.encrypt_RSA(self.public, self.session_key)
        b_msg = json.dumps(msg).encode('utf-8')
        cipher_aes = AES.new(self.session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(b_msg)
        b_msg = enc_session_key + cipher_aes.nonce + tag + ciphertext
        self.socket.sendall(format_message(b_msg))

    def parse_message(self, received_byte):
        msg_arr = []
        for x in (16, 16, -1):
            if x == -1:
                msg_arr.append(received_byte)
            else:
                msg_arr.append(received_byte[0:x])
                received_byte = received_byte[x:]
        [nonce, tag, ciphertext] = msg_arr

        btext = self.decrypt_AES(nonce, tag, ciphertext)
        return parse_message(btext)

    def decrypt_AES(self, nonce, tag, ciphertext):
        try:
            cipher = AES.new(self.session_key, AES.MODE_EAX, nonce)
            return cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError:
            print('your message is tampered')
            exit(1)

    def encrypt_format_session_message(self, msg):
        cipher_aes = AES.new(self.session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(msg)
        return format_message(self.enc_session_key + cipher_aes.nonce + tag + ciphertext)


    def encrypt_RSA(self, public_key_str, msg):
        public_key_str = '-----BEGIN RSA PUBLIC KEY-----\n' + public_key_str + '\n-----END RSA PUBLIC KEY-----'
        public_key = RSA.importKey(public_key_str)
        cipher_rsa = PKCS1_OAEP.new(public_key)
        if type(msg) != bytes:
            msg = bytes(msg, 'utf-8')
        return cipher_rsa.encrypt(msg)




if __name__ == '__main__':
    s = Session(None, None, 'MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA33bh0ZPszl9wxWqP5TWtvO44QrqSdNA3yoPCRf8gBXvthOK9QK/xLART+q9yPIXjdUyR855GeAiPXvbee7IjzgY1ZGKBfpTxojPn13M+xRCae0SCezTWGZ1sxYYB1FRUsfQaTzzPC6wgJrYwh4BoRruWTruXzq3UbtQxmDKqCO2D0nIzrnubZQLfXBFMyGkVnqghiGblbXd7TcT6eJA7kGLnrCWhgt/TlLQwudOZ1VdfB7cHcNX8gCHV4E9rEoPMTEoc+kzXNEyWkdnivuNg7z1sGW2jDuHCcOEYJxwq6UaRn3qwe54VfkkMonR+d5UYuwJIbWuUhog5jcUbCQ5v8YhThk3vgiE6sDulAx1cOtCBk1JofTTnNOxzLOnxz82UUBYB0hUXRsWl8U15wELXIAw5glUzc0gVLMJeiLKwye7zCebpEL+HhKtTBcW6q7VWV4cu3dls18Tf+UjtMB+wRvh25y0mBNK+odKmVmko2Lf+IaAsbYvcjQTqxCVvIGqvQ9683RFBu1cPQkyiy60KldkRWVjTei98PjQafcqhxTAgUCBByoNuzTn+w0Mi1By4kIWkqOXEQWUQ0aprHPsk7v//aIJM2rBltcGk0EedwWvoiGaKzjdqIkXEP7RDM/h2V6VpYYAuPxsnSx1yPWfnixcoefQDDWXvBcvuvuRtAmcCAwEAAQ==', None)
    s.encrypt(b"hello")