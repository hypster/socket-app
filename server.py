import codecs
import socket
import threading
import base64
import json
from multipledispatch import dispatch
import rsa


# register client at the server
@dispatch(str, str, str)
def register(id, name, public_key):
    new_user = [{
        'id': id,
        'name': name,
        'public_key': public_key
    }]
    with codecs.open('json_files/all_users.json', 'r+', encoding='utf8') as users_file:
        data = json.load(users_file)
        for user in data['users']:
            if user['id'] == new_user[0]['id']:
                return
        data['users'] += new_user
        users_file.seek(0)
        json.dump(data, users_file, indent=4)
        users_file.truncate()


"""
Registers user based on the JSON file provided for authentication, and if a user exists, does not register them
"""


@dispatch(str)
def register(json_file):
    with codecs.open('json_files/all_users.json', 'r+', encoding='utf8') as users_file:
        data = json.load(users_file)
        for user in data['users']:
            if user['id'] == json_file[0]['id']:
                return
        data['users'] += json_file
        users_file.seek(0)
        json.dump(data, users_file, indent=4)
        users_file.truncate()


# return public key of someone
@dispatch(str)
def retrieve_public_key(user_id):
    global client_information
    for i in client_information:
        if i.index(0) == user_id:
            return i.index(3)


# return dictionary of all public keys of people with the same name (and their ids to identify them)
# as everyone with the same name should get a message if this is sent to them
@dispatch(str, str)
def retrieve_public_key(first_name, last_name):
    clients_with_this_name = {}
    global client_information
    for i in client_information:
        if i.index(1) == first_name and i.index(2) == last_name:
            clients_with_this_name[i.index(0)] = i.index(3)
            # key is the id!
    return clients_with_this_name


def show_whois_online(user_id):
    global client_information
    for single_client in client_information:
        if single_client[0] == user_id:
            single_client[3].sendall(bytes(', '.join([client_id[0] for client_id in client_information]),
                                           encoding='UTF-8'))


# TODO: modify this so it does everything it needs to do
# for now, it echoes
def client_connection(clientconn, address):  # for just one client
    global client_information
    # Michal's send and receive data function as a placeholder
    print("Connected by: ", address)
    data = clientconn.recv(1024)
    data_in_json = json.loads(data.decode('utf-8').replace("'", '"'))
    client_id, name, public_key = data_in_json[0]['id'], data_in_json[0]['name'], data_in_json[0]['public_key']
    register(client_id, name, public_key)
    current_client = [client_id, name, public_key, clientconn]
    client_information.append(current_client)
    clientconn.sendall(b'Connected successfully!')
    while threading.currentThread().is_alive():
        while True:
            data = clientconn.recv(1024)
            if data.decode("utf-8").startswith("MSG"):
                data = data.decode("utf-8").split(" ", maxsplit=2)
                send_message(client_id, data[1], data[2])
            elif data.decode("utf-8") == "ONLINE":
                show_whois_online(client_id)
    client_information = [conn_client for conn_client in client_information if conn_client[0] != client_id]
    clientconn.close()


# TODO: send message functions need to be implemented
def send_message(sender_id, receiver_id, plaintext_message):
    for single_client in client_information:
        if single_client[0] == receiver_id:
            message = plaintext_message
            # message = encrypt_message(single_client[0], plaintext_message)
            single_client[3].sendall(b'Message from'+bytes(sender_id, encoding='utf8')+b': '+bytes(message, encoding='utf8'))
    return


def encrypt_message(public_key, message):
    return rsa.encrypt(bytes(message, encoding='utf-8'), public_key)


# def send_message(first_name, last_name, encrypted_message):
#    pass


# this is an attempt at some functions
# TODO: check everything and add remaining functions, test functionality

HOST = '127.0.0.1'
PORT = 13370
client_information = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# infinite loop, creates different thread for every client
while True:
    client, address = server.accept()
    client_thread = threading.Thread(args=(client, address), target=client_connection)
    client_thread.start()  # to be able to handle multiple clients
    # print("New thread started.")

# Michal's one :D
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#    s.bind((HOST, PORT))
#    s.listen()
#    connection, address = s.accept()
#    with connection:
#        print("Connected by: ", address)
#        while True:
#            data = connection.recv(1024)
#            if not data:
#                break
#            connection.sendall(data)
