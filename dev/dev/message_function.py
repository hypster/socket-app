"""
@author: yiping
"""
import json
import rsa
BUFLEN = 1024


def format_message(msg):
    """format message with custom protocal

    :param msg: send data in json format
    :return: message with header and body
    """
    body = msg.encode('utf-8')
    body_len = len(body)
    header = int.to_bytes(body_len, 4, byteorder='big')  # header is 4 byte long
    return header + body

def get_response(socket):
    """return body in the parsed res
    :param socket: data socket
    :return: body in the parsed res
    """
    header = socket.recv(4)
    if not header:
        return None

    body_length = int.from_bytes(header, byteorder='big')
    body = socket.recv(body_length)

    while len(body) < body_length:
        body += socket.recv(body_length - len(body))
    return json.loads(body.decode('utf-8'))





if __name__ == '__main__':
    b_str = format_message(json.dumps({'type': 'register'}))