from bank.business.db import *
import logging

def _handle_substract(user_id, fromAcc, amount, conn):
    if check_acc_exists(fromAcc, conn):
        if check_permission(user_id, fromAcc, conn):
            if amount < 0:
                return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id, 'message': 'Amount must be positive value'}
            if not check_enough_balance(fromAcc, amount, conn):
                return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id, 'message': 'You don\'t have enough balance'}
            if substract(fromAcc, amount, conn):
                logging.info(f'Account {fromAcc} withdrew {amount}')
                return {'type': MessageType.Request.MES, 'status': 1, 'id': user_id, \
                        'message': f'You withdrew {amount} from account {fromAcc}, your balance is now: {get_balance(fromAcc, conn)}'}
            else:
                return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id, \
                        'message': f'Your action failed. Please try again.'}
        else:
            return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id, 'message': 'You don\'t have permission'}
    else:
        return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id, 'message': 'Account does not exist'}


def _handle_transfer(user_id, fromAcc, toAcc, amount, conn):
    if not(check_acc_exists(fromAcc, conn) and check_acc_exists(toAcc, conn)):  # both accounts exist
        return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id, 'message': 'Account doesn\'t exist.'}
    if not check_permission(user_id, fromAcc, conn):
        return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id,
                'message': 'You don\'t have enough balance'}
    if amount < 0:
        return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id,
                'message': 'Amount must be positive'}
    if not check_enough_balance(fromAcc, amount, conn):
        return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id, 'message': 'You don\'t have permission.'}

    if substract(fromAcc, amount, conn) and add(toAcc, amount, conn):
        logging.info(f"Account {fromAcc} transferred {amount} to account {toAcc}")
        other_id = get_user_id(toAcc, conn)
        return [{'type': MessageType.Request.MES, 'status': 1, 'id': user_id,
                'message': f'Transaction success, you transferred {amount} to account {toAcc}, \ '
                           f'your balance in account {fromAcc} is now: {get_balance(fromAcc, conn)}'},
                {
                    'type': MessageType.Request.MES, 'status':1, 'id': other_id,
                    'message': f'Account {fromAcc} transferred {amount} to your account {toAcc}. Your balance is now: {get_balance(toAcc, conn)}'
                }]
    else:
        return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id,
                'message': 'Your action failed. Please try again.'}



