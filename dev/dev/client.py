"""
@author: yiping
"""
import socket
import json
from message_function import get_response, format_message
from threading import Thread
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
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.info = self.read_info(config_file)
        server = self.info['server']
        self.start(server['ip'], int(server['port']))

    def start(self, host, port):
        self.data_socket.connect((host, port))
        print(f"connected to {host, port}")

    def read_info(self, config_file):
        with open(config_file, 'rb') as f:
            return json.loads(f.read())

    def register(self):
        s = self.data_socket
        person = self.info['person']
        id = person['id']
        name = person['name']
        [firstname, lastname] = name.split(',')
        firstname = firstname.strip()
        lastname = lastname.strip()
        public = person['keys']['public']
        body = {'type':'register', 'id': id, 'firstname': firstname, 'lastname': lastname, 'public': public}
        msg = format_message(json.dumps(body))
        s.send(msg)
        res = get_response(s)
        print(res)
        return res

    def do_actions(self):
        s = self.data_socket
        for action in self.info['actions']:
            msg = parse_action(action)
            msg = format_message(msg)
            s.send(msg)
            # res = get_response(s)
            # print(res)
            # return res

    def close(self):
        self.data_socket.close()


def automate(config):
    c = Client(config)
    c.register()
    c.do_actions()


if __name__ == '__main__':
    for i in range(2):
        th = Thread(target=automate, args=(f'./config_{i+1}.json',)) #create a thread for processing dialog
        th.start()



    # c1 = Client(config_file='./config_1.json')
    # c2 = Client(config_file='./config_2.json')
    # c1.register()
    # c2.register()
    # c1.do_actions()
    # # c1.close()
    # # c2.close()
