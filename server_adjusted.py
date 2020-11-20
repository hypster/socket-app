import codecs
import socket
import threading
import base64
import json
from multipledispatch import dispatch
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

# TODO: add a client class ? so we can let it initialise with the JSON file

# register client at the server
@dispatch(str, str, str)
def register(id, name, public_key):
    registered = True

    new_user = [{
        'id': id,
        'name': name,
        'public_key': public_key
    }]

    for i in client_information:
        if i['id'] == new_user['id']:
            registered = False
            return register

    if registered:
        client_information.append(new_user)
        with codecs.open('json_files/all_users.json', 'r+', encoding='utf8') as users_file:
            data = json.load(users_file)
            for user in data['users']:
                if user['id'] == new_user[0]['id']:
                    return
            data['users'] += new_user
            users_file.seek(0)
            json.dump(data, users_file, indent=4)
            users_file.truncate()
            return registered


# return public key of someone
@dispatch(str)
def retrieve_public_key(user_id):
    global client_information
    for i in client_information:
        if i['id'] == user_id:
            return i['key']
    return


# return list of all public keys of people with the same name (and their ids to identify them) - tuples
# as everyone with the same name should get a message if this is sent to them
@dispatch(str, str)
def retrieve_public_key(name):
    clients_with_this_name = []
    global client_information
    for i in client_information:
        if i['name'] == name:
            clients_with_this_name.append((i['id'], i['public_key']))
    return clients_with_this_name


def show_whois_online(user_id, public_key):
    global client_information
    for single_client in client_information:
        if single_client[0] == user_id:
            single_client[3].sendall(
                encrypt_message(public_key, ', '.join([client_id[0] for client_id in client_information])))


# TODO: add the base64 encryption
# TODO: perform encryption in client
# for now, it echoes
def client_connection(clientconn, address):  # for just one client
    global client_information

    print("Connected by: ", address)
    data = clientconn.recv(1024)

    # gets data from user - which it needs to register
    data_in_json = json.loads(data.decode('utf-8').replace("'", '"'))
    client_id, name, public_key = data_in_json[0]['id'], data_in_json[0]['name'], data_in_json[0]['public_key']

    # register client
    registered = register(client_id, name, public_key)
    if registered:
        clientconn.sendall(encrypt_message(public_key, "Registered successfully!"))
        id_connections.append((client_id, clientconn))
    else:
        clientconn.sendall(encrypt_message(public_key, "Could not register!"))

    # TODO: add things like get public key to this - so client is able to encrypt
    while threading.currentThread().is_alive():
        while True:
            data = clientconn.recv(1024)
            if data.decode("utf-8").startswith("SEND"):
                data = data.decode("utf-8").split(" ", maxsplit=2)
                send_message(client_id, data[1], data[2])
            elif data.decode("utf-8") == "ONLINE":
                show_whois_online(client_id, public_key)
    client_information = [conn_client for conn_client in client_information if conn_client[0] != client_id]
    clientconn.close()


# TODO: plaintext message needs to be encrypted in client before we do this
# TODO: implement send_message with the -name- of someone
def send_message(sender_id, receiver_id, plaintext_message):
    for single_client in client_information:
        if single_client['id'] == receiver_id:
            message = "Message from: "+sender_id+": "+plaintext_message
            message = encrypt_message(single_client['public_key'], message)
            for i in id_connections:
                if i[0] == receiver_id:
                    single_client[i[1]].sendall(message)
    return


# TODO: needs to be done in client - using the get public key methods
# TODO: also, I think we need to use base64 encoding?
def encrypt_message(public_key, message):
    if not public_key.startswith("-----BEGIN RSA PUBLIC KEY-----"):
        public_key = "-----BEGIN RSA PUBLIC KEY-----\n"+public_key+"\n-----END RSA PUBLIC KEY-----"
    recipient_key = RSA.importKey(public_key)
    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(message.encode("UTF-8"))
    encrypted_message = b"".join([x for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)])
    return encrypted_message


# TODO: check everything and add remaining functions, test functionality

HOST = '127.0.0.1'
PORT = 13370
client_information = []
id_connections = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# infinite loop, creates different thread for every client
while True:
    client, address = server.accept()
    client_thread = threading.Thread(args=(client, address), target=client_connection)
    client_thread.start()  # to be able to handle multiple clients