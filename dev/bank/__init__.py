from client import Client
import json
from client.parser import *
from bank.parser import *
import MessageType
from bank.business.handler import _handle_substract, _handle_transfer


class Bank(Client):
    def __init__(self, config_file=''):
        self.conn = None
        self.connect_db(config_file)
        if self.conn:
            super().__init__(config_file)
        else:
            print('connection to db failed')
            exit(1)


    def connect_db(self, config_file):
        print(' connecting to db')
        conn = self.read_info(config_file)['accounts']
        if conn:
            self.conn = conn


    def handle_substract(self, req, command, conn):
        user_id = req['source']['id']
        fromAcc = command['fromAcc']
        amount = command['amount']
        msg = _handle_substract(user_id, fromAcc, amount, conn)
        self.start_send(msg)

    def handle_transfer(self, req, command, conn):
        user_id = req['source']['id']
        fromAcc = command['fromAcc']
        toAcc = command['toAcc']
        amount = command['amount']
        msg = _handle_transfer(user_id, fromAcc, toAcc,amount, conn)
        if isinstance(msg, list): # success, inform both parties
            for m in msg:
                self.start_send(m)
        elif msg:
            self.start_send(msg)

    # override
    def handle_user_message(self, req):
        super().handle_user_message(req)
        if check_directive_format(req['message']):
            print('message is for transaction')
            command = parse_directive(req['message'])
            print(command)
            if command is None:
                return
            if command['action'] == 'add':
                self.handle_transfer(req, command, self.conn)
            elif command['action'] == 'sub':
                self.handle_substract(req, command, self.conn)
        else:
            print('normal message or unsupported transaction')

