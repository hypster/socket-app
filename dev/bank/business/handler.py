from bank.business.db import *


def _handle_substract(user_id, fromAcc, amount, conn):
    if check_acc_exists(fromAcc, conn):
        if check_permission(user_id, fromAcc, conn):
            if not check_enough_balance(fromAcc, amount, conn):
                return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id, 'message': 'you don\'t have enough balance'}
            else:
                if substract(fromAcc, amount, conn):
                    return {'type': MessageType.Request.MES, 'status': 1, 'id': user_id, \
                            'message': f'you withdrew {amount} from account {fromAcc}, your balance is now: {get_balance(fromAcc, conn)}'}
                else:
                    return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id, \
                            'message': f'your action failed. Please try again.'}

        else:
            return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id, 'message': 'you don\'t have permission'}
    else:
        return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id, 'message': 'account does not exist'}


def _handle_transfer(user_id, fromAcc, toAcc, amount, conn):
    if check_acc_exists(fromAcc, conn) and check_acc_exists(toAcc, conn):  # both accounts exist
        if check_permission(user_id, fromAcc, conn):
            if check_enough_balance(fromAcc, amount, conn):
                if substract(fromAcc, amount, conn) and add(toAcc, amount, conn):
                    other_id = get_user_id(toAcc, conn)
                    return [{'type': MessageType.Request.MES, 'status': 1, 'id': user_id,
                            'message': f'transaction success, you transferred {amount} to account {toAcc}, \ '
                                       f'your balance in account {fromAcc} is now: {get_balance(fromAcc, conn)}'},
                            {
                                'type': MessageType.Request.MES, 'status':1, 'id': other_id,
                                'message': f'account {fromAcc} transferred {amount} to your account {toAcc}. Your balance is now: {get_balance(toAcc, conn)}'
                            }]
                else:
                    return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id,
                            'message': 'your action failed. Please try again.'}
            else:
                return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id, 'message': 'you don\'t have enough balance'}
        else:
            return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id, 'message': 'you don\'t have permission.'}
    else:
        return {'type': MessageType.Request.MES, 'status': 0, 'id': user_id, 'message': 'account doesn\'t exist.'}