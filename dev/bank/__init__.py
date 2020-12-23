from client import Client
import json
from client.parser import *
from bank.parser import *
import MessageType
from bank.business.handler import _handle_substract, _handle_transfer
import log_config
from bank.business import Directive
import logging
import tkinter

class Bank(Client):
    def __init__(self, config_file='', log_file=''):
        log_config.config(log_file)
        self.conn = None
        self.connect_db(config_file)
        if self.conn:
            super().__init__(config_file, log_file)
        else:
            logging.debug('connection to db failed')
            exit(1)


    def connect_db(self, config_file):
        logging.debug(' connecting to db...')
        conn = self.read_info(config_file)['accounts']
        if conn:
            self.conn = conn
            logging.debug('connected to db')


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
        if is_normal_message(req['message']):
            return
        if is_valid_directive(req['message']):
            command = parse_directive(req['message'])
            if command:
                if command['action'].lower() == Directive.ADD:
                    self.handle_transfer(req, command, self.conn)
                elif command['action'].lower() == Directive.SUB:
                    self.handle_substract(req, command, self.conn)
            else:
                self.start_send({'type': MessageType.Request.MES, 'status': 0, 'id': req['source']['id'],
                                 'message': 'Parse directive failed. Please check your input'})
        else:
            self.start_send({'type': MessageType.Request.MES, 'status': 0, 'id': req['source']['id'],
                             'message': 'Directive is not unsupported'})
