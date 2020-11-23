import re
import socket
import threading

HOST = '127.0.0.1'
PORT = 13370

client_information = []
id_connections = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Server up and running!")


def registration(id, first_name, last_name, public_key):
    info = {'id': id, 'first_name': first_name, 'last_name': last_name, 'public_key': public_key}
    client_information.append(info)
    print(info)
    return info


def retrieve_public_key_id(id):
    for current_client in client_information:
        if id == current_client['id']:
            return current_client['public_key']
    return None


def retrieve_public_key_name(first_name, last_name):
    same_name_client = {}
    client_exists = False
    for current_client in client_information:
        if first_name == current_client['first_name'] and last_name == current_client['last_name']:
            same_name_client[current_client['id']] = current_client['public_key']
            client_exists = True
    if client_exists:
        return same_name_client
    else:
        return None


def send_message(id, encrypted_message, sender_id):
    message_sent = False
    for current_client in id_connections:
        if current_client[0] == id:
            id_connections[1].sendall('INCOMING MESSAGE FROM [' + str(sender_id) + ']').encode('utf-8')
            current_client[1].sendall(encrypted_message)
            message_sent = True
    print("Message from " + sender_id + " sent!")
    return message_sent


def send_message(first_name, last_name, encrypted_message, sender_id):
    id_list = []
    message_sent = False
    for current_client in client_information:
        if first_name == current_client['first_name'] and last_name == current_client['last_name']:
            id_list.append(current_client['id'])

    # send to everyone with this name
    for client_id in id_list:
        for current_client in id_connections:
            if current_client[0] == client_id:
                id_connections[1].sendall('INCOMING MESSAGE FROM [' + str(sender_id) + ']').encode('utf-8')
                id_connections[1].sendall(encrypted_message)
                message_sent = True
                break

    print("Message from " + sender_id + " sent!")

    return message_sent


def client_connection(clientconn, address):  # for just one client
    print("Connected by: ", address)
    registered = False

    while True:
        message_from_client = str(clientconn.recv(1024).decode('utf-8'))
        # put everything between brackets in a list
        list_info = re.findall(r"[^[]*\[([^]]*)\]", message_from_client)
        id = '' # to keep track of who this is

        # firstly: register
        if message_from_client.lower().startswith('register'):
            for person in client_information:
                if person['id'] == list_info[0]:
                    registered = True
                    id = list_info[0]
                    encoded_message = "Error: was already registered".encode('utf-8')
                    clientconn.sendall()

            if not registered:
                registration(id=list_info[0], first_name=list_info[1].lower(), last_name=list_info[2].lower(),
                             public_key=list_info[3])
                clientconn.sendall("Registered correctly!".encode('utf-8'))
                registered = True
                id = list_info[0]

        if registered:
            if message_from_client.lower().startswith('receive_key_id'):
                print("Receiving key id")
                key = retrieve_public_key_id(list_info[0])
                if key is not None:
                    key_string = 'KEY [' + str(key) + ']'
                    clientconn.sendall(key_string.encode('utf-8'))
                else:
                    clientconn.sendall("Error: recipient is not found")

            # first test the one with id
            #if message_from_client.lower().startswith('receive_key_name'):
                #print("Receiving key name")
                #key_list = retrieve_public_key_name(first_name=list_info[0].lower(), last_name=list_info[1].lower())
                #if key_list is not None:
                    #key_list_string = 'KEY'
                    #for i in key_list:
                        #key_list_string = key_list_string + ' [' + str(i) + ']'
                    #clientconn.sendall(key_list_string.encode('utf-8'))
                #else:
                    #clientconn.sendall("Error: recipient is not found")

            if message_from_client.lower().startswith('send'):
                print("Sending message")
                possible_name_parts = list_info[0].split(', ')
                id = False

                if len(possible_name_parts) == 2:
                    last_name = possible_name_parts[0].lower()
                    first_name = possible_name_parts[1].lower()
                else:
                    id = True
                    id_cl = list_info[0]

                if id:
                    sent = send_message(id_cl, list_info[1], id)
                else:
                    sent = send_message(first_name, last_name, list_info[1], id)

                if sent:
                    clientconn.sendall("Message sent!")
                else:
                    clientconn.sendall("Error: message not sent!")

        else:
            clientconn.sendall("Error: Not registered yet!".encode('utf-8'))

    clientconn.close()


# infinite loop, creates different thread for every client
while True:
    client, address = server.accept()
    client_thread = threading.Thread(args=(client, address), target=client_connection)
    client_thread.start()
