import socket
import json

with open("json_files/config_1.json") as json_file:
    json_data = json.load(json_file)
    HOST = json_data['server']['ip']
    PORT = int(json_data['server']['port'])

public_json_data = json.dumps([{'id': json_data['person']['id'], 'name': json_data['person']['name'],
                                'public_key': json_data['person']['keys']['public']}])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(bytes(public_json_data, encoding='UTF-8'))
    while True:
        data = s.recv(1024)
        print('Received', repr(data))
