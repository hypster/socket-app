import socket
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP


def decode_rsa_message(message):
    key = private_key
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
    return encoded_message.decode("utf-8")

with open("json_files/config_1.json") as json_file:
    json_data = json.load(json_file)
    HOST = json_data['server']['ip']
    PORT = int(json_data['server']['port'])

public_json_data = json.dumps([{'id': json_data['person']['id'], 'name': json_data['person']['name'],
                                'public_key': json_data['person']['keys']['public']}])
private_key = json_data['person']['keys']['private']

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(bytes(public_json_data, encoding='UTF-8'))
    while True:
        data = s.recv(1024)
        print('Received', decode_rsa_message(data))
        text = input()
        s.sendall(bytes(text, encoding='UTF-8'))

