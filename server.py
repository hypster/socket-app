import codecs
import socket
import threading
import base64
import json
from multipledispatch import dispatch


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
        print(new_user[0]['id'])
        for user in data['users']:
            if user['id'] == new_user[0]['id']:
                return
        data['users'] += new_user
        users_file.seek(0)
        json.dump(data, users_file, indent=4)
        users_file.truncate()
        return
    # current_client = [id, name, public_key]
    # client_information.append(current_client)


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
        return


# return public key of someone
def retrieve_public_key(id):
    for i in client_information:
        if i.index(0) == id:
            return i.index(3)


# return dictionary of all public keys of people with the same name (and their ids to identify them)
# as everyone with the same name should get a message if this is sent to them
def retrieve_public_key(first_name, last_name):
    clients_with_this_name = {}
    for i in client_information:
        if i.index(1) == first_name and i.index(2) == last_name:
            clients_with_this_name[i.index(0)] = i.index(3)
            # key is the id!
    return clients_with_this_name


# TODO: modify this so it does everything it needs to do
# for now, it echoes
def client_connection(clientconn, address):  # for just one client
    # Michal's send and receive data function as a placeholder
    print("Connected by: ", address)
    while True:
        data = clientconn.recv(1024)
        data_in_json = json.loads(data.decode('utf8').replace("'", '"'))
        register(data_in_json)
        if not data:
            break
        clientconn.sendall(data)

    clientconn.close()


# TODO: send message functions need to be implemented
def send_message(id, encrypted_message):
    for single_client in client_information:
        if single_client.index(0) == id:
            pass
    pass


def send_message(first_name, last_name, encrypted_message):
    pass


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
