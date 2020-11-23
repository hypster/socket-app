"""
@author: yiping
"""
import socket
from threading import Thread
import json
from message_function import get_response, format_message
# from handlers import client_handlier
BUFLEN = 1024

users = {} #stores all user information here, id -> info
name2id = {} #(firstname,lastname) -> user id
connections = {} #id -> socket

def client_handlier(conn, addr):
    while True:
        msg = get_response(conn)
        if not msg: #if client closed connection
            print(f'client {addr} closes the connection' )
            break

        print(f'receive info from {addr}：\n \t\t\ {msg}')
        res = handle_start(msg, conn)
        send_msg = json.dumps(res)
        conn.send(format_message(send_msg))
    conn.close()

def handle_start(res, conn):
    type = res['type']
    if type == 'register':
        return handle_register(res, conn)
    elif type == 'send':
        return handle_send(res)

def handle_register(res, conn):
    try:
        id = res['id']
        if id in users:
            return {'status': 1, 'text': 'you registered already'}
        firstname = res['firstname'].lower()
        lastname = res['lastname'].lower()
        pk = res['public']
        users[id] = {'firstname': firstname, 'lastname':lastname, 'id':id, 'public': pk}
        connections[id] = conn
        if (firstname, lastname) in name2id:
            name2id[(firstname, lastname)].append(id)
        else:
            name2id[(firstname, lastname)] = [id]
        return {'status': 1, 'text': 'register ok'}
    except (KeyError,AttributeError):
        return {'status': 0, 'text': 'please pass id, firstname, lastname and public key'}

def handle_send(res):
    try:
        print('send msg:' + str(res))
        msg = res['message']
        if 'id' in res:
            id = [res['id']]
        else:
            firstname = res['firstname'].lower()
            lastname = res['lastname'].lower()
            id = name2id[(firstname, lastname)]
        print("id:" + str(id))
        for i in id:
            conn = connections[i]
            conn.send(format_message(msg))
            #TODO: send ack message to sender

    except (KeyError, AttributeError):
        return {'status': 0, 'text': 'please pass id/firstname, lastname and your message'}


def handle_retrieve_public_key(res):
    pass



SERVER_HOST = '127.0.0.1'
SERVER_PORT = 52800

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.bind((SERVER_HOST, SERVER_PORT))
listen_socket.listen(5) #maximum number of people
while True:
    data_socket, addr = listen_socket.accept()
    print(f'client {str(addr)} connected')
    th = Thread(target=client_handlier, args=(data_socket, addr)) #create a thread for processing dialog
    th.start()

listen_socket.close()
