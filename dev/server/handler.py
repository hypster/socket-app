from server.server_global import *
import MessageType
from datetime import datetime
from server import Role

def handle_retrieve_public_key(req, sess):
    print('in handle retrieve')
    _id = None
    if 'id' in req:
        _id = req['id']

        if _id in users:
            public_key = users[_id]['public']
            firstname = users[_id]['firstname']
            lastname = users[_id]['lastname']
            obj = {'status': 1, 'type': MessageType.PUB_KEY, 'public': public_key, 'id': _id, 'firstname': firstname, 'lastname': lastname,
                   'text': 'public key retrieved'}
        else:
            obj = {'status': 0, 'type': MessageType.PUB_KEY, 'text': f'{_id} is not registered'}

    elif 'firstname' in req and 'lastname' in req:
        firstname = req['firstname'].lower()
        lastname = req['lastname'].lower()
        name = (firstname, lastname)
        obj = {'users': []}
        if name in name2id:
            ids = name2id[name]
            for _id in ids:
                user = users[_id]
                firstname = user['firstname']
                lastname = user['lastname']
                public = user['public']
                obj['users'].append({'firstname': firstname, 'lastname':lastname,'public': public, 'id': _id})
            obj['status'] = 1
            obj['text'] = 'public key retrieved'
            obj['type'] = MessageType.PUB_KEY
        else:
            obj = {'status': 0, 'type':MessageType.PUB_KEY, 'text': f'{name} is not registered'}

    print(f"retrieve: {obj}")
    sess.send(obj)



def handle_start(req, sess):
    print('in handle start')
    type = req['type']
    if type == MessageType.Request.REGISTER:
        handle_register(req,sess)
    elif type == MessageType.Request.MES:
        handle_send(req,sess)
    elif type == MessageType.Request.RET_PUB_KEY:
        handle_retrieve_public_key(req, sess)

def handle_register(req, conn, addr, bank_info):

    try:
        _id = req['id']
        # print("id :" + _id)
        if _id in users:
            return {'status': 1, 'text': 'you registered already'}
        firstname = req['firstname'].lower()
        lastname = req['lastname'].lower()
        pk = req['public']
        # save in users table
        users[_id] = {'firstname': firstname, 'lastname': lastname, 'id': _id, 'public': pk}
        if _id == bank_info['id']:
            users[_id]['roles'] = [Role.BANK, Role.NORMAL]
        else:
            users[_id]['roles'] = [Role.NORMAL]
        # save name-id mapping
        if (firstname, lastname) in name2id:
            name2id[(firstname, lastname)].append(_id)
        else:
            name2id[(firstname, lastname)] = [_id]

        # save login status in connections
        # connections[addr] = id
        return {'status': 1, 'text': 'register ok'}
    except (KeyError, AttributeError):
        return {'status': 0, 'text': 'please pass id, firstname, lastname and public key'}


def handle_send(req,sess):
    # try:
        if 'id' in req: # addressed with id
            ids = [req['id']]
        else: # addressed with name
            firstname = req['firstname'].lower()
            lastname = req['lastname'].lower()
            ids = name2id[(firstname, lastname)]
        # print("id:" + str(id))
        id_online = []
        id_offline = []
        for i in ids:
            if i in id2session:  # if user is online
                id_online.append(i)
            else:
                id_offline.append(i)
        if len(id_offline):  # some users are not online
            sess.send({'status': 0, 'type': MessageType.ACK_MSG, 'text': 'user(s) are not online', 'message_id': req['message_id'], 'ids': id_offline})
        if len(id_online): # some users are online
            msg = {}
            time = datetime.now().timestamp() #timestamp to add
            msg = create_ack_message(req, sess)
            msg['timestamp'] = time
            sess.send(msg) #send timestamped message back to sender

            for i in id_online:  # send message to every receiver
                other_sess = id2session[i]
                msg = create_send_message(req,sess)
                msg['id'] = i
                msg['firstname'] = users[i]['firstname']
                msg['lastname'] = users[i]['lastname']
                msg['timestamp'] = time
                print('resending msg to other user')

                other_sess.send(msg) #send to receiver

    # except (KeyError, AttributeError):
    #     return sess.send({'status': 0, 'type': MessageType.ACK, 'text': 'please pass id/firstname, lastname and your message'})


def create_send_message(req, sess):
    msg = {'status': 1, 'type': MessageType.USER_MSG, 'message': req['message']}
    if 'message_type' in req:
        msg['message_type'] = req['message_type']
    user = {}
    user['id'] = sess.user['id']
    user['firstname'] = sess.user['firstname']
    user['lastname'] = sess.user['lastname']
    msg['source'] = user
    return msg

def create_ack_message(req, sess):
    msg = {'status': 1, 'type': MessageType.ACK_MSG, 'text': 'Message sent','message_id': req['message_id']}
    return msg

def handle_transfer_message(req, sess):
    pass

def handle_withdraw_message(req, sess):
    pass
