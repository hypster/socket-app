"""
@author: yiping
"""
import json
import struct
BUFLEN = 1024



def format_message(body):
    """format message with custom protocal

    :param msg: byte string
    :return: bytestring with header and body
    """
    body_len = len(body)

    header = struct.pack('!L', body_len)
    # header = int.to_bytes(body_len, 4, byteorder='big')  # header is 4 byte long
    return header + body

def parse_message(bytes):
    str = bytes.decode('utf-8')
    return json.loads(str)

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